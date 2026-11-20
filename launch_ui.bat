@echo off
REM InvoiceFlow AI One-Click Windows Launcher
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scripts\run_app.py %*
) else (
    python scripts\run_app.py %*
)
pause
