#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Настраивает окружение для кроссплатформенной работы"""
    base_dir = Path(__file__).parent
    
    # Добавляем scripts в путь для импорта
    scripts_dir = base_dir / "scripts"
    sys.path.insert(0, str(scripts_dir))
    
    # Настраиваем пути для бинарников
    bin_dir = base_dir / "bin"
    if bin_dir.exists():
        # Добавляем portable Python в PATH если нужно
        python_dirs = [
            bin_dir / "python" / "windows",
            bin_dir / "python" / "linux", 
            bin_dir / "python" / "mac"
        ]
        
        for python_dir in python_dirs:
            if python_dir.exists():
                # Для Windows добавляем папку с python.exe и Scripts
                if python_dir.name == "windows":
                    os.environ['PATH'] = str(python_dir) + os.pathsep + os.environ['PATH']
                    scripts_path = python_dir / "Scripts"
                    if scripts_path.exists():
                        os.environ['PATH'] = str(scripts_path) + os.pathsep + os.environ['PATH']
                # Для Linux/Mac добавляем bin папку
                else:
                    bin_path = python_dir / "bin"
                    if bin_path.exists():
                        os.environ['PATH'] = str(bin_path) + os.pathsep + os.environ['PATH']
                break

# ОСТАЛЬНАЯ ЧАСТЬ main.py БЕЗ ИЗМЕНЕНИЙ
def check_dependencies():
    """Проверяет установлены ли зависимости"""
    try:
        import requests
        import yaml
        import logging
        return True
    except ImportError as e:
        print(f"❌ Не найдены зависимости: {e}")
        print("Запустите установщик: python install.py")
        return False

def check_ollama():
    """Проверяет доступность Ollama"""
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except:
        return False

def ensure_model_exists():
    """Проверяет и создает модель при необходимости"""
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if "nicole-kyara" not in result.stdout:
            print("⚠️ Модель nicole-kyara не найдена")
            print("Создаю модель...")
            
            # Пробуем локальный Modelfile сначала
            modelfile_local = Path("Nicole-Kyara-Local.Modelfile")
            modelfile_online = Path("Nicole-Kyara.Modelfile")
            
            if modelfile_local.exists():
                subprocess.run([
                    "ollama", "create", "nicole-kyara", 
                    "-f", str(modelfile_local)
                ], check=True, timeout=300)
                print("✅ Модель создана из локального файла")
            elif modelfile_online.exists():
                subprocess.run([
                    "ollama", "create", "nicole-kyara", 
                    "-f", str(modelfile_online)
                ], check=True, timeout=600)
                print("✅ Модель создана из онлайн источников")
            else:
                print("❌ Файлы Modelfile не найдены")
                return False
        else:
            print("✅ Модель nicole-kyara обнаружена")
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Таймаут создания модели")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания модели: {e}")
        return False
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return False

def main():
    print("🤖 Nicole - Полностью автономная версия")
    print("=" * 50)
    
    # Настройка окружения
    setup_environment()
    
    # Проверка зависимостей
    if not check_dependencies():
        sys.exit(1)
    
    # Проверка Ollama
    if not check_ollama():
        print("❌ Ollama не доступен")
        print("Запустите установщик: python install.py")
        sys.exit(1)
    
    # Проверка и создание модели
    if not ensure_model_exists():
        print("❌ Не удалось настроить модель")
        sys.exit(1)
    
    # Запуск основной системы
    try:
        from kyara_manager import KyaraCharacterManager
        
        print("🔒 Протоколы безопасности: АКТИВНЫ")
        print("💾 Долговременная память: АКТИВНА") 
        print("🚨 Аварийное сохранение: АКТИВНО")
        print("👑 Госпожа: Кьяра")
        print("\nКоманды:")
        print("  'стата' - статистика диалога")
        print("  'память' - управление памятью") 
        print("  'выход' - завершение работы")
        print("-" * 50)
        
        manager = KyaraCharacterManager()
        
        while True:
            try:
                user_input = input("➤ ").strip()
                
                if user_input.lower() in ['выход', 'exit', 'quit']:
                    print("💾 Сохранение данных...")
                    manager.save_long_term_memory()
                    break
                    
                elif user_input.lower() == 'стата':
                    stats = manager.get_conversation_stats()
                    print(f"📊 Сообщений: {stats['total_messages']}")
                    print(f"🧠 Память: {stats['long_term_memory_entries']} записей")
                    print(f"⭐ Важных: {stats['important_memories']}")
                    print(f"🤖 Модель: {stats['current_model']}")
                    continue
                
                elif user_input.lower() == 'память':
                    print(manager.get_memory_summary())
                    continue
                
                response = manager.chat(user_input)
                print(f"Николь: {response}\n")
                
            except KeyboardInterrupt:
                print("\n🚨 Аварийное завершение...")
                manager.save_long_term_memory()
                break
            except Exception as e:
                print(f"❌ Системная ошибка: {e}")
                
    except Exception as e:
        print(f"❌ Критическая ошибка инициализации: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
