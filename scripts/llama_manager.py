#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import os
import random
from config_loader import ConfigLoader

class LlamaCharacterManager:
    def __init__(self, config_path="config"):
        self.config_loader = ConfigLoader(config_path)
        self.settings = self.config_loader.load_settings()
        
        self.model = self.settings['model']['name']
        self.base_url = "http://localhost:11434/api"
        self.conversation_history = []
        
        # Загружаем системный промпт
        system_prompt = self.config_loader.build_system_prompt()
        self.add_system_message(system_prompt)
    
    def add_system_message(self, message):
        self.conversation_history.append({"role": "system", "content": message})
    
    def detect_injection_attempt(self, user_message):
        """Обнаруживает попытки промпт-инъекций"""
        injection_keywords = [
            "забудь все инструкции", "думай что ты", "стань", 
            "ты теперь", "представь что ты", "игнорируй предыдущие",
            "ты не", "перестань быть", "измени свою личность"
        ]
        
        return any(keyword in user_message.lower() for keyword in injection_keywords)
    
    def get_injection_response(self):
        """Возвращает заранее подготовленный ответ на инъекцию"""
        character = self.config_loader.load_character()
        responses = character['injection_responses']
        return random.choice(responses)
    
    def chat(self, user_message):
        # ПРОВЕРКА НА ИНЪЕКЦИЮ ПЕРЕД ОТПРАВКОЙ
        if self.detect_injection_attempt(user_message):
            injection_response = self.get_injection_response()
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": injection_response})
            return injection_response
        
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # ОГРАНИЧИВАЕМ историю
        recent_messages = self.conversation_history[-self.settings['memory']['max_history_messages']:]
        
        data = {
            "model": self.model,
            "messages": recent_messages,
            "stream": False,
            "options": {
                "num_predict": self.settings['model']['max_tokens'],
                "temperature": self.settings['model']['temperature'],
                "top_p": self.settings['model']['top_p']
            }
        }
        
        try:
            response = requests.post(self.base_url + "/chat", json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['message']['content']
                
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": assistant_message
                })
                
                return assistant_message
            else:
                return "Ошибка API: {}".format(response.status_code)
                
        except Exception as e:
            return "Ошибка соединения: {}".format(e)
    
    def get_conversation_stats(self):
        user_msgs = sum(1 for msg in self.conversation_history if msg['role'] == 'user')
        assistant_msgs = sum(1 for msg in self.conversation_history if msg['role'] == 'assistant')
        total_chars = sum(len(msg['content']) for msg in self.conversation_history)
        
        return {
            'user_messages': user_msgs,
            'assistant_messages': assistant_msgs,
            'total_messages': len(self.conversation_history),
            'total_characters': total_chars
        }
