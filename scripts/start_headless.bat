@echo off
cd /d "D:\Projects\jarvis"
call venv\Scripts\activate.bat
python -u main_headless.py >> "D:\Projects\jarvis\data\logs\jarvis.log" 2>&1
