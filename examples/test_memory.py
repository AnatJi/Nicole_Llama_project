#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from memory_manager import MemoryManager

def test_memory_system():
    print("🧠 ТЕСТ СИСТЕМЫ ПАМЯТИ")
    print("=" * 40)
    
    manager = MemoryManager()
    
    # Тестовая беседа
    test_conversation = [
        {"role": "user", "content": "Привет, Николь! Как дела?"},
        {"role": "assistant", "content": "Все системы функционируют в штатном режиме. Чем могу служить?"},
        {"role": "user", "content": "Расскажи о своих функциях"},
        {"role": "assistant", "content": "В настоящее время активны функции чат-ассистента. Боевые системы на техническом обслуживании."}
    ]
    
    # Сохраняем тестовую беседу
    saved_file = manager.save_conversation(test_conversation, "test_memory")
    print(f"✅ Беседа сохранена: {saved_file}")
    
    # Загружаем предыдущие беседы
    previous_streams = manager.load_previous_streams(days=7)
    print(f"📁 Найдено бесед: {len(previous_streams)}")
    
    # Показываем контекст памяти
    memory_context = manager.get_memory_context()
    print(f"🧠 Контекст памяти:\n{memory_context}")

if __name__ == "__main__":
    test_memory_system()
