@echo off
cd /d "%~dp0"

if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo.
    echo  A new .env file was created.
    echo  Open it, paste your token from @BotFather, save, then run this again.
    echo.
    pause
    exit /b
)

if not exist ".venv\Scripts\python.exe" (
    echo Setting up for the first time, please wait...
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
)

".venv\Scripts\python.exe" bot.py
pause
