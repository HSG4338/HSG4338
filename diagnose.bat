@echo off
title Agentic AI - Diagnostics
color 07

echo ============================================
echo  AGENTIC AI SYSTEM - DIAGNOSTICS
echo ============================================
echo.
echo Running checks... (this window will stay open)
echo.

:: 1. Python
echo [1] Python version:
python --version 2>&1
if %ERRORLEVEL% neq 0 (
    echo     FAIL - Python not found! Install from https://python.org
    echo     Make sure to tick "Add Python to PATH" during install.
) else (
    echo     OK
)
echo.

:: 2. Python path
echo [2] Python location:
where python 2>&1
echo.

:: 3. Virtual environment
echo [3] Virtual environment:
if exist "venv\Scripts\python.exe" (
    echo     OK - venv found
    venv\Scripts\python.exe --version 2>&1
) else (
    echo     MISSING - run install_dependencies.bat first
)
echo.

:: 4. Key files
echo [4] Key files present:
if exist "main.py"                     (echo     OK: main.py)           else (echo     MISSING: main.py)
if exist "configs\config.json"         (echo     OK: configs\config.json) else (echo     MISSING: configs\config.json)
if exist "agents\planner_agent.py"     (echo     OK: agents\)           else (echo     MISSING: agents\)
if exist "orchestrator\orchestrator.py" (echo    OK: orchestrator\)     else (echo     MISSING: orchestrator\)
if exist "memory\memory_store.py"      (echo     OK: memory\)           else (echo     MISSING: memory\)
if exist "ui\app.py"                   (echo     OK: ui\)               else (echo     MISSING: ui\)
echo.

:: 5. Python imports
echo [5] Python module check (using venv if available):
if exist "venv\Scripts\python.exe" (
    set PYEXE=venv\Scripts\python.exe
) else (
    set PYEXE=python
)

%PYEXE% -c "import sqlite3; print('    OK: sqlite3')" 2>&1
%PYEXE% -c "import json; print('    OK: json')" 2>&1
%PYEXE% -c "import flask; print('    OK: flask')" 2>nul || echo     MISSING: flask (run install_dependencies.bat)
%PYEXE% -c "import transformers; print('    OK: transformers')" 2>nul || echo     MISSING: transformers (run install_dependencies.bat)
%PYEXE% -c "import torch; print('    OK: torch')" 2>nul || echo     MISSING: torch (run install_dependencies.bat)
echo.

:: 6. Try running main.py and capture crash
echo [6] Test run of main.py --help:
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py --help 2>&1
) else (
    python main.py --help 2>&1
)
echo.

echo ============================================
echo  Diagnostics complete.
echo  If you see MISSING above, run:
echo    install_dependencies.bat
echo ============================================
echo.
pause
