@echo off
cd /d "D:\Projects\jarvis"
call venv\Scripts\activate.bat
python -u -m jarvis.main_headless >> "D:\Projects\jarvis\data\logs\jarvis.log" 2>&1
