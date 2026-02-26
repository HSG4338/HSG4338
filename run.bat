@echo off
chcp 65001 >nul 2>&1
title Agentic AI System

:: ── ANSI colour codes for bat-level messages only ──────────────────────────────
set "ESC="
for /f %%a in ('echo prompt $E^| cmd /q') do set "ESC=%%a"
set "R=%ESC%[0m"
set "BOLD=%ESC%[1m"
set "GREY=%ESC%[90m"
set "MAGENTA=%ESC%[95m"
set "CYAN=%ESC%[96m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "WHITE=%ESC%[97m"
set "DIM=%ESC%[2m"

cls

:: ── Find Python ─────────────────────────────────────────────────────────────────
set PYEXE=
where python >nul 2>&1
if %ERRORLEVEL%==0 set PYEXE=python
if "%PYEXE%"=="" (
    where python3 >nul 2>&1
    if %ERRORLEVEL%==0 set PYEXE=python3
)
if "%PYEXE%"=="" (
    echo.
    echo  %RED%[ERROR]%R%  Python not found on PATH.
    echo.
    echo           Install Python 3.9+ from %CYAN%https://python.org%R%
    echo           Tick %WHITE%"Add Python to PATH"%R% during install.
    echo.
    pause & exit /b 1
)

:: ── Create venv if missing ───────────────────────────────────────────────────────
if not exist "venv\Scripts\python.exe" (
    echo.
    echo  %CYAN%[SETUP]%R%  Creating virtual environment...
    %PYEXE% -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo  %RED%[ERROR]%R%  venv creation failed.
        pause & exit /b 1
    )
    echo  %GREEN%[OK]%R%     Virtual environment created.
    echo.
)
set VP=venv\Scripts\python.exe

:: ── Install dependencies if flask is missing ────────────────────────────────────
%VP% -c "import flask" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo  %YELLOW%[SETUP]%R%  Installing dependencies %GREY%(first run only, please wait)%R%...
    echo.
    %VP% -m pip install --upgrade pip --quiet
    %VP% -m pip install flask transformers accelerate huggingface_hub requests gitpython psutil tqdm protobuf --quiet
    %VP% -m pip install torch --quiet
    if %ERRORLEVEL% neq 0 (
        %VP% -m pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet
    )
    %VP% -m pip install sentencepiece --only-binary :all: --quiet >nul 2>&1
    echo.
    echo  %GREEN%[OK]%R%     Dependencies installed.
    echo.
)

:: ── Hand off entirely to Python for the pretty menu ─────────────────────────────
%VP% main.py
echo.
pause
