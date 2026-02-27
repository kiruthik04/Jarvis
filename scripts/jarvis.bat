@echo off
if "%1"=="log" (
    powershell -Command "Get-Content -Wait 'D:\Projects\jarvis\data\logs\jarvis.log'"
) else if "%1"=="start" (
    cscript //nologo "D:\Projects\jarvis\scripts\start_headless_silent.vbs"
) else if "%1"=="stop" (
    taskkill /f /im python.exe
) else if "%1"=="test" (
    cd /d "D:\Projects\jarvis"
    call venv\Scripts\activate.bat
    if "%2"=="" (
        python tests\run_tests.py
    ) else (
        python tests\run_tests.py %2 %3 %4
    )
) else (
    echo Usage:
    echo   jarvis log            - View live console logs
    echo   jarvis start          - Start Jarvis silently
    echo   jarvis stop           - Stop Jarvis
    echo   jarvis test           - Run ALL tests
    echo   jarvis test --offline - Run offline tests only
    echo   jarvis test --online  - Run API tests only
    echo   jarvis test memory    - Run a specific test module
)
