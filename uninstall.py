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
    
    def stop_ollama_processes(self):
        """Останавливает все процессы Ollama"""
        self.logger.info("🛑 Остановка процессов Ollama...")
        try:
            system = platform.system().lower()
            
            if system == "windows":
                # Останавливаем службу Ollama
                subprocess.run(["net", "stop", "Ollama"], 
                             capture_output=True, timeout=30)
                # Убиваем процессы
                subprocess.run(["taskkill", "/f", "/im", "ollama.exe"], 
                             capture_output=True, timeout=30)
            else:
                # Linux/Mac - убиваем процессы
                subprocess.run(["pkill", "-f", "ollama"], 
                             capture_output=True, timeout=30)
                subprocess.run(["pkill", "-9", "-f", "ollama"], 
                             capture_output=True, timeout=30)
            
            self.logger.info("✅ Процессы Ollama остановлены")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось остановить процессы: {e}")
    
    def remove_ollama_model(self):
        """Удаляет модель nicole-kyara из Ollama"""
        self.logger.info("🗑️ Удаление модели nicole-kyara из Ollama...")
        try:
            result = subprocess.run(["ollama", "rm", "nicole-kyara"], 
                         capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.logger.info("✅ Модель nicole-kyara удалена")
            else:
                self.logger.warning(f"⚠️ Не удалось удалить модель: {result.stderr}")
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка удаления модели: {e}")
    
    def remove_ollama_data(self):
        """Удаляет ВСЕ данные Ollama из системы"""
        self.logger.info("🧹 Удаление данных Ollama из системы...")
        
        # Определяем пути к данным Ollama
        ollama_paths = []
        
        if platform.system().lower() == "windows":
            ollama_paths = [
                Path.home() / "AppData" / "Local" / "ollama",
                Path.home() / ".ollama"  # На всякий случай
            ]
        else:
            # Linux/Mac
            ollama_paths = [
                Path.home() / ".ollama",
                Path("/usr/local/bin/ollama")  # Бинарник если установлен системно
            ]
        
        for ollama_path in ollama_paths:
            if ollama_path.exists():
                try:
                    # Спрашиваем подтверждение для удаления ВСЕХ моделей
                    if ollama_path.name == "ollama" and ".ollama" in str(ollama_path):
                        model_count = len(list(ollama_path.glob("models/*"))) if (ollama_path / "models").exists() else 0
                        
                        if model_count > 0:
                            print(f"\n⚠️  Обнаружено {model_count} моделей Ollama в {ollama_path}")
                            response = input("Удалить ВСЕ модели Ollama? (y/N): ")
                            if response.lower() not in ['y', 'yes', 'д', 'да']:
                                self.logger.info(f"⚠️ Пропущено удаление {ollama_path}")
                                continue
                    
                    shutil.rmtree(ollama_path)
                    self.logger.info(f"✅ Удалены данные Ollama: {ollama_path}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Ошибка удаления {ollama_path}: {e}")
    
    def remove_project_files(self):
        """Удаляет ВСЕ файлы проекта кроме самого uninstall.py"""
        self.logger.info("🗑️ Удаление файлов проекта...")
        
        # Сохраняем uninstall.py для последующего удаления
        current_file = Path(__file__)
        
        # Удаляем все файлы и папки кроме текущего скрипта и лога
        items_to_remove = []
        for item in self.base_dir.iterdir():
            if item != current_file and item.name != 'uninstall.log':
                items_to_remove.append(item)
        
        # Сначала удаляем содержимое, потом папки
        for item in items_to_remove:
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
        self.logger.info("🧹 Очистка portable Python зависимостей...")
        
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
                            lib_dir.mkdir()  # Создаем пустую папку обратно
                            self.logger.info(f"✅ Очищены зависимости: {lib_dir}")
                        except Exception as e:
                            self.logger.error(f"❌ Ошибка очистки {lib_dir}: {e}")
                
                # Для Linux/Mac
                else:
                    lib_dir = python_dir / "lib" / "python3.11" / "site-packages"
                    if lib_dir.exists():
                        try:
                            shutil.rmtree(lib_dir)
                            lib_dir.mkdir(parents=True)  # Создаем пустую папку обратно
                            self.logger.info(f"✅ Очищены зависимости: {lib_dir}")
                        except Exception as e:
                            self.logger.error(f"❌ Ошибка очистки {lib_dir}: {e}")
    
    def remove_system_dependencies(self):
        """Предлагает удалить системные зависимости"""
        self.logger.info("🔍 Проверка системных зависимостей...")
        
        # Проверяем установлен ли Ollama системно
        try:
            result = subprocess.run(["ollama", "--version"], 
                         capture_output=True, text=True, check=True)
            
            print(f"\n⚠️  Обнаружен системный Ollama: {result.stdout.strip()}")
            response = input("Удалить Ollama с системы? (y/N): ")
            if response.lower() in ['y', 'yes', 'д', 'да']:
                self.remove_ollama_system()
        except:
            self.logger.info("✅ Ollama не установлен в системе")
    
    def remove_ollama_system(self):
        """Удаляет Ollama с системы"""
        system = platform.system().lower()
        self.logger.info(f"🗑️ Удаление Ollama для {system}...")
        
        try:
            if system == "windows":
                # Через winget или ручное удаление
                result = subprocess.run([
                    "winget", "uninstall", "Ollama.Ollama"
                ], timeout=60, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("✅ Ollama удален через winget")
                else:
                    self.logger.warning("⚠️ Не удалось удалить через winget, удалите вручную")
                
            elif system == "linux":
                # Для Linux (Debian/Ubuntu)
                if shutil.which("apt"):
                    subprocess.run(["sudo", "apt", "remove", "--purge", "-y", "ollama"], 
                                 timeout=30)
                # Для Linux (RedHat/CentOS)
                elif shutil.which("yum"):
                    subprocess.run(["sudo", "yum", "remove", "-y", "ollama"], 
                                 timeout=30)
                # Универсальное удаление
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
    
    def final_cleanup(self):
        """Финальная очистка - удаляет сам скрипт"""
        self.logger.info("🎯 Финальная очистка...")
        
        try:
            # Удаляем лог файл
            log_file = self.base_dir / "uninstall.log"
            if log_file.exists():
                log_file.unlink()
            
            # Удаляем сам скрипт (только если папка почти пустая)
            remaining_items = list(self.base_dir.iterdir())
            if len(remaining_items) <= 2:  # Только . и ..
                self.logger.info("✅ Удаление завершено. Папка проекта пуста.")
                print(f"\n✅ Папка проекта готова к удалению: {self.base_dir}")
            else:
                self.logger.info("⚠️ В папке остались файлы, удалите вручную")
                print(f"\n⚠️  Удалите папку проекта вручную: {self.base_dir}")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка финальной очистки: {e}")
    
    def show_final_instructions(self):
        """Показывает финальные инструкции"""
        print("\n" + "="*50)
        print("🎉 Удаление завершено!")
        print("="*50)
        print("Были удалены:")
        print("  ✅ Все файлы проекта")
        print("  ✅ Модель nicole-kyara из Ollama") 
        print("  ✅ Данные Ollama из системы")
        print("  ✅ Зависимости portable Python")
        print("  ✅ Логи и временные файлы")
        print("\nДля полной очистки:")
        print(f"  Удалите папку проекта: {self.base_dir}")
        print("\nРекомендуется:")
        print("  🔄 Перезагрузить компьютер")
    
    def uninstall(self):
        """Основной метод удаления"""
        self.logger.info("🚀 Запуск полного удаления Nicole...")
        self.logger.info("=" * 50)
        
        try:
            print("⚠️  ВНИМАНИЕ: Это действие удалит ВСЕ данные проекта!")
            print("Будут удалены:")
            print("  • Все файлы и папки проекта")
            print("  • Модель nicole-kyara из Ollama")
            print("  • Все данные Ollama из системы")
            print("  • Все настройки и логи")
            print("  • (Опционально) Ollama с системы")
            print("\nЭто действие НЕОБРАТИМО!")
            
            confirm = input("\nВведите 'DELETE ALL' для подтверждения: ")
            
            if confirm != 'DELETE ALL':
                print("❌ Удаление отменено.")
                return
            
            # 1. Останавливаем процессы Ollama
            self.stop_ollama_processes()
            
            # 2. Удаление модели из Ollama
            self.remove_ollama_model()
            
            # 3. Удаление данных Ollama из системы
            self.remove_ollama_data()
            
            # 4. Очистка portable Python зависимостей
            self.clean_portable_python()
            
            # 5. Удаление всех файлов проекта
            self.remove_project_files()
            
            # 6. Удаление системных зависимостей (опционально)
            self.remove_system_dependencies()
            
            # 7. Финальная очистка
            self.final_cleanup()
            
            # 8. Финальные инструкции
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
    main()
