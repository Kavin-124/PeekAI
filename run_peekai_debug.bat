@echo off
title PeekAI - Debug Console
cd /d "%~dp0"
.venv\Scripts\python.exe main.py
if errorlevel 1 (
    echo.
    echo PeekAI exited with an error.
    pause
)
