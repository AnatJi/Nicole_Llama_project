#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import platform
import subprocess
import shutil
import time
from pathlib import Path
import logging

class NicoleInstaller:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.bin_dir = self.base_dir / "bin"
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
        self.logger.info(f"Обнаружена ОС: {system}")
        
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "mac"
        else:
            raise Exception(f"Неподдерживаемая ОС: {system}")
    
    def get_portable_python(self):
        """Находит portable Python в проекте"""
        os_type = self.detect_os()
        portable_python = self.bin_dir / "python" / os_type
        
        if os_type == "windows":
            portable_python = portable_python / "python.exe"
        elif os_type == "linux":
            portable_python = portable_python / "bin" / "python3"
        else:  # mac
            portable_python = portable_python / "bin" / "python3"
        
        if portable_python.exists():
            if os_type != "windows":
                portable_python.chmod(0o755)
            self.logger.info(f"✅ Найден portable Python: {portable_python}")
            return str(portable_python)
        
        raise Exception(f"Portable Python не найден по пути: {portable_python}")
    
    def install_python_dependencies(self):
        """Устанавливает Python зависимости оффлайн"""
        self.logger.info("Установка Python зависимостей оффлайн...")
        
        python_cmd = self.get_portable_python()
        dependencies_dir = self.base_dir / "dependencies"
        requirements_file = self.base_dir / "requirements-offline.txt"
        
        if not dependencies_dir.exists():
            self.logger.error("❌ Папка dependencies не найдена")
            raise Exception("Отсутствуют оффлайн зависимости")
        
        if not requirements_file.exists():
            self.logger.error("❌ Файл requirements-offline.txt не найден")
            raise Exception("Отсутствует файл требований")
        
        try:
            # Устанавливаем зависимости из локальной папки
            result = subprocess.run([
                python_cmd, "-m", "pip", "install",
                "--no-index", "--find-links", str(dependencies_dir),
                "-r", str(requirements_file)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("✅ Python зависимости установлены")
                self.logger.info(result.stdout)
            else:
                self.logger.error(f"❌ Ошибка установки: {result.stderr}")
                raise Exception("Не удалось установить зависимости")
                
        except subprocess.TimeoutExpired:
            self.logger.error("⏰ Таймаут установки зависимостей")
            raise
        except Exception as e:
            self.logger.error(f"❌ Ошибка установки зависимостей: {e}")
            raise
    
    def install_ollama_windows(self):
        """Устанавливает Ollama на Windows"""
        ollama_setup = self.bin_dir / "ollama" / "windows" / "OllamaSetup.exe"
        
        if not ollama_setup.exists():
            self.logger.error("❌ OllamaSetup.exe не найден")
            return False
        
        self.logger.info("🚀 Установка Ollama для Windows...")
        try:
            # Запускаем установщик
            process = subprocess.Popen([str(ollama_setup)], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            # Ждем завершения установки
            time.sleep(30)
            
            # Проверяем, завершился ли процесс
            if process.poll() is None:
                self.logger.info("⚠️ Установка занимает больше времени...")
                time.sleep(30)
            
            self.logger.info("✅ Установка Ollama завершена")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка установки Ollama: {e}")
            return False
    
    def install_ollama_linux(self):
        """Устанавливает Ollama на Linux"""
        self.logger.info("🚀 Установка Ollama для Linux...")
        
        try:
            # Скачиваем и устанавливаем Ollama
            result = subprocess.run([
                "curl", "-fsSL", "https://ollama.com/install.sh"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.error("❌ Не удалось скачать скрипт установки")
                return False
            
            # Выполняем скрипт установки
            install_result = subprocess.run(
                ["sh"], 
                input=result.stdout, 
                text=True,
                timeout=120
            )
            
            if install_result.returncode == 0:
                self.logger.info("✅ Ollama установлен для Linux")
                return True
            else:
                self.logger.error("❌ Ошибка установки Ollama для Linux")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка установки Ollama для Linux: {e}")
            return False
    
    def install_ollama_mac(self):
        """Устанавливает Ollama на macOS"""
        ollama_app = self.bin_dir / "ollama" / "mac" / "Ollama.app"
        
        if not ollama_app.exists():
            self.logger.error("❌ Ollama.app не найден")
            return False
        
        self.logger.info("🚀 Установка Ollama для macOS...")
        try:
            # Копируем в Applications
            applications_dir = Path("/Applications")
            if ollama_app.exists():
                shutil.copytree(ollama_app, applications_dir / "Ollama.app", 
                              dirs_exist_ok=True)
                self.logger.info("✅ Ollama скопирован в Applications")
                
                # Запускаем Ollama
                subprocess.run(["open", "-a", "Ollama"], check=True)
                self.logger.info("✅ Ollama запущен")
                time.sleep(10)
                return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка установки Ollama для macOS: {e}")
            return False
    
    def install_ollama(self):
        """Устанавливает Ollama в зависимости от ОС"""
        if self.check_ollama_installed():
            self.logger.info("✅ Ollama уже установлен")
            return True
        
        os_type = self.detect_os()
        self.logger.info(f"Установка Ollama для {os_type}...")
        
        if os_type == "windows":
            return self.install_ollama_windows()
        elif os_type == "linux":
            return self.install_ollama_linux()
        elif os_type == "mac":
            return self.install_ollama_mac()
        else:
            self.logger.error(f"Неподдерживаемая ОС: {os_type}")
            return False
    
    def check_ollama_installed(self):
        """Проверяет, установлен ли Ollama"""
        try:
            result = subprocess.run(
                ["ollama", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info(f"✅ Ollama обнаружен: {result.stdout.strip()}")
                return True
        except:
            pass
        return False
    
    def setup_local_model(self):
        """Настраивает локальную модель"""
        local_model_dir = self.bin_dir / "models" / "llama-3.1-8b"
        model_files = list(local_model_dir.glob("*.gguf"))
        
        if not model_files:
            self.logger.warning("⚠️ Локальная модель не найдена")
            self.logger.info("Создание модели из онлайн источников...")
            return self.setup_online_model()
        
        model_file = model_files[0]
        self.logger.info(f"✅ Локальная модель обнаружена: {model_file.name}")
        
        try:
            # Создаем Modelfile для локальной модели
            modelfile_content = f"""FROM {model_file}

SYSTEM \"\"\"{{{{ .System }}}}\"\"\"

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 32000
"""
            modelfile_path = self.base_dir / "Nicole-Kyara-Local.Modelfile"
            with open(modelfile_path, 'w', encoding='utf-8') as f:
                f.write(modelfile_content)
            
            # Создаем модель в Ollama
            self.logger.info("🚀 Создание модели из локального файла...")
            result = subprocess.run([
                "ollama", "create", "nicole-kyara", 
                "-f", str(modelfile_path)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("✅ Локальная модель nicole-kyara создана")
                return True
            else:
                self.logger.error(f"❌ Ошибка создания модели: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("⏰ Таймаут создания модели")
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка настройки локальной модели: {e}")
            return False
    
    def setup_online_model(self):
        """Настраивает модель из онлайн источников (запасной вариант)"""
        self.logger.info("🚀 Создание модели из онлайн источников...")
        
        modelfile_path = self.base_dir / "Nicole-Kyara.Modelfile"
        if not modelfile_path.exists():
            self.logger.error("❌ Nicole-Kyara.Modelfile не найден")
            return False
        
        try:
            result = subprocess.run([
                "ollama", "create", "nicole-kyara", 
                "-f", str(modelfile_path)
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.logger.info("✅ Модель nicole-kyara создана")
                return True
            else:
                self.logger.error(f"❌ Ошибка создания модели: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("⏰ Таймаут создания модели")
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка настройки модели: {e}")
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
        
        # Проверяем доступное место на диске
        try:
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free // (2**30)
            if free_gb < 10:
                self.logger.warning(f"⚠️ Мало свободного места: {free_gb}GB (рекомендуется 10GB+)")
            else:
                self.logger.info(f"✅ Свободное место: {free_gb}GB")
        except:
            self.logger.warning("⚠️ Не удалось проверить свободное место")
        
        return True
    
    def wait_for_ollama_service(self, max_wait=60):
        """Ожидает запуска службы Ollama"""
        self.logger.info("⏳ Ожидание запуска службы Ollama...")
        
        for i in range(max_wait):
            try:
                result = subprocess.run(
                    ["ollama", "list"], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.logger.info("✅ Служба Ollama запущена")
                    return True
            except:
                pass
            
            time.sleep(1)
            if (i + 1) % 10 == 0:
                self.logger.info(f"   ...ожидание ({i+1}/{max_wait} секунд)")
        
        self.logger.error("❌ Служба Ollama не запустилась")
        return False
    
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
            
            # 4. Установка Ollama
            ollama_installed = self.install_ollama()
            if not ollama_installed:
                self.logger.warning("⚠️ Ollama не установлен автоматически")
                self.logger.info("Установите Ollama вручную с https://ollama.com")
                return False
            
            # 5. Ожидание запуска службы Ollama
            if not self.wait_for_ollama_service():
                self.logger.warning("⚠️ Служба Ollama не запустилась автоматически")
                self.logger.info("Запустите Ollama вручную и повторите установку")
                return False
            
            # 6. Настройка модели
            model_ready = self.setup_local_model()
            if not model_ready:
                self.logger.warning("⚠️ Не удалось настроить локальную модель")
                return False
            
            self.logger.info("=" * 50)
            self.logger.info("🎉 Установка завершена успешно!")
            return True
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка установки: {e}")
            return False

def main():
    print("🤖 Установщик Nicole - Полностью автономная версия")
    print("=" * 50)
    print("Этот установщик:")
    print("  • Установит Python зависимости оффлайн")
    print("  • Установит Ollama")
    print("  • Настроит локальную модель")
    print("  • Создаст все необходимые директории")
    print("=" * 50)
    
    installer = NicoleInstaller()
    success = installer.install()
    
    if success:
        print("\n✅ Установка завершена успешно!")
        print("Запустите проект:")
        print("  Windows: run.bat")
        print("  Linux/Mac: ./run.sh")
    else:
        print("\n❌ Установка завершена с ошибками")
        print("Проверьте файл install.log для деталей")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
