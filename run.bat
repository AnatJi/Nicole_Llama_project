@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🤖 Запуск системы Kyara...

:: Check if we're in the right directory
if not exist "main.py" (
    echo ❌ Ошибка: Запускайте скрипт из корневой директории проекта
    pause
    exit /b 1
)

:: Function to check Python
set PYTHON_PATH=
if exist "venv\Scripts\python.exe" (
    set PYTHON_PATH=venv\Scripts\python.exe
    echo ✅ Локальный Python найден
) else if exist "python\local\python.exe" (
    set PYTHON_PATH=python\local\python.exe
    echo ✅ Установленный Python найден
)

:: Check dependencies
if defined PYTHON_PATH (
    %PYTHON_PATH% -c "import requests, yaml, json, os" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Зависимости установлены
    ) else (
        goto :install
    )
) else (
    goto :install
)

:: Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Ollama запущен
    echo 🚀 Запуск main.py...
    %PYTHON_PATH% main.py
    goto :end
) else (
    echo ⚠️ Ollama не запущен
    goto :install
)

:install
echo 🔧 Запуск установщика...
if defined PYTHON_PATH (
    %PYTHON_PATH% install.py
) else (
    :: Try to find system Python
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        python install.py
    ) else (
        echo ❌ Python не найден. Запустите установку вручную:
        echo python install.py
        pause
    )
)

:end
pause
