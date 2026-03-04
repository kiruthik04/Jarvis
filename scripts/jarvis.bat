@echo off

if "%1"=="log" goto do_log
if "%1"=="start" goto do_start
if "%1"=="ui" goto do_ui
if "%1"=="stop" goto do_stop
if "%1"=="test" goto do_test

:do_help
echo Usage:
echo   jarvis log            - View live console logs
echo   jarvis ui             - Start the GUI Visual Interface
echo   jarvis start          - Start Jarvis silently in Headless Mode
echo   jarvis stop           - Stop all running Jarvis instances
echo   jarvis test           - Run ALL tests
echo   jarvis test --offline - Run offline tests only
echo   jarvis test --online  - Run API tests only
echo   jarvis test memory    - Run a specific test module
goto :eof

:do_log
powershell -Command "Get-Content -Wait 'D:\Projects\jarvis\data\logs\jarvis.log'"
goto :eof

:do_start
echo Starting Jarvis (Headless Mode)...
cscript //nologo "D:\Projects\jarvis\scripts\start_headless_silent.vbs"
goto :eof

:do_ui
echo Starting Jarvis UI (Visual Mode)...
cscript //nologo "D:\Projects\jarvis\scripts\start_ui_silent.vbs"
goto :eof

:do_stop
taskkill /f /im python.exe
goto :eof

:do_test
cd /d "D:\Projects\jarvis"
call venv\Scripts\activate.bat
if "%2"=="" (
    python tests\run_tests.py
) else (
    python tests\run_tests.py %2 %3 %4
)
goto :eof

