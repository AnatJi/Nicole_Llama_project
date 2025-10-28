#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import platform
import subprocess
import logging
from pathlib import Path

class NicoleUninstaller:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.base_dir / 'uninstall.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger("NicoleUninstaller")
    
    def remove_ollama_model(self):
        """Удаляет модель nicole-kyara из Ollama"""
        self.logger.info("Удаление модели nicole-kyara из Ollama...")
        try:
            subprocess.run(["ollama", "rm", "nicole-kyara"], 
                         capture_output=True, timeout=30)
            self.logger.info("✅ Модель nicole-kyara удалена")
        except:
            self.logger.warning("⚠️ Не удалось удалить модель nicole-kyara")
    
    def remove_project_data(self):
        """Удаляет все данные проекта"""
        directories_to_remove = [
            self.base_dir / "data",
            self.base_dir / "logs",
            self.base_dir / "__pycache__",
            self.base_dir / "scripts" / "__pycache__"
        ]
        
        files_to_remove = [
            self.base_dir / "install.log",
            self.base_dir / "uninstall.log",
            self.base_dir / "nicole_system.log"
        ]
        
        # Удаление директорий
        for directory in directories_to_remove:
            if directory.exists():
                try:
                    shutil.rmtree(directory)
                    self.logger.info(f"✅ Удалена директория: {directory}")
                except Exception as e:
                    self.logger.error(f"❌ Ошибка удаления {directory}: {e}")
        
        # Удаление файлов
        for file_path in files_to_remove:
            if file_path.exists():
                try:
                    file_path.unlink()
                    self.logger.info(f"✅ Удален файл: {file_path}")
                except Exception as e:
                    self.logger.error(f"❌ Ошибка удаления {file_path}: {e}")
    
    def clean_system_dependencies(self):
        """Очищает системные зависимости (опционально)"""
        self.logger.info("Очистка системных зависимостей...")
        
        # Предлагаем удалить Ollama (только по согласию)
        response = input("Удалить Ollama с системы? (y/N): ")
        if response.lower() == 'y':
            self.remove_ollama_system()
        
        # Предлагаем удалить Python зависимости
        response = input("Удалить Python зависимости проекта? (y/N): ")
        if response.lower() == 'y':
            self.remove_python_dependencies()
    
    def remove_ollama_system(self):
        """Удаляет Ollama с системы"""
        system = platform.system().lower()
        self.logger.info(f"Удаление Ollama для {system}...")
        
        try:
            if system == "windows":
                # Через PowerShell
                subprocess.run([
                    "powershell", "-Command", 
                    "Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like '*Ollama*'} | ForEach-Object {$_.Uninstall()}"
                ], timeout=60)
            elif system == "linux":
                # Для Linux (Ubuntu-based)
                subprocess.run(["sudo", "apt", "remove", "--purge", "-y", "ollama"], 
                             timeout=60)
            elif system == "darwin":
                # Для macOS
                subprocess.run([
                    "sudo", "rm", "-rf", 
                    "/Applications/Ollama.app",
                    "/usr/local/bin/ollama"
                ], timeout=60)
            
            self.logger.info("✅ Ollama удален с системы")
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления Ollama: {e}")
    
    def remove_python_dependencies(self):
        """Удаляет Python зависимости проекта"""
        self.logger.info("Удаление Python зависимостей...")
        
        requirements_file = self.base_dir / "requirements.txt"
        if not requirements_file.exists():
            self.logger.warning("Файл requirements.txt не найден")
            return
        
        try:
            # Получаем список зависимостей
            with open(requirements_file, 'r') as f:
                dependencies = [line.strip().split('>=')[0] for line in f 
                              if line.strip() and not line.startswith('#')]
            
            # Удаляем каждую зависимость
            for dep in dependencies:
                subprocess.run([
                    sys.executable, "-m", "pip", "uninstall", "-y", dep
                ], capture_output=True)
            
            self.logger.info("✅ Python зависимости удалены")
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления зависимостей: {e}")
    
    def show_remaining_files(self):
        """Показывает оставшиеся файлы проекта"""
        self.logger.info("Оставшиеся файлы проекта:")
        
        exclude_dirs = {'bin', '.git'}  # Исключаем бинарники и git
        
        for item in self.base_dir.rglob('*'):
            if item.is_file() and not any(part in exclude_dirs for part in item.parts):
                print(f"  - {item.relative_to(self.base_dir)}")
        
        print("\nДля полного удаления удалите папку проекта вручную:")
        print(f"  {self.base_dir}")
    
    def uninstall(self):
        """Основной метод удаления"""
        self.logger.info("🚀 Запуск удаления Nicole...")
        self.logger.info("=" * 50)
        
        try:
            print("Это действие удалит все данные проекта и настройки.")
            confirm = input("Продолжить? (yes/NO): ")
            
            if confirm.lower() != 'yes':
                print("Удаление отменено.")
                return
            
            # 1. Удаление модели из Ollama
            self.remove_ollama_model()
            
            # 2. Удаление данных проекта
            self.remove_project_data()
            
            # 3. Очистка системных зависимостей (опционально)
            self.clean_system_dependencies()
            
            # 4. Показ оставшихся файлов
            self.show_remaining_files()
            
            self.logger.info("=" * 50)
            self.logger.info("🎉 Удаление завершено!")
            
            print("\n✅ Удаление завершено!")
            print("Ручное удаление: удалите папку проекта для полной очистки.")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления: {e}")
            print(f"❌ Произошла ошибка: {e}")

def main():
    print("🗑️  Удаление Nicole - Полная очистка")
    print("=" * 50)
    print("Этот скрипт удалит:")
    print("  • Все данные и настройки проекта")
    print("  • Логи и временные файлы")
    print("  • Модель nicole-kyara из Ollama")
    print("  • (Опционально) Системные зависимости")
    print("=" * 50)
    
    uninstaller = NicoleUninstaller()
    uninstaller.uninstall()

if __name__ == "__main__":
    import sys
    main()
