@echo off
title AI RPG Arena
color 0A
echo ========================================
echo         AI RPG ARENA - LAUNCHER
echo ========================================
echo.
echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from python.org
    pause
    exit /b
)
echo [OK] Python found
echo.
echo [2/3] Installing dependencies...
pip install -q stable-baselines3 gymnasium pygame numpy matplotlib
echo [OK] Dependencies ready
echo.
echo [3/3] Starting AI RPG Arena...
echo.
python step3_gui.py
pause