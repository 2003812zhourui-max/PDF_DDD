@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\scripts\run_custom_window_prompt.ps1"
