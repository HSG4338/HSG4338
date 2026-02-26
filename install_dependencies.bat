@echo off
setlocal enabledelayedexpansion
title Agentic AI System Installer
color 07

if not exist "logs" mkdir logs
set LOG_FILE=logs\install.log

echo =================================================
echo  AGENTIC AI SYSTEM - INSTALLER
echo =================================================
echo.
echo Log will be saved to: %LOG_FILE%
echo.

echo ================================================= >> %LOG_FILE%
echo Install started: %date% %time% >> %LOG_FILE%
echo ================================================= >> %LOG_FILE%

:: [1] Find Python
echo [1/5] Checking Python...
set PYEXE=
where python >nul 2>&1
if %ERRORLEVEL%==0 set PYEXE=python
if "%PYEXE%"=="" (
    where python3 >nul 2>&1
    if %ERRORLEVEL%==0 set PYEXE=python3
)
if "%PYEXE%"=="" (
    echo.
    echo [ERROR] Python not found. Install from https://python.org
    echo         Tick "Add Python to PATH" during install.
    echo.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('%PYEXE% --version 2^>^&1') do set PY_VER=%%v
echo         Found: %PY_VER%
echo %PY_VER% >> %LOG_FILE%

:: [2] Create venv
echo.
echo [2/5] Setting up virtual environment...
if not exist "venv\Scripts\python.exe" (
    %PYEXE% -m venv venv >> %LOG_FILE% 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] venv creation failed. Check %LOG_FILE%
        pause & exit /b 1
    )
    echo         Created new venv.
) else (
    echo         Already exists.
)
set VP=venv\Scripts\python.exe

:: [3] Upgrade pip
echo.
echo [3/5] Upgrading pip...
%VP% -m pip install --upgrade pip --quiet >> %LOG_FILE% 2>&1
echo         Done.

:: [4] Install packages one by one
echo.
echo [4/5] Installing packages...
echo       (Installing one by one so a single failure does not block others)
echo.

set FAILS=

call :pkg flask
call :pkg requests
call :pkg gitpython
call :pkg psutil
call :pkg tqdm
call :pkg protobuf
call :pkg huggingface_hub
call :pkg transformers
call :pkg accelerate

:: torch needs special handling - no pinned version
echo         torch (large download, please wait)...
%VP% -m pip install torch --quiet >> %LOG_FILE% 2>&1
if %ERRORLEVEL% neq 0 (
    echo         torch failed on default index. Trying PyTorch CPU index...
    %VP% -m pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet >> %LOG_FILE% 2>&1
    if %ERRORLEVEL% neq 0 (
        echo         [WARN] torch failed both ways. Will retry at runtime.
        set FAILS=%FAILS% torch
    ) else (
        echo         torch installed (CPU).
    )
) else (
    echo         torch installed.
)

:: sentencepiece - binary only, skip gracefully if unavailable for this Python version
echo         sentencepiece (optional, binary only)...
%VP% -m pip install sentencepiece --only-binary :all: --quiet >> %LOG_FILE% 2>&1
if %ERRORLEVEL% neq 0 (
    echo         sentencepiece skipped (no prebuilt wheel for Python 3.14 yet, not required).
) else (
    echo         sentencepiece installed.
)

:: [5] Summary
echo.
echo [5/5] Done.
echo Install finished: %date% %time% >> %LOG_FILE%

if not "%FAILS%"=="" (
    echo.
    echo [WARN] These packages had issues: %FAILS%
    echo        Try running run.bat anyway - it may still work.
) else (
    echo         All packages installed OK.
)

echo.
echo =====================================================
echo  DONE. Now double-click run.bat to launch the system.
echo =====================================================
echo.
pause
exit /b 0

:pkg
echo         %~1...
%VP% -m pip install %~1 --quiet >> %LOG_FILE% 2>&1
if %ERRORLEVEL% neq 0 (
    echo         [WARN] %~1 failed.
    set FAILS=%FAILS% %~1
    echo FAILED: %~1 >> %LOG_FILE%
) else (
    echo %~1 OK >> %LOG_FILE%
)
exit /b 0
