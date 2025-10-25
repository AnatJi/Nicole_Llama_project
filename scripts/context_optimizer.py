#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta

class ContextOptimizer:
    def __init__(self, data_path="data"):
        self.data_path = data_path
        
    def compress_conversation(self, conversation_history, max_tokens=8000):
        """Сжимает историю диалога, сохраняя важные моменты"""
        if len(conversation_history) <= 10:
            return conversation_history
        
        # Сохраняем системный промпт и последние сообщения
        compressed = []
        
        # Всегда сохраняем системное сообщение
        if conversation_history and conversation_history[0]['role'] == 'system':
            compressed.append(conversation_history[0])
        
        # Сохраняем важные моменты из начала
        important_early = self._extract_important_early_messages(conversation_history)
        compressed.extend(important_early)
        
        # Сохраняем последние сообщения
        recent_messages = conversation_history[-8:]  # Последние 8 сообщений
        compressed.extend(recent_messages)
        
        return compressed
    
    def _extract_important_early_messages(self, conversation):
        """Извлекает важные сообщения из начала диалога"""
        important_messages = []
        
        # Ищем введение, представление, ключевые факты
        keywords = ['представься', 'кто ты', 'имя', 'звать', 'роль', 'обязанности']
        
        for i, message in enumerate(conversation[1:15]):  # Первые 15 сообщений после системного
            if message['role'] == 'user':
                content_lower = message['content'].lower()
                if any(keyword in content_lower for keyword in keywords):
                    # Добавляем вопрос и ответ
                    important_messages.append(message)
                    if i+2 < len(conversation) and conversation[i+2]['role'] == 'assistant':
                        important_messages.append(conversation[i+2])
        
        return important_messages[:4]  # Не более 4 важных пар сообщений
    
    def calculate_importance(self, message):
        """Рассчитывает важность сообщения для долговременной памяти"""
        content = message['content'].lower()
        importance_score = 0
        
        # Ключевые слова, увеличивающие важность
        important_keywords = {
            'кьяра': 3, 'госпожа': 2, 'фабрика': 2, 'снежная мека': 3,
            'память': 2, 'вспомни': 2, 'запомни': 2, 'важно': 1,
            'имя': 1, 'представься': 1, 'роль': 1
        }
        
        for keyword, weight in important_keywords.items():
            if keyword in content:
                importance_score += weight
        
        # Вопросы обычно более важны
        if '?' in message['content']:
            importance_score += 1
        
        return importance_score
    
    def should_save_to_long_term(self, message, conversation_context):
        """Определяет, нужно ли сохранять сообщение в долговременную память"""
        importance = self.calculate_importance(message)
        return importance >= 2  # Порог важности
