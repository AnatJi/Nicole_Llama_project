#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Запуск системы Kyara...${NC}"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Ошибка: Запускайте скрипт из корневой директории проекта${NC}"
    exit 1
fi

# Function to find Python executable
find_python() {
    local python_paths=(
        "python/local/bin/python3"
        "python/local/bin/python"
        "venv/bin/python"
        "venv/bin/python3"
    )
    
    for path in "${python_paths[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    return 1
}

# Function to check if Python is available
check_python() {
    if find_python > /dev/null; then
        local python_exec=$(find_python)
        echo -e "${GREEN}✅ Локальный Python найден: $python_exec${NC}"
        return 0
    else
        echo -e "${RED}❌ Python не найден${NC}"
        return 1
    fi
}

# Function to check if dependencies are installed
check_dependencies() {
    local python_exec=$(find_python)
    if [ -n "$python_exec" ]; then
        if $python_exec -c "import requests, yaml, json, os" 2>/dev/null; then
            echo -e "${GREEN}✅ Зависимости установлены${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️ Зависимости не установлены${NC}"
            # Покажем детальную информацию о проблемах
            echo -e "${BLUE}🔍 Детальная проверка зависимостей:${NC}"
            $python_exec -c "
try:
    import requests
    print('✅ requests')
except ImportError as e:
    print('❌ requests:', e)
try:
    import yaml
    print('✅ yaml') 
except ImportError as e:
    print('❌ yaml:', e)
try:
    import json
    print('✅ json')
except ImportError as e:
    print('❌ json:', e)
" 2>/dev/null || true
            return 1
        fi
    else
        return 1
    fi
}

# Function to check Ollama with better diagnostics
check_ollama() {
    echo -e "${BLUE}🔍 Проверка Ollama...${NC}"
    
    # Check if process is running
    if pgrep -f "ollama" > /dev/null 2>/dev/null; then
        echo -e "${GREEN}✅ Ollama процесс запущен${NC}"
    else
        echo -e "${YELLOW}⚠️ Ollama процесс не запущен${NC}"
        return 1
    fi
    
    # Check API response
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama API доступен${NC}"
        
        # Check if our model is available
        local models_response=$(curl -s http://localhost:11434/api/tags)
        if echo "$models_response" | grep -q "nicole-kyara"; then
            echo -e "${GREEN}✅ Модель Nicole-Kyara доступна${NC}"
        else
            echo -e "${YELLOW}⚠️ Модель Nicole-Kyara не найдена${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Ollama API не отвечает${NC}"
        return 1
    fi
}

# Function to start ollama if not running
start_ollama_if_needed() {
    echo -e "${BLUE}🔧 Проверка и запуск Ollama...${NC}"
    
    # Check if ollama binary exists
    local ollama_binary=""
    if [ -f "ollama/ollama" ]; then
        ollama_binary="ollama/ollama"
    elif [ -f "ollama/bin/ollama" ]; then
        ollama_binary="ollama/bin/ollama"
    fi
    
    if [ -z "$ollama_binary" ]; then
        echo -e "${RED}❌ Бинарник Ollama не найден${NC}"
        return 1
    fi
    
    # Check if ollama is already running
    if pgrep -f "ollama" > /dev/null 2>/dev/null; then
        echo -e "${GREEN}✅ Ollama уже запущен${NC}"
        return 0
    fi
    
    # Start ollama in background
    echo -e "${YELLOW}🚀 Запуск Ollama...${NC}"
    $ollama_binary serve > ollama.log 2>&1 &
    local ollama_pid=$!
    
    # Wait for ollama to start
    echo -e "${BLUE}⏳ Ожидание запуска Ollama...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Ollama успешно запущен!${NC}"
            return 0
        fi
        echo -e "${BLUE}⏳ Попытка $i/10...${NC}"
        sleep 2
    done
    
    echo -e "${RED}❌ Не удалось запустить Ollama${NC}"
    echo -e "${YELLOW}📋 Проверьте лог: ollama.log${NC}"
    return 1
}

# Function to install dependencies in venv
install_dependencies_in_venv() {
    echo -e "${BLUE}🔧 Установка зависимостей в виртуальное окружение...${NC}"
    
    local python_exec=$(find_python)
    if [ -z "$python_exec" ]; then
        echo -e "${RED}❌ Python не найден${NC}"
        return 1
    fi
    
    # Проверяем, что это venv
    if [[ "$python_exec" != *"venv/"* ]]; then
        echo -e "${YELLOW}⚠️ Не виртуальное окружение, пропускаем${NC}"
        return 0
    fi
    
    echo -e "${BLUE}📦 Устанавливаем зависимости в $python_exec${NC}"
    
    # Устанавливаем зависимости
    if $python_exec -m pip install --no-index --find-links dependencies \
        dependencies/urllib3-2.5.0-py3-none-any.whl \
        dependencies/idna-3.11-py3-none-any.whl \
        dependencies/charset_normalizer-3.4.4-py3-none-any.whl \
        dependencies/certifi-2025.10.5-py3-none-any.whl \
        dependencies/requests-2.32.5-py3-none-any.whl \
        dependencies/pyyaml-6.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl; then
        echo -e "${GREEN}✅ Зависимости установлены в виртуальное окружение${NC}"
        return 0
    else
        echo -e "${RED}❌ Ошибка установки зависимостей${NC}"
        return 1
    fi
}

# Main execution
echo -e "${BLUE}🔍 Проверка системы...${NC}"

if check_python; then
    python_exec=$(find_python)
    echo -e "${BLUE}📝 Используется Python: $python_exec${NC}"
    
    if check_dependencies; then
        echo -e "${GREEN}✅ Python и зависимости готовы${NC}"
    else
        echo -e "${YELLOW}⚠️ Зависимости не установлены, пытаемся исправить...${NC}"
        if install_dependencies_in_venv; then
            echo -e "${GREEN}✅ Зависимости установлены${NC}"
        else
            echo -e "${YELLOW}⚠️ Не удалось установить зависимости автоматически${NC}"
        fi
    fi
    
    # Check and start Ollama if needed
    if check_ollama; then
        echo -e "${GREEN}✅ Все системы готовы${NC}"
        echo -e "${BLUE}🚀 Запуск main.py...${NC}"
        $python_exec main.py
    else
        echo -e "${YELLOW}⚠️ Проблемы с Ollama, пытаемся исправить...${NC}"
        if start_ollama_if_needed; then
            echo -e "${GREEN}✅ Ollama запущен${NC}"
            echo -e "${BLUE}🚀 Запуск main.py...${NC}"
            $python_exec main.py
        else
            echo -e "${RED}❌ Не удалось запустить Ollama${NC}"
            echo -e "${YELLOW}🔧 Запустите установку вручную: python3 install.py${NC}"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️ Требуется установка/настройка${NC}"
    echo -e "${BLUE}🔧 Запуск установщика...${NC}"
    
    # Try to use system Python for installation
    if command -v python3 &> /dev/null; then
        python3 install.py
    elif command -v python &> /dev/null; then
        python install.py
    else
        echo -e "${RED}❌ Python не найден в системе${NC}"
        echo "Установите Python 3.8+ и запустите: python install.py"
        exit 1
    fi
    
    # After installation, try to run again
    echo -e "${BLUE}🔄 Повторная проверка после установки...${NC}"
    if check_python; then
        python_exec=$(find_python)
        echo -e "${GREEN}✅ Python найден: $python_exec${NC}"
        
        # Устанавливаем зависимости в venv если нужно
        if ! check_dependencies; then
            install_dependencies_in_venv
        fi
        
        if check_ollama; then
            echo -e "${GREEN}✅ Установка завершена! Запуск main.py...${NC}"
            $python_exec main.py
        else
            echo -e "${YELLOW}⚠️ Проблемы с Ollama, но запускаем main.py...${NC}"
            $python_exec main.py
        fi
    else
        echo -e "${RED}❌ Установка не завершена корректно${NC}"
        echo -e "${YELLOW}🔧 Запустите установку вручную: python3 install.py${NC}"
        exit 1
    fi
fi
