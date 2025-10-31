@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🤖 Запуск Nicole - Полностью автономная версия
echo ================================================

:: ВСЕГДА используем portable Python если он существует
set PORTABLE_PYTHON=bin\python\windows\python.exe

if exist "!PORTABLE_PYTHON!" (
    echo ✅ Используется Portable Python 3.11
    set PYTHON_CMD=!PORTABLE_PYTHON!
) else (
    echo ❌ Portable Python не найден в bin\python\windows\
    echo Убедитесь что архив распакован полностью
    pause
    exit /b 1
)

:: Проверяем зависимости в portable Python
echo 📦 Проверка зависимостей...
!PYTHON_CMD! -c "import requests, yaml, logging" >nul 2>&1
if !errorlevel! neq 0 (
    echo ⚠️ Зависимости не установлены, устанавливаю...
    !PYTHON_CMD! -m pip install --no-index --find-links=dependencies -r requirements-offline.txt
    if !errorlevel! neq 0 (
        echo ❌ Ошибка установки зависимостей
        echo Проверьте папку dependencies/
        pause
        exit /b 1
    )
)

:: Запуск основной программы
echo 🚀 Запуск Nicole...
!PYTHON_CMD! main.py

pause
