#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from memory_manager import MemoryManager

def main():
    print("🎮 СТРИМ-ЧАТ С НИКОЛЬ (LLaMA 3.1)")
    print("=" * 50)
    
    manager = MemoryManager()
    
    # Показываем загруженную конфигурацию
    character = manager.config_loader.load_character()
    print("Персонаж: {} - {}".format(character['name'], character['profession']))
    print("Контекст: 32K токенов (~3 часа стрима)")
    print("🔒 Защита от промпт-инъекций: АКТИВНА")
    print("Для выхода: 'выход', Статистика: 'стата'\n")
    
    while True:
        try:
            user_input = input("Зритель: ").strip()
            
            if user_input.lower() in ['выход', 'exit', 'quit']:
                # Сохраняем финальную версию
                manager.save_conversation()
                print("💾 Диалог сохранен. До свидания!")
                break
                
            elif user_input.lower() == 'стата':
                stats = manager.get_conversation_stats()
                print("📊 Статистика:")
                print(" - Сообщений: {}".format(stats['total_messages']))
                print(" - Символов: {}".format(stats['total_characters']))
                print(" - Зритель: {}".format(stats['user_messages']))
                print(" - Николь: {}".format(stats['assistant_messages']))
                continue
                
            # Авто-сохранение
            manager.auto_save()
            
            # Генерация ответа
            response = manager.chat(user_input)
            print("Николь: {}".format(response))
            print()  # Разделитель
            
        except KeyboardInterrupt:
            print("\n💾 Сохраняю диалог...")
            manager.save_conversation()
            print("До свидания!")
            break
        except Exception as e:
            print("Ошибка: {}".format(e))

if __name__ == "__main__":
    main()
