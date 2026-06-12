@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  echo Missing virtual environment: .venv
  echo Create it first:
  echo   python -m venv .venv
  echo   .venv\Scripts\python -m pip install -r requirements.txt
  pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"
python main.py %*

echo.
pause
