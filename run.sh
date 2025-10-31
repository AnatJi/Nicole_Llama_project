#!/bin/bash

echo "🤖 Запуск Nicole - Полностью автономная версия"
echo "================================================"

# ВСЕГДА используем portable Python если он существует
if [ -f "bin/python/linux/bin/python3" ]; then
    echo "✅ Используется Portable Python 3.11"
    PYTHON_CMD="bin/python/linux/bin/python3"
    chmod +x "$PYTHON_CMD"
elif [ -f "bin/python/mac/bin/python3" ]; then
    echo "✅ Используется Portable Python 3.11 (macOS)"
    PYTHON_CMD="bin/python/mac/bin/python3"
    chmod +x "$PYTHON_CMD"
else
    echo "❌ Portable Python не найден"
    echo "Убедитесь что архив распакован полностью"
    exit 1
fi

# Проверяем зависимости
echo "📦 Проверка зависимостей..."
"$PYTHON_CMD" -c "import requests, yaml, logging" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ Зависимости не установлены, устанавливаю..."
    "$PYTHON_CMD" -m pip install --no-index --find-links=dependencies -r requirements-offline.txt
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка установки зависимостей"
        echo "Проверьте папку dependencies/"
        exit 1
    fi
fi

# Запуск основной программы
echo "🚀 Запуск Nicole..."
"$PYTHON_CMD" main.py
