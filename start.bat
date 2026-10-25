@echo off
cd /d "%~dp0"
uv run python Daily\app.py
if errorlevel 1 pause
