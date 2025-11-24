#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import platform
import subprocess
import tarfile
import zipfile
import shutil
import json
from pathlib import Path

class CrossPlatformInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.project_root = Path(__file__).parent
        self.emoji_support = True
        
        # Определяем архитектуру
        if 'x86_64' in self.architecture or 'amd64' in self.architecture:
            self.architecture = 'x86_64'
        elif 'arm64' in self.architecture or 'aarch64' in self.architecture:
            self.architecture = 'arm64'
        else:
            self.architecture = 'x86_64'
            
        print(f"🎯 Обнаружена система: {self.system} {self.architecture}")
        
    def print_step(self, message):
        print(f"\n🔧 {message}...")
        
    def print_success(self, message):
        print(f"✅ {message}")
        
    def print_error(self, message):
        print(f"❌ {message}")
        
    def print_warning(self, message):
        print(f"⚠️ {message}")
        
    def setup_emoji_support(self):
        """Настройка поддержки эмодзи для разных ОС"""
        self.print_step("Настройка поддержки эмодзи")
        
        try:
            if self.system == 'windows':
                os.environ['PYTHONIOENCODING'] = 'utf-8'
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8')
                if hasattr(sys.stderr, 'reconfigure'):
                    sys.stderr.reconfigure(encoding='utf-8')
                    
            elif self.system == 'linux':
                os.environ['LANG'] = 'en_US.UTF-8'
                os.environ['LC_ALL'] = 'en_US.UTF-8'
                
            self.print_success("Поддержка эмодзи настроена")
            
        except Exception as e:
            self.print_warning(f"Эмодзи могут отображаться некорректно: {e}")
            self.emoji_support = False
            
    def install_python(self):
        """Установка Python из локальных файлов"""
        self.print_step("Установка Python")
        
        python_dir = self.project_root / "bin" / "python" / self.system
        
        if not python_dir.exists():
            self.print_error("Файлы Python для вашей ОС не найдены")
            return False
            
        python_archives = list(python_dir.glob("*"))
        if not python_archives:
            self.print_error("Архивы Python не найдены")
            return False
            
        python_archive = python_archives[0]
        install_dir = self.project_root / "python" / "local"
        
        try:
            # Очищаем предыдущую установку
            if install_dir.exists():
                shutil.rmtree(install_dir)
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Распаковываем архив
            self.print_step(f"Распаковка {python_archive.name}")
            
            if python_archive.suffix == '.zip':
                with zipfile.ZipFile(python_archive, 'r') as zip_ref:
                    zip_ref.extractall(install_dir)
            elif python_archive.suffix in ['.gz', '.tgz', '.tar.gz']:
                with tarfile.open(python_archive, 'r:gz') as tar_ref:
                    tar_ref.extractall(install_dir)
                    
            # Проверяем структуру после распаковки
            extracted_items = list(install_dir.iterdir())
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                # Если есть одна директория внутри - перемещаем содержимое на уровень выше
                inner_dir = extracted_items[0]
                for item in inner_dir.iterdir():
                    shutil.move(str(item), str(install_dir))
                inner_dir.rmdir()
                
            self.print_success(f"Python установлен в {install_dir}")
            
            # Проверяем что Python доступен
            python_executable = self._get_python_executable()
            if python_executable and python_executable.exists():
                # Проверяем версию Python
                result = subprocess.run([
                    str(python_executable), "--version"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    self.print_success(f"Версия Python: {result.stdout.strip()}")
                    return True
                    
            self.print_error("Python не доступен после установки")
            return False
            
        except Exception as e:
            self.print_error(f"Ошибка установки Python: {e}")
            return False
            
    def _get_python_executable(self):
        """Получает путь к Python исполняемому файлу"""
        if self.system == 'windows':
            possible_paths = [
                self.project_root / "python" / "local" / "python.exe",
                self.project_root / "python" / "local" / "bin" / "python.exe",
                self.project_root / "venv" / "Scripts" / "python.exe"
            ]
        else:
            possible_paths = [
                self.project_root / "python" / "local" / "bin" / "python3",
                self.project_root / "python" / "local" / "bin" / "python",
                self.project_root / "python" / "local" / "python3",
                self.project_root / "python" / "local" / "python",
                self.project_root / "venv" / "bin" / "python"
            ]
            
        for path in possible_paths:
            if path.exists():
                return path
        return None
        
    def install_pip(self):
        """Установка pip из локальных файлов"""
        self.print_step("Установка pip")
        
        python_executable = self._get_python_executable()
        if not python_executable:
            self.print_error("Python не установлен или не найден")
            return False
            
        self.print_step(f"Используется Python: {python_executable}")
        
        try:
            # Проверяем, установлен ли уже pip
            result = subprocess.run([
                str(python_executable), "-c", "import pip; print(pip.__version__)"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.print_success(f"Pip уже установлен: {result.stdout.strip()}")
                return True
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        # Устанавливаем pip из локального файла
        get_pip_script = self.project_root / "dependencies" / "get-pip.py"
        pip_wheel = self.project_root / "dependencies" / "pip-25.3-py3-none-any.whl"
        
        if not get_pip_script.exists():
            self.print_error("Файл get-pip.py не найден")
            return False
            
        try:
            self.print_step("Запуск установки pip")
            
            # Сначала проверяем что Python работает
            version_result = subprocess.run([
                str(python_executable), "--version"
            ], capture_output=True, text=True)
            
            if version_result.returncode != 0:
                self.print_error("Python не работает корректно")
                return False
                
            # Устанавливаем pip
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root / "python" / "local")
            
            result = subprocess.run([
                str(python_executable), str(get_pip_script),
                "--no-warn-script-location",
                "--no-index",
                "--find-links", str(self.project_root / "dependencies")
            ], env=env, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.print_success("Pip успешно установлен")
                return True
            else:
                self.print_error(f"Ошибка установки pip: {result.stderr}")
                return False
            
        except subprocess.TimeoutExpired:
            self.print_error("Таймаут установки pip")
            return False
        except Exception as e:
            self.print_error(f"Ошибка установки pip: {e}")
            return False

    def _find_correct_pyyaml_wheel(self, dependencies_dir):
        """Находит правильный wheel для PyYAML для текущей системы"""
        self.print_step("Поиск подходящего wheel для PyYAML")
        
        # Получаем все wheels PyYAML
        pyyaml_wheels = list(dependencies_dir.glob("pyyaml*")) + list(dependencies_dir.glob("PyYAML*"))
        
        if not pyyaml_wheels:
            self.print_error("Не найдены wheels для PyYAML")
            return None
        
        # Выводим все доступные wheels для отладки
        self.print_step("Доступные wheels PyYAML:")
        for wheel in pyyaml_wheels:
            print(f"  - {wheel.name}")
        
        # Приоритеты для разных систем
        if self.system == 'linux':
            # Для Linux ищем manylinux wheels
            priority_patterns = [
                f"*manylinux*{self.architecture}*",
                f"*{self.architecture}*manylinux*",
                "*manylinux2014_x86_64*",
                "*manylinux_2_17_x86_64*",
                "*manylinux*",
                "*linux*",
                "*none-any*",  # Универсальный wheel
            ]
        elif self.system == 'windows':
            priority_patterns = [
                f"*win*{self.architecture}*",
                f"*{self.architecture}*win*", 
                "*win_amd64*",
                "*win*",
                "*none-any*",
            ]
        elif self.system == 'darwin':
            priority_patterns = [
                f"*macosx*{self.architecture}*",
                f"*{self.architecture}*macosx*",
                "*macosx*",
                "*none-any*",
            ]
        else:
            priority_patterns = ["*none-any*"]
        
        # Ищем по приоритетам
        for pattern in priority_patterns:
            pattern_clean = pattern.replace('*', '').lower()
            for wheel in pyyaml_wheels:
                wheel_name = wheel.name.lower()
                if pattern_clean in wheel_name:
                    self.print_success(f"Выбран wheel: {wheel.name} (паттерн: {pattern})")
                    return wheel.name
        
        # Если ничего не нашли, берем первый универсальный wheel
        universal_wheels = [w for w in pyyaml_wheels if 'none-any' in w.name.lower()]
        if universal_wheels:
            self.print_warning(f"Используем универсальный wheel: {universal_wheels[0].name}")
            return universal_wheels[0].name
        
        # Или просто первый доступный
        if pyyaml_wheels:
            self.print_warning(f"Используем первый доступный wheel: {pyyaml_wheels[0].name}")
            return pyyaml_wheels[0].name
        
        return None

    def install_pyyaml_fallback(self, python_executable, dependencies_dir):
        """Альтернативный метод установки PyYAML"""
        self.print_step("Попытка альтернативной установки PyYAML")
        
        # Для Linux систем обычно подходят these wheels:
        linux_wheels = [
            "pyyaml-6.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl",
            "PyYAML-6.0.3-cp38-cp38-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl",
            "pyyaml-6.0.3-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl",
            "PyYAML-6.0.2-cp311-cp311-macosx_10_9_x86_64.whl",
            "pyyaml-6.0.3-cp311-cp311-win_amd64.whl"
        ]
        
        for wheel_name in linux_wheels:
            wheel_path = dependencies_dir / wheel_name
            if wheel_path.exists():
                self.print_step(f"Пробуем установить {wheel_name}")
                try:
                    result = subprocess.run([
                        str(python_executable), "-m", "pip", "install",
                        str(wheel_path), "--no-deps", "--no-index"
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        self.print_success(f"PyYAML установлен через {wheel_name}")
                        return True
                    else:
                        self.print_warning(f"Не удалось установить {wheel_name}: {result.stderr}")
                except Exception as e:
                    self.print_warning(f"Ошибка с {wheel_name}: {e}")
        
        return False
            
    def install_dependencies(self):
        """Установка зависимостей из локальных wheel файлов"""
        self.print_step("Установка зависимостей Python")
        
        python_executable = self._get_python_executable()
        if not python_executable:
            self.print_error("Python не доступен")
            return False
            
        dependencies_dir = self.project_root / "dependencies"
        
        try:
            # Сначала обновляем pip
            self.print_step("Обновление pip")
            subprocess.run([
                str(python_executable), "-m", "pip", "install", "--upgrade", "pip",
                "--no-index", "--find-links", str(dependencies_dir)
            ], check=True, timeout=60)
            
            # Устанавливаем зависимости в правильном порядке
            wheels_to_install = [
                "urllib3-2.5.0-py3-none-any.whl",
                "idna-3.11-py3-none-any.whl", 
                "charset_normalizer-3.4.4-py3-none-any.whl",
                "certifi-2025.10.5-py3-none-any.whl",
                "requests-2.32.5-py3-none-any.whl"
            ]
            
            # Находим правильный wheel для PyYAML
            pyyaml_wheel = self._find_correct_pyyaml_wheel(dependencies_dir)
            if pyyaml_wheel:
                wheels_to_install.append(pyyaml_wheel)
            else:
                self.print_error("Не найден подходящий wheel для PyYAML")
                return False
                
            # Устанавливаем все wheels
            for wheel in wheels_to_install:
                wheel_path = dependencies_dir / wheel
                if wheel_path.exists():
                    self.print_step(f"Установка {wheel}")
                    result = subprocess.run([
                        str(python_executable), "-m", "pip", "install",
                        str(wheel_path), "--no-deps", "--no-index"
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        self.print_error(f"Ошибка установки {wheel}: {result.stderr}")
                        
                        # Для PyYAML пробуем fallback
                        if 'yaml' in wheel.lower():
                            self.print_warning("Пробуем альтернативный метод установки PyYAML")
                            if self.install_pyyaml_fallback(python_executable, dependencies_dir):
                                continue
                            else:
                                return False
                        else:
                            return False
                else:
                    self.print_error(f"Wheel не найден: {wheel}")
                    return False
                    
            # Финальная проверка что все зависимости установлены
            self.print_step("Проверка установленных зависимостей")
            try:
                subprocess.run([
                    str(python_executable), "-c", 
                    "import requests, yaml, json, os, sys; print('Все зависимости OK')"
                ], check=True, capture_output=True, timeout=10)
                self.print_success("Все зависимости установлены и проверены")
                return True
            except subprocess.CalledProcessError:
                self.print_error("Не все зависимости установлены корректно")
                
                # Особенно проверяем PyYAML
                try:
                    subprocess.run([
                        str(python_executable), "-c", "import yaml"
                    ], check=True, capture_output=True)
                    self.print_success("PyYAML установлен")
                    return True
                except:
                    self.print_error("PyYAML не установлен, пробуем fallback")
                    if self.install_pyyaml_fallback(python_executable, dependencies_dir):
                        return True
                    else:
                        return False
                        
        except Exception as e:
            self.print_error(f"Ошибка установки зависимостей: {e}")
            return False

    def install_ollama(self):
        """Установка Ollama из локальных файлов"""
        self.print_step("Установка Ollama")
        
        ollama_dir = self.project_root / "bin" / "ollama" / self.system
        
        if not ollama_dir.exists():
            self.print_error("Файлы Ollama для вашей ОС не найдены")
            return False
            
        ollama_archives = list(ollama_dir.glob("*"))
        if not ollama_archives:
            self.print_error("Архивы Ollama не найдены")
            return False
            
        ollama_archive = ollama_archives[0]
        install_dir = self.project_root / "ollama"
        
        try:
            if install_dir.exists():
                shutil.rmtree(install_dir)
            install_dir.mkdir(parents=True, exist_ok=True)
            
            self.print_step(f"Распаковка {ollama_archive.name}")
            
            if self.system == 'windows':
                self._install_ollama_windows(ollama_archive, install_dir)
            else:
                if ollama_archive.suffix in ['.gz', '.tgz', '.tar.gz']:
                    with tarfile.open(ollama_archive, 'r:gz') as tar_ref:
                        # Создаем временную директорию для распаковки
                        temp_dir = install_dir / "temp"
                        temp_dir.mkdir(exist_ok=True)
                        tar_ref.extractall(temp_dir)
                        
                        # Ищем бинарник ollama в распакованных файлах
                        ollama_binary = None
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                if file == 'ollama':
                                    ollama_binary = Path(root) / file
                                    break
                            if ollama_binary:
                                break
                        
                        if ollama_binary and ollama_binary.exists():
                            # Перемещаем бинарник в корень install_dir
                            shutil.move(str(ollama_binary), str(install_dir / "ollama"))
                            # Удаляем временную директорию
                            shutil.rmtree(temp_dir)
                        else:
                            self.print_error("Бинарник ollama не найден в архиве")
                            return False
                            
                elif ollama_archive.suffix == '.zip':
                    with zipfile.ZipFile(ollama_archive, 'r') as zip_ref:
                        zip_ref.extractall(install_dir)
                
                # Делаем бинарник исполняемым
                ollama_binary = install_dir / "ollama"
                if ollama_binary.exists():
                    ollama_binary.chmod(0o755)
                    self.print_success(f"Ollama установлен: {ollama_binary}")
                else:
                    # Проверим есть ли бинарник в поддиректориях
                    found_binary = None
                    for root, dirs, files in os.walk(install_dir):
                        for file in files:
                            if file == 'ollama':
                                found_binary = Path(root) / file
                                # Перемещаем в корень
                                shutil.move(str(found_binary), str(install_dir / "ollama"))
                                (install_dir / "ollama").chmod(0o755)
                                self.print_success(f"Ollama перемещен: {install_dir / 'ollama'}")
                                break
                        if found_binary:
                            break
                    
                    if not found_binary:
                        self.print_error("Бинарник Ollama не найден после установки")
                        return False
                        
            return True
            
        except Exception as e:
            self.print_error(f"Ошибка установки Ollama: {e}")
            return False

    def _install_ollama_windows(self, installer_path, install_dir):
        """Установка Ollama на Windows"""
        install_script = install_dir / "install_ollama.bat"
        with open(install_script, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'"{installer_path}" /S\n')
            f.write('timeout /t 5\n')
        subprocess.run(['cmd', '/c', str(install_script)], check=True)
        
    def setup_ollama_service(self):
        """Запуск Ollama сервиса"""
        self.print_step("Запуск Ollama")
        
        try:
            if self.system == 'windows':
                result = subprocess.run([
                    'sc', 'query', 'Ollama'
                ], capture_output=True, text=True)
                
                if 'RUNNING' in result.stdout:
                    self.print_success("Ollama сервис уже запущен")
                else:
                    subprocess.run([
                        'net', 'start', 'Ollama'
                    ], check=True)
                    self.print_success("Ollama сервис запущен")
                    
            else:
                # Ищем бинарник Ollama в нескольких местах
                possible_paths = [
                    self.project_root / "ollama" / "ollama",
                    self.project_root / "ollama" / "bin" / "ollama",
                ]
                
                ollama_binary = None
                for path in possible_paths:
                    if path.exists():
                        ollama_binary = path
                        break
                
                if not ollama_binary:
                    self.print_error("Бинарник Ollama не найден")
                    return False
                    
                self.print_step(f"Найден Ollama: {ollama_binary}")
                
                # Проверяем не запущен ли уже ollama
                result = subprocess.run([
                    'pgrep', '-f', 'ollama'
                ], capture_output=True)
                
                if result.returncode == 0:
                    self.print_success("Ollama уже запущен")
                    return True
                
                # Запускаем Ollama в фоне
                self.print_step("Запуск Ollama сервера...")
                
                # Создаем лог файл
                log_file = self.project_root / "ollama.log"
                
                # Запускаем процесс
                with open(log_file, 'w') as log:
                    process = subprocess.Popen([
                        str(ollama_binary), 'serve'
                    ], stdout=log, stderr=log, start_new_session=True)
                
                # Даем время на запуск
                import time
                for i in range(10):
                    self.print_step(f"Ожидание запуска Ollama... ({i+1}/10)")
                    try:
                        response = subprocess.run([
                            'curl', '-s', 'http://localhost:11434/api/tags'
                        ], capture_output=True, timeout=5)
                        if response.returncode == 0:
                            self.print_success("Ollama успешно запущен и отвечает!")
                            return True
                    except:
                        pass
                    time.sleep(2)
                
                self.print_error("Ollama не ответил в течение 20 секунд")
                self.print_warning(f"Проверьте лог: {log_file}")
                return False
                
        except Exception as e:
            self.print_error(f"Ошибка запуска Ollama: {e}")
            return False
            
    def install_model(self):
        """Установка модели нейросети"""
        self.print_step("Установка модели")
        
        models_dir = self.project_root / "bin" / "models" / "llama-3.1-8b"
        model_files = list(models_dir.glob("*.gguf"))
        
        if not model_files:
            self.print_error("Файлы модели не найдены")
            return False
            
        ollama_models_dir = self._get_ollama_models_dir()
        if not ollama_models_dir:
            self.print_error("Не удалось найти директорию моделей Ollama")
            return False
            
        try:
            ollama_models_dir.mkdir(parents=True, exist_ok=True)
            
            for model_file in model_files:
                dest_path = ollama_models_dir / model_file.name
                shutil.copy2(model_file, dest_path)
                
            modelfile_path = ollama_models_dir / "Nicole-Kyara.Modelfile"
            with open(modelfile_path, 'w', encoding='utf-8') as f:
                f.write(f'FROM ./{model_files[0].name}\n')
                f.write('TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>\n\n{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>\n\n{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>\n\n"""\n')
                f.write('SYSTEM """Ты - Николь, умный и дружелюбный AI ассистент."""\n')
                
            # Создаем модель в Ollama
            self.print_step("Создание модели в Ollama...")
            import time
            time.sleep(2)  # Даем время Ollama на инициализацию
            
            # Импортируем модель
            ollama_binary = self.project_root / "ollama" / "ollama"
            if ollama_binary.exists():
                result = subprocess.run([
                    str(ollama_binary), 'create', 'nicole-kyara', '-f', str(modelfile_path)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.print_success("Модель создана в Ollama")
                else:
                    self.print_warning(f"Модель не создана автоматически: {result.stderr}")
                    self.print_warning("Вы можете создать модель вручную: ./ollama/ollama create nicole-kyara -f <path-to-modelfile>")
            
            self.print_success("Модель установлена")
            return True
            
        except Exception as e:
            self.print_error(f"Ошибка установки модели: {e}")
            return False
            
    def _get_ollama_models_dir(self):
        """Получает путь к директории моделей Ollama"""
        if self.system == 'windows':
            return Path.home() / "AppData" / "Local" / "ollama" / "models"
        else:
            return Path.home() / ".ollama" / "models"
            
    def create_virtual_env(self):
        """Создает виртуальное окружение"""
        self.print_step("Создание виртуального окружения")
        
        python_executable = self._get_python_executable()
        if not python_executable:
            self.print_error("Python не доступен")
            return False
            
        try:
            venv_dir = self.project_root / "venv"
            
            if venv_dir.exists():
                shutil.rmtree(venv_dir)
                
            subprocess.run([
                str(python_executable), "-m", "venv", str(venv_dir)
            ], check=True, timeout=60)
            
            self.print_success("Виртуальное окружение создано")
            return True
            
        except Exception as e:
            self.print_error(f"Ошибка создания виртуального окружения: {e}")
            return False

    def verify_installation(self):
        """Проверяет корректность установки"""
        self.print_step("Проверка установки")
        
        checks = []
        
        python_executable = self._get_python_executable()
        if python_executable and python_executable.exists():
            checks.append(("✅ Python", True))
            
            # Проверяем зависимости
            try:
                subprocess.run([
                    str(python_executable), "-c", 
                    "import requests, yaml, json, os, sys; print('Dependencies OK')"
                ], check=True, capture_output=True)
                checks.append(("✅ Зависимости", True))
            except:
                checks.append(("❌ Зависимости", False))
        else:
            checks.append(("❌ Python", False))
            checks.append(("❌ Зависимости", False))
            
        # Проверяем Ollama
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                checks.append(("✅ Ollama", True))
                
                # Проверяем наличие нашей модели
                models_response = requests.get('http://localhost:11434/api/tags', timeout=5)
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    if 'models' in models_data:
                        model_names = [model.get('name', '') for model in models_data['models']]
                        if any('nicole-kyara' in name for name in model_names):
                            checks.append(("✅ Модель Nicole-Kyara", True))
                        else:
                            checks.append(("⚠️ Модель Nicole-Kyara", "Файлы есть, но модель не создана"))
            else:
                checks.append(("❌ Ollama", False))
        except:
            checks.append(("❌ Ollama", False))
            
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
        print("="*50)
        
        all_ok = True
        for check_name, status in checks:
            if isinstance(status, bool):
                print(f"{check_name}: {'УСПЕХ' if status else 'ОШИБКА'}")
                if not status:
                    all_ok = False
            else:
                print(f"{check_name}: {status}")
                
        print("="*50)
        
        if all_ok:
            self.print_success("Установка завершена успешно! 🎉")
            print("\n🚀 Запустите приложение командой:")
            if self.system == 'windows':
                print("run.bat")
            else:
                print("./run.sh")
                
            print("\n💡 Дополнительные команды:")
            print("./cleanup.py - удалить ненужные файлы для экономии места")
            print("./check_installation.py - проверить установку")
            print("./check_ollama.py - диагностика Ollama")
        else:
            self.print_warning("Установка завершена с небольшими проблемами")
            print("\n🔧 Рекомендации:")
            print("1. Если модель не создана, выполните вручную:")
            print("   ./ollama/ollama create nicole-kyara -f ~/.ollama/models/Nicole-Kyara.Modelfile")
            print("2. Запустите диагностику: python3 check_ollama.py")
            
        return all_ok
        
    def run(self):
        """Основной метод установки"""
        print("🚀 ЗАПУСК АВТОНОМНОЙ УСТАНОВКИ KYARA")
        print("="*60)
        
        self.setup_emoji_support()
        
        steps = [
            ("Установка Python", self.install_python),
            ("Установка pip", self.install_pip),
            ("Создание виртуального окружения", self.create_virtual_env),
            ("Установка зависимостей", self.install_dependencies),
            ("Установка Ollama", self.install_ollama),
            ("Запуск Ollama", self.setup_ollama_service),
            ("Установка модели", self.install_model),
            ("Проверка установки", self.verify_installation)
        ]
        
        success_count = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            self.print_step(step_name)
            if step_func():
                success_count += 1
            else:
                self.print_error(f"Провален этап: {step_name}")
                # Не прерываем установку, продолжаем для диагностики
                continue
                
        print("\n" + "="*60)
        print(f"📊 УСТАНОВКА ЗАВЕРШЕНА: {success_count}/{total_steps} этапов успешно")
        
        if success_count == total_steps:
            self.print_success("🎉 ВСЕ ЭТАПЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        elif success_count >= total_steps - 1:
            self.print_warning("⚠️ Установка завершена с небольшими проблемами")
        else:
            self.print_error("❌ Установка завершена с ошибками")

if __name__ == "__main__":
    try:
        installer = CrossPlatformInstaller()
        installer.run()
    except KeyboardInterrupt:
        print("\n\n❌ Установка прервана пользователем")
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
