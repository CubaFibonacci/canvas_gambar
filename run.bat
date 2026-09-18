@echo off
title GestureCanvas Launcher
echo ========================================================
echo               GestureCanvas AI Air Canvas               
echo ========================================================
echo.

set "PY_EXEC="

if exist "C:\Users\razor\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    set "PY_EXEC=C:\Users\razor\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PY_EXEC=python"
    ) else (
        where py >nul 2>nul
        if %ERRORLEVEL% equ 0 (
            set "PY_EXEC=py"
        )
    )
)

if "%PY_EXEC%"=="" (
    echo [ERROR] Python tidak ditemukan di sistem!
    echo Silakan install Python 3.10 - 3.12 dari https://python.org
    pause
    exit /b 1
)

echo Menggunakan Python: %PY_EXEC%
echo Menjalankan GestureCanvas...
echo.

"%PY_EXEC%" main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [Program selesai atau mengalami error.]
    pause
)
