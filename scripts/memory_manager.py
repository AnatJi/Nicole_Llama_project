#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta

class MemoryManager:
    def __init__(self, data_path="data"):
        self.data_path = data_path
        self.long_term_memory = []
        self.stream_memory = []
        
    def save_conversation(self, conversation, stream_id=None):
        """Сохраняет текущую беседу"""
        if not stream_id:
            stream_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        filename = f"chat_{stream_id}.json"
        filepath = os.path.join(self.data_path, filename)
        
        data = {
            'stream_id': stream_id,
            'timestamp': datetime.now().isoformat(),
            'conversation': conversation,
            'summary': self._generate_summary(conversation)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_previous_streams(self, days=30):
        """Загружает беседы за последние N дней"""
        streams = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file in os.listdir(self.data_path):
            if file.startswith('chat_') and file.endswith('.json'):
                filepath = os.path.join(self.data_path, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    stream_date = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    if stream_date > cutoff_date:
                        streams.append(data)
                except Exception as e:
                    print(f"Ошибка загрузки {file}: {e}")
        
        return sorted(streams, key=lambda x: x['timestamp'])
    
    def _generate_summary(self, conversation):
        """Генерирует краткое содержание беседы"""
        user_messages = [msg['content'] for msg in conversation if msg['role'] == 'user']
        if len(user_messages) > 5:
            return f"Беседа из {len(conversation)} сообщений. Ключевые темы: {', '.join(user_messages[:3])}"
        return f"Короткая беседа из {len(conversation)} сообщений"
    
    def get_memory_context(self):
        """Возвращает контекст из долговременной памяти"""
        recent_streams = self.load_previous_streams(days=7)
        
        if not recent_streams:
            return ""
        
        context = "ПРЕДЫДУЩИЕ ВЗАИМОДЕЙСТВИЯ:\n"
        for stream in recent_streams[-3:]:  # Последние 3 стрима
            context += f"- {stream['summary']}\n"
        
        return context
