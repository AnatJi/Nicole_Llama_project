#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import os
import random
from datetime import datetime
from config_loader import ConfigLoader
from security_system import SecuritySystem
from context_optimizer import ContextOptimizer
from emergency_save import EmergencySave

class KyaraCharacterManager:
    def __init__(self, config_path="config", data_path="data"):
        self.config_loader = ConfigLoader(config_path)
        self.settings = self.config_loader.load_settings()
        self.security_system = SecuritySystem(config_path)
        self.context_optimizer = ContextOptimizer(data_path)
        self.emergency_save = EmergencySave(data_path)
        
        # Настраиваем аварийное сохранение
        self.emergency_save.setup_emergency_handlers()
        
        self.model = self.settings['model']['name']
        self.base_url = "http://localhost:11434/api"
        self.conversation_history = []
        self.long_term_memory = []
        
        # Загружаем системный промпт
        system_prompt = self.config_loader.build_system_prompt()
        self.add_system_message(system_prompt)
        
        # Загружаем долговременную память и добавляем в контекст
        self.load_long_term_memory()
        self.inject_memory_into_context()
        
        # Счетчики для автосохранения
        self.message_count = 0
        
        print("🧠 Долговременная память: ЗАГРУЖЕНА")
        if self.long_term_memory:
            print(f"   📚 Воспоминаний: {len(self.long_term_memory)}")
        
    def add_system_message(self, message):
        self.conversation_history.append({"role": "system", "content": message})
    
    def load_long_term_memory(self):
        """Загружает долговременную память из файла"""
        memory_dir = os.path.join("data", "long_term_memory")
        os.makedirs(memory_dir, exist_ok=True)
        memory_file = os.path.join(memory_dir, "memory.json")
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    self.long_term_memory = json.load(f)
                print(f"✅ Загружено воспоминаний: {len(self.long_term_memory)}")
            except Exception as e:
                print(f"❌ Ошибка загрузки памяти: {e}")
                self.long_term_memory = []
        else:
            self.long_term_memory = []
    
    def inject_memory_into_context(self):
        """Добавляет воспоминания в системный промпт"""
        if not self.long_term_memory:
            return
        
        memory_context = self.build_memory_context()
        if memory_context:
            # Обновляем системный промпт с памятью
            if self.conversation_history and self.conversation_history[0]['role'] == 'system':
                self.conversation_history[0]['content'] += f"\n\nВАЖНЫЕ ВОСПОМИНАНИЯ ИЗ ПРОШЛЫХ БЕСЕД:\n{memory_context}"
                print("🔗 Воспоминания добавлены в контекст")
    
    def build_memory_context(self):
        """Строит контекст из долговременной памяти"""
        if not self.long_term_memory:
            return ""
        
        context = ""
        # Берем последние 15 важных воспоминаний
        important_memories = sorted(
            [m for m in self.long_term_memory if m.get('importance', 0) >= 2],
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )[:15]
        
        for memory in important_memories:
            timestamp = memory.get('timestamp', '')[:16]  # Берем дату и время
            content = memory['content']
            context += f"- {content} ({timestamp})\n"
        
        return context
    
    def enhance_memory_detection(self, message):
        """Улучшенное определение важных для запоминания фраз"""
        content = message['content'].lower()
        role = message['role']
        
        # Запросы на запоминание
        memory_requests = [
            'запомни', 'запомни что', 'не забудь', 'напомни', 'сохрани в память',
            'запиши', 'учти', 'имей в виду', 'держи в памяти'
        ]
        
        # Ключевые объекты и действия
        important_objects = [
            'склад', 'шляпа', 'фиолетов', 'поручен', 'задание', 'просьб',
            'документ', 'ключ', 'оружие', 'кофе', 'чай', 'подарок'
        ]
        
        # Вопросы о прошлом
        past_references = [
            'в прошлый раз', 'ранее', 'раньше', 'помнишь', 'вспомни',
            'на прошлом стриме', 'в предыдущей беседе', 'мы говорили'
        ]
        
        # ОЧЕНЬ ВАЖНО: явные просьбы запомнить
        if any(phrase in content for phrase in memory_requests):
            return 5  # Максимальная важность
        
        # ВАЖНО: упоминания ключевых объектов
        if any(obj in content for obj in important_objects):
            return 4
        
        # СРЕДНЯЯ ВАЖНОСТЬ: вопросы о прошлом
        if any(ref in content for ref in past_references):
            return 3
            
        # Базовая важность из context_optimizer
        return self.context_optimizer.calculate_importance(message)
    
    def manual_memory_save(self, content, importance=4):
        """Ручное сохранение в память"""
        memory_entry = {
            'timestamp': self._get_timestamp(),
            'content': content,
            'role': 'memory',
            'importance': importance,
            'type': 'user_request'
        }
        self.long_term_memory.append(memory_entry)
        self.save_long_term_memory()
        return f"✅ Информация сохранена в долговременную память: '{content}'"
    
    def save_long_term_memory(self):
        """Сохраняет долговременную память в файл"""
        memory_dir = os.path.join("data", "long_term_memory")
        os.makedirs(memory_dir, exist_ok=True)
        memory_file = os.path.join(memory_dir, "memory.json")
        
        # Ограничиваем размер памяти (последние 200 записей)
        if len(self.long_term_memory) > 200:
            self.long_term_memory = self.long_term_memory[-200:]
        
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения памяти: {e}")
    
    def detect_memory_commands(self, user_message):
        """Обрабатывает специальные команды памяти"""
        message_lower = user_message.lower()
        
        # Команда явного сохранения в память
        if any(cmd in message_lower for cmd in ['запомни что', 'сохрани в память', 'не забудь что']):
            # Извлекаем содержание для запоминания
            content_to_save = user_message
            for prefix in ['запомни что', 'сохрани в память', 'не забудь что']:
                if prefix in message_lower:
                    content_to_save = user_message[user_message.lower().find(prefix) + len(prefix):].strip()
                    break
            
            if content_to_save and len(content_to_save) > 5:
                response = self.manual_memory_save(content_to_save, importance=5)
                return True, response
        
        # Показать память
        if 'покажи память' in message_lower or 'что помнишь' in message_lower:
            memory_summary = self.get_memory_summary()
            return True, f"Текущее состояние памяти:\n{memory_summary}"
        
        # Очистить память
        if 'очисти память' in message_lower or 'удали воспоминания' in message_lower:
            self.long_term_memory = []
            self.save_long_term_memory()
            return True, "✅ Долговременная память очищена."
        
        return False, None
    
    def get_memory_summary(self):
        """Возвращает сводку по памяти"""
        if not self.long_term_memory:
            return "Память пуста."
        
        total = len(self.long_term_memory)
        important = len([m for m in self.long_term_memory if m.get('importance', 0) >= 3])
        recent = len([m for m in self.long_term_memory[-10:]])
        
        summary = f"Всего воспоминаний: {total}\n"
        summary += f"Важных: {important}\n"
        summary += f"Недавних: {recent}\n\n"
        summary += "Последние 5 записей:\n"
        
        for memory in self.long_term_memory[-5:]:
            content = memory['content'][:50] + "..." if len(memory['content']) > 50 else memory['content']
            importance = memory.get('importance', 0)
            summary += f"- {content} (важность: {importance}/5)\n"
        
        return summary
    
    def optimize_context(self):
        """Оптимизирует контекст для экономии памяти"""
        if len(self.conversation_history) > 25:
            self.conversation_history = self.context_optimizer.compress_conversation(
                self.conversation_history
            )
    
    def save_to_long_term_memory(self, message):
        """Сохраняет важные сообщения в долговременную память"""
        importance = self.enhance_memory_detection(message)
        
        if importance >= 2:  # Порог для сохранения
            memory_entry = {
                'timestamp': self._get_timestamp(),
                'content': message['content'],
                'role': message['role'],
                'importance': importance,
                'type': 'auto_save'
            }
            self.long_term_memory.append(memory_entry)
            
            # Автосохранение файла каждые 5 важных сообщений
            if importance >= 3 and len(self.long_term_memory) % 5 == 0:
                self.save_long_term_memory()
    
    def _get_timestamp(self):
        return datetime.now().isoformat()
    
    def chat(self, user_message):
        # АВАРИЙНОЕ СОХРАНЕНИЕ каждые 50 сообщений
        self.message_count += 1
        if self.message_count % 50 == 0:
            self.emergency_save.save_emergency_state({
                'conversation_history': self.conversation_history[-20:],
                'long_term_memory': self.long_term_memory[-100:]
            })
        
        # ПРОВЕРКА КОМАНД ПАМЯТИ
        is_memory_command, memory_response = self.detect_memory_commands(user_message)
        if is_memory_command:
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": memory_response})
            return memory_response
        
        # ПРОВЕРКА БЕЗОПАСНОСТИ
        is_injection, security_response = self.security_system.detect_injection_attempt(user_message)
        if is_injection:
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": security_response})
            return security_response
        
        # ОПТИМИЗАЦИЯ КОНТЕКСТА
        self.optimize_context()
        
        # ДОБАВЛЕНИЕ СООБЩЕНИЯ
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # СОХРАНЕНИЕ В ДОЛГОВРЕМЕННУЮ ПАМЯТЬ
        self.save_to_long_term_memory({"role": "user", "content": user_message})
        
        # ПОДГОТОВКА ДАННЫХ ДЛЯ API
        recent_messages = self.conversation_history[-self.settings['memory']['short_term_messages']:]
        
        data = {
            "model": self.model,
            "messages": recent_messages,
            "stream": False,
            "options": {
                "num_predict": self.settings['model']['max_tokens'],
                "temperature": self.settings['model']['temperature'],
                "top_p": self.settings['model']['top_p'],
                "repeat_penalty": self.settings['model']['repeat_penalty']
            }
        }
        
        try:
            response = requests.post(self.base_url + "/chat", json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['message']['content']
                
                # УБЕДИТЕСЬ ЧТО ОТВЕТ ПОЛНЫЙ
                if not assistant_message.endswith(('.', '!', '?')) and len(assistant_message) > 50:
                    assistant_message += "."
                
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": assistant_message
                })
                
                # СОХРАНЕНИЕ ОТВЕТА В ПАМЯТЬ
                self.save_to_long_term_memory({"role": "assistant", "content": assistant_message})
                
                # ФИНАЛЬНОЕ СОХРАНЕНИЕ ПАМЯТИ
                self.save_long_term_memory()
                
                return assistant_message
            else:
                return "Ошибка системы: временная неисправность протокола связи."
                
        except Exception as e:
            return "Временная потеря связи. Протоколы восстановления активированы."
    
    def get_conversation_stats(self):
        """Возвращает статистику диалога"""
        important_memories = len([m for m in self.long_term_memory if m.get('importance', 0) >= 3])
        
        return {
            'total_messages': len(self.conversation_history),
            'long_term_memory_entries': len(self.long_term_memory),
            'important_memories': important_memories,
            'memory_usage': f"{len(self.conversation_history)}/25 сообщений"
        }

# Тестирование
if __name__ == "__main__":
    manager = KyaraCharacterManager()
    
    print("🤖 Система Николь активирована")
    print("🔒 Протоколы безопасности: АКТИВНЫ")
    print("💾 Долговременная память: АКТИВНА")
    print("🚨 Аварийное сохранение: АКТИВНО")
    print("\nКоманды памяти:")
    print("  'запомни что ...' - сохранить в память")
    print("  'покажи память' - показать состояние памяти")
    print("  'очисти память' - очистить все воспоминания")
    print("  'стата' - статистика")
    print("  'выход' - завершение работы\n")
    
    while True:
        try:
            user_input = input("Пользователь: ")
            if user_input.lower() in ['выход', 'exit']:
                print("💾 Сохранение данных...")
                manager.save_long_term_memory()
                break
                
            elif user_input.lower() == 'стата':
                stats = manager.get_conversation_stats()
                print(f"📊 Сообщений: {stats['total_messages']}")
                print(f"🧠 Память: {stats['long_term_memory_entries']} записей")
                print(f"⭐ Важных: {stats['important_memories']}")
                print(f"💾 Использование: {stats['memory_usage']}")
                continue
            
            response = manager.chat(user_input)
            print(f"Николь: {response}\n")
            
        except KeyboardInterrupt:
            print("\n🚨 Аварийное завершение...")
            manager.save_long_term_memory()
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
