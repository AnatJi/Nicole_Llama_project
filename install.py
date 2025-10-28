#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import logging

class NicoleInstaller:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.bin_dir = self.base_dir / "bin"
        self.scripts_dir = self.base_dir / "scripts"
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.base_dir / 'install.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger("NicoleInstaller")
    
    def detect_os(self):
        """Определяет операционную систему"""
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        self.logger.info(f"Обнаружена ОС: {system}, архитектура: {arch}")
        
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "mac"
        else:
            raise Exception(f"Неподдерживаемая ОС: {system}")
    
    def install_python_dependencies(self):
        """Устанавливает Python зависимости"""
        self.logger.info("Установка Python зависимостей...")
        
        requirements_file = self.base_dir / "requirements.txt"
        if not requirements_file.exists():
            self.logger.warning("Файл requirements.txt не найден")
            return
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", str(requirements_file)
            ])
            self.logger.info("✅ Python зависимости установлены")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Ошибка установки зависимостей: {e}")
            raise
    
    def setup_ollama(self):
        """Настраивает Ollama локально"""
        os_type = self.detect_os()
        ollama_bin_dir = self.bin_dir / "ollama" / os_type
        
        self.logger.info(f"Настройка Ollama для {os_type}...")
        
        if not ollama_bin_dir.exists():
            self.logger.error(f"❌ Ollama не найден для {os_type}")
            self.logger.info("Скачайте Ollama с https://ollama.ai и поместите в bin/ollama/")
            return False
        
        # Добавляем Ollama в PATH для текущей сессии
        ollama_path = str(ollama_bin_dir)
        if ollama_path not in os.environ['PATH']:
            os.environ['PATH'] = ollama_path + os.pathsep + os.environ['PATH']
        
        # Проверяем доступность ollama
        try:
            result = subprocess.run(
                ["ollama", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info("✅ Ollama настроен корректно")
                return True
            else:
                self.logger.error("❌ Ollama не запускается")
                return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска Ollama: {e}")
            return False
    
    def setup_local_model(self):
        """Настраивает локальную модель"""
        models_dir = self.bin_dir / "models"
        local_model_dir = models_dir / "llama-3.1-8b"
        
        self.logger.info("Проверка локальной модели...")
        
        if local_model_dir.exists():
            # Модель уже есть локально
            self.logger.info("✅ Локальная модель обнаружена")
            return True
        else:
            self.logger.warning("⚠️ Локальная модель не найдена")
            self.logger.info("Для автономной работы скачайте модель и поместите в bin/models/")
            return False
    
    def create_directories(self):
        """Создает необходимые директории"""
        directories = [
            self.base_dir / "data",
            self.base_dir / "data" / "long_term_memory",
            self.base_dir / "data" / "emergency_backup",
            self.base_dir / "data" / "conversations",
            self.base_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Создана директория: {directory}")
    
    def check_system_requirements(self):
        """Проверяет системные требования"""
        self.logger.info("Проверка системных требований...")
        
        # Проверяем Python версию
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.logger.error("❌ Требуется Python 3.8 или выше")
            return False
        
        self.logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Проверяем доступное место на диске
        try:
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free // (2**30)
            if free_gb < 5:
                self.logger.warning(f"⚠️ Мало свободного места: {free_gb}GB (рекомендуется 5GB+)")
            else:
                self.logger.info(f"✅ Свободное место: {free_gb}GB")
        except:
            self.logger.warning("⚠️ Не удалось проверить свободное место")
        
        return True
    
    def install(self):
        """Основной метод установки"""
        self.logger.info("🚀 Запуск установки Nicole...")
        self.logger.info("=" * 50)
        
        try:
            # 1. Проверка системы
            if not self.check_system_requirements():
                raise Exception("Системные требования не выполнены")
            
            # 2. Создание директорий
            self.create_directories()
            
            # 3. Установка Python зависимостей
            self.install_python_dependencies()
            
            # 4. Настройка Ollama
            ollama_ready = self.setup_ollama()
            
            # 5. Настройка модели
            model_ready = self.setup_local_model()
            
            self.logger.info("=" * 50)
            
            if ollama_ready and model_ready:
                self.logger.info("🎉 Установка завершена! Запустите: python main.py")
                return True
            else:
                self.logger.warning("⚠️ Установка завершена с предупреждениями")
                self.logger.info("Для работы необходим Ollama и модель Llama")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка установки: {e}")
            return False

def main():
    print("🤖 Установщик Nicole - Автономная версия")
    print("=" * 50)
    
    installer = NicoleInstaller()
    success = installer.install()
    
    if success:
        print("\n✅ Установка завершена успешно!")
        print("Запустите проект: python main.py")
    else:
        print("\n❌ Установка завершена с ошибками")
        print("Проверьте файл install.log для деталей")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
