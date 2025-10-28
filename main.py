#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Проверяет установлены ли зависимости"""
    base_dir = Path(__file__).parent
    scripts_dir = base_dir / "scripts"
    
    # Добавляем scripts в путь
    sys.path.insert(0, str(scripts_dir))
    
    try:
        import requests
        import yaml
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

def setup_environment():
    """Настраивает окружение"""
    base_dir = Path(__file__).parent
    bin_dir = base_dir / "bin"
    
    # Добавляем локальные бинарники в PATH
    if bin_dir.exists():
        ollama_dirs = [
            bin_dir / "ollama" / "windows",
            bin_dir / "ollama" / "linux", 
            bin_dir / "ollama" / "mac"
        ]
        
        for ollama_dir in ollama_dirs:
            if ollama_dir.exists():
                os.environ['PATH'] = str(ollama_dir) + os.pathsep + os.environ['PATH']
                break

def main():
    print("🤖 Nicole - Автономная версия")
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
    
    # Проверка модели
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
            
            modelfile = Path("Nicole-Kyara.Modelfile")
            if modelfile.exists():
                subprocess.run([
                    "ollama", "create", "nicole-kyara", 
                    "-f", str(modelfile)
                ], check=True)
                print("✅ Модель создана")
            else:
                print("❌ Файл Nicole-Kyara.Modelfile не найден")
                sys.exit(1)
    except subprocess.TimeoutExpired:
        print("❌ Таймаут проверки моделей")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания модели: {e}")
        sys.exit(1)
    
    # Запуск основной системы
    try:
        from scripts.kyara_manager import KyaraCharacterManager
        
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
