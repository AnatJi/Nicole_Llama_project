#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from kyara_manager import KyaraCharacterManager

def main():
    print("🤖 СИСТЕМА НИКОЛЬ - АКТИВАЦИЯ")
    print("=" * 50)
    print("🔒 Протоколы безопасности: АКТИВНЫ")
    print("💾 Долговременная память: АКТИВНА") 
    print("🚨 Аварийное сохранение: АКТИВНО")
    print("👑 Госпожа: Кьяра")
    print("\nДля выхода: 'выход', Статистика: 'стата'\n")
    
    manager = KyaraCharacterManager()
    
    while True:
        try:
            user_input = input("➤ ").strip()
            
            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("💾 Сохранение данных...")
                break
                
            elif user_input.lower() == 'стата':
                stats = manager.get_conversation_stats()
                print(f"📊 Сообщений: {stats['total_messages']}")
                print(f"🧠 Память: {stats['long_term_memory_entries']} записей")
                print(f"💾 Использование: {stats['memory_usage']}")
                continue
            
            response = manager.chat(user_input)
            print(f"Николь: {response}\n")
            
        except KeyboardInterrupt:
            print("\n🚨 Аварийное завершение...")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
