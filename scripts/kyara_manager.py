#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import os
import random
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
        
        # Загружаем долговременную память
        self.load_long_term_memory()
        
        # Счетчики для автосохранения
        self.message_count = 0
        
    def add_system_message(self, message):
        self.conversation_history.append({"role": "system", "content": message})
    
    def detect_complex_task(self, user_message):
        """Определяет сложные задачи для пошагового решения"""
        task_indicators = ['задача', 'реши', 'логическ', 'головоломк', 'посчитай']
        return any(indicator in user_message.lower() for indicator in task_indicators)
    
    def optimize_context(self):
        """Оптимизирует контекст для экономии памяти"""
        if len(self.conversation_history) > 20:
            self.conversation_history = self.context_optimizer.compress_conversation(
                self.conversation_history
            )
    
    def save_to_long_term_memory(self, message):
        """Сохраняет важные сообщения в долговременную память"""
        if self.context_optimizer.should_save_to_long_term(message, self.conversation_history):
            memory_entry = {
                'timestamp': self._get_timestamp(),
                'content': message['content'],
                'role': message['role'],
                'importance': self.context_optimizer.calculate_importance(message)
            }
            self.long_term_memory.append(memory_entry)
    
    def load_long_term_memory(self):
        """Загружает долговременную память из файла"""
        memory_file = os.path.join("data", "long_term_memory", "memory.json")
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    self.long_term_memory = json.load(f)
            except:
                self.long_term_memory = []
    
    def save_long_term_memory(self):
        """Сохраняет долговременную память в файл"""
        memory_dir = os.path.join("data", "long_term_memory")
        os.makedirs(memory_dir, exist_ok=True)
        memory_file = os.path.join(memory_dir, "memory.json")
        
        # Ограничиваем размер памяти (последние 1000 записей)
        if len(self.long_term_memory) > 1000:
            self.long_term_memory = self.long_term_memory[-1000:]
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()
    
    def chat(self, user_message):
        # АВАРИЙНОЕ СОХРАНЕНИЕ каждые 50 сообщений
        self.message_count += 1
        if self.message_count % 50 == 0:
            self.emergency_save.save_emergency_state({
                'conversation_history': self.conversation_history[-20:],
                'long_term_memory': self.long_term_memory[-100:]
            })
        
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
                self.save_long_term_memory()
                
                return assistant_message
            else:
                return "Ошибка системы: временная неисправность протокола связи."
                
        except Exception as e:
            return "Временная потеря связи. Протоколы восстановления активированы."
    
    def get_conversation_stats(self):
        """Возвращает статистику диалога"""
        return {
            'total_messages': len(self.conversation_history),
            'long_term_memory_entries': len(self.long_term_memory),
            'memory_usage': f"{len(self.conversation_history)}/30 сообщений"
        }

# Тестирование
if __name__ == "__main__":
    manager = KyaraCharacterManager()
    
    print("🤖 Система Николь активирована")
    print("🔒 Протоколы безопасности: АКТИВНЫ")
    print("💾 Долговременная память: АКТИВНА")
    print("🚨 Аварийное сохранение: АКТИВНО")
    
    while True:
        try:
            user_input = input("Пользователь: ")
            if user_input.lower() in ['выход', 'exit']:
                break
                
            response = manager.chat(user_input)
            print(f"Николь: {response}")
            
        except KeyboardInterrupt:
            print("\n💾 Выполняю аварийное сохранение...")
            break
