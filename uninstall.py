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
            result = subprocess.run(["ollama", "rm", "nicole-kyara"], 
                         capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.logger.info("✅ Модель nicole-kyara удалена")
            else:
                self.logger.warning(f"⚠️ Не удалось удалить модель: {result.stderr}")
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка удаления модели: {e}")
    
    def remove_project_files(self):
        """Удаляет ВСЕ файлы проекта кроме самого uninstall.py"""
        self.logger.info("Удаление файлов проекта...")
        
        # Сохраняем uninstall.py для последующего удаления
        current_file = Path(__file__)
        
        # Удаляем все файлы и папки кроме текущего скрипта
        for item in self.base_dir.iterdir():
            if item != current_file and item.name != 'uninstall.log':
                try:
                    if item.is_file():
                        item.unlink()
                        self.logger.info(f"✅ Удален файл: {item.name}")
                    elif item.is_dir():
                        shutil.rmtree(item)
                        self.logger.info(f"✅ Удалена папка: {item.name}")
                except Exception as e:
                    self.logger.error(f"❌ Ошибка удаления {item}: {e}")
    
    def clean_portable_python(self):
        """Очищает установленные зависимости portable Python"""
        self.logger.info("Очистка portable Python зависимостей...")
        
        python_dirs = [
            self.base_dir / "bin" / "python" / "windows",
            self.base_dir / "bin" / "python" / "linux", 
            self.base_dir / "bin" / "python" / "mac"
        ]
        
        for python_dir in python_dirs:
            if python_dir.exists():
                # Для Windows
                if python_dir.name == "windows":
                    lib_dir = python_dir / "Lib" / "site-packages"
                    if lib_dir.exists():
                        try:
                            shutil.rmtree(lib_dir)
                            self.logger.info(f"✅ Очищены зависимости: {lib_dir}")
                        except Exception as e:
                            self.logger.error(f"❌ Ошибка очистки {lib_dir}: {e}")
                
                # Для Linux/Mac
                else:
                    lib_dir = python_dir / "lib" / "python3.11" / "site-packages"
                    if lib_dir.exists():
                        try:
                            shutil.rmtree(lib_dir)
                            self.logger.info(f"✅ Очищены зависимости: {lib_dir}")
                        except Exception as e:
                            self.logger.error(f"❌ Ошибка очистки {lib_dir}: {e}")
    
    def remove_system_dependencies(self):
        """Предлагает удалить системные зависимости"""
        self.logger.info("Проверка системных зависимостей...")
        
        # Проверяем установлен ли Ollama
        try:
            subprocess.run(["ollama", "--version"], 
                         capture_output=True, check=True)
            response = input("Удалить Ollama с системы? (y/N): ")
            if response.lower() == 'y':
                self.remove_ollama_system()
        except:
            self.logger.info("✅ Ollama не установлен в системе")
    
    def remove_ollama_system(self):
        """Удаляет Ollama с системы"""
        system = platform.system().lower()
        self.logger.info(f"Удаление Ollama для {system}...")
        
        try:
            if system == "windows":
                # Через winget или ручное удаление
                subprocess.run([
                    "winget", "uninstall", "Ollama.Ollama"
                ], timeout=60, capture_output=True)
                self.logger.info("✅ Ollama удален через winget")
                
            elif system == "linux":
                # Для Linux (универсальный способ)
                subprocess.run(["sudo", "rm", "-f", "/usr/local/bin/ollama"], 
                             timeout=30)
                self.logger.info("✅ Ollama удален для Linux")
                
            elif system == "darwin":
                # Для macOS
                subprocess.run([
                    "sudo", "rm", "-rf", 
                    "/Applications/Ollama.app",
                    "/usr/local/bin/ollama"
                ], timeout=30)
                self.logger.info("✅ Ollama удален для macOS")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления Ollama: {e}")
            print("Удалите Ollama вручную с Панели управления")
    
    def show_final_instructions(self):
        """Показывает финальные инструкции"""
        print("\n" + "="*50)
        print("🗑️  Удаление завершено!")
        print("="*50)
        print("Были удалены:")
        print("  ✅ Все файлы проекта")
        print("  ✅ Модель nicole-kyara из Ollama") 
        print("  ✅ Зависимости portable Python")
        print("  ✅ Логи и временные файлы")
        print("\nДля полной очистки:")
        print(f"  Удалите папку проекта: {self.base_dir}")
        print("\nЕсли вы удалили Ollama:")
        print("  Перезагрузите компьютер для завершения удаления")
    
    def uninstall(self):
        """Основной метод удаления"""
        self.logger.info("🚀 Запуск полного удаления Nicole...")
        self.logger.info("=" * 50)
        
        try:
            print("⚠️  ВНИМАНИЕ: Это действие удалит ВСЕ данные проекта!")
            print("Будут удалены:")
            print("  • Все файлы и папки проекта")
            print("  • Модель nicole-kyara из Ollama")
            print("  • Все настройки и логи")
            print("  • (Опционально) Ollama с системы")
            print("\nЭто действие НЕОБРАТИМО!")
            
            confirm = input("\nВведите 'DELETE ALL' для подтверждения: ")
            
            if confirm != 'DELETE ALL':
                print("❌ Удаление отменено.")
                return
            
            # 1. Удаление модели из Ollama
            self.remove_ollama_model()
            
            # 2. Очистка portable Python зависимостей
            self.clean_portable_python()
            
            # 3. Удаление всех файлов проекта
            self.remove_project_files()
            
            # 4. Удаление системных зависимостей (опционально)
            self.remove_system_dependencies()
            
            # 5. Финальные инструкции
            self.show_final_instructions()
            
            self.logger.info("🎉 Полное удаление завершено!")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления: {e}")
            print(f"❌ Произошла ошибка: {e}")

def main():
    print("🗑️  Nicole - Полное удаление")
    print("=" * 50)
    print("Этот скрипт полностью удалит проект Nicole")
    print("и все связанные с ним данные.")
    print("=" * 50)
    
    uninstaller = NicoleUninstaller()
    uninstaller.uninstall()

if __name__ == "__main__":
    import sys
    main()
