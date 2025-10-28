#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

class ContextOptimizer:
    def __init__(self, data_path="data"):
        self.data_path = Path(data_path) if data_path else None
        self.logger = logging.getLogger("NicoleContext")
        self.logger.info("🔧 Инициализирован оптимизатор контекста")
        
    def compress_conversation(self, conversation_history, max_tokens=8000):
        """Сжимает историю диалога, сохраняя важные моменты"""
        try:
            if len(conversation_history) <= 10:
                self.logger.debug("Контекст не требует сжатия (<10 сообщений)")
                return conversation_history
            
            original_count = len(conversation_history)
            compressed = []
            
            # Всегда сохраняем системное сообщение
            if conversation_history and conversation_history[0]['role'] == 'system':
                compressed.append(conversation_history[0])
                self.logger.debug("Сохранено системное сообщение")
            
            # Сохраняем важные моменты из начала
            important_early = self._extract_important_early_messages(conversation_history)
            compressed.extend(important_early)
            if important_early:
                self.logger.debug(f"Сохранено {len(important_early)} важных ранних сообщений")
            
            # Сохраняем последние сообщения
            recent_count = min(8, len(conversation_history) - len(compressed))
            recent_messages = conversation_history[-recent_count:]
            compressed.extend(recent_messages)
            self.logger.debug(f"Сохранено {len(recent_messages)} последних сообщений")
            
            final_count = len(compressed)
            compression_ratio = (original_count - final_count) / original_count * 100
            self.logger.info(f"🔧 Контекст сжат: {original_count} → {final_count} сообщений ({compression_ratio:.1f}% сжатия)")
            
            return compressed
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сжатия контекста: {e}")
            # Возвращаем безопасное количество сообщений
            safe_slice = conversation_history[-15:] if len(conversation_history) > 15 else conversation_history
            self.logger.warning(f"Возвращен безопасный срез: {len(safe_slice)} сообщений")
            return safe_slice
    
    def _extract_important_early_messages(self, conversation):
        """Извлекает важные сообщения из начала диалога"""
        important_messages = []
        
        try:
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
                        self.logger.debug(f"Найдено важное сообщение: {content_lower[:30]}...")
            
            self.logger.debug(f"Извлечено {len(important_messages)} важных ранних сообщений")
            return important_messages[:4]  # Не более 4 важных пар сообщений
            
        except Exception as e:
            self.logger.error(f"Ошибка извлечения важных сообщений: {e}")
            return []
    
    def calculate_importance(self, message):
        """Рассчитывает важность сообщения для долговременной памяти"""
        try:
            content = message['content'].lower()
            importance_score = 0
            
            # Ключевые слова, увеличивающие важность
            important_keywords = {
                'кьяра': 3, 'госпожа': 2, 'фабрика': 2, 'снежная мека': 3,
                'память': 2, 'вспомни': 2, 'запомни': 2, 'важно': 1,
                'имя': 1, 'представься': 1, 'роль': 1, 'директор': 2
            }
            
            for keyword, weight in important_keywords.items():
                if keyword in content:
                    importance_score += weight
                    self.logger.debug(f"Ключевое слово '{keyword}' +{weight} к важности")
            
            # Вопросы обычно более важны
            if '?' in message['content']:
                importance_score += 1
                self.logger.debug("Обнаружен вопрос +1 к важности")
            
            self.logger.debug(f"Рассчитана важность {importance_score} для: {content[:30]}...")
            return importance_score
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета важности: {e}")
            return 0
    
    def should_save_to_long_term(self, message, conversation_context):
        """Определяет, нужно ли сохранять сообщение в долговременную память"""
        try:
            importance = self.calculate_importance(message)
            should_save = importance >= 2  # Порог важности
            
            if should_save:
                self.logger.debug(f"Сообщение важно для сохранения (важность: {importance})")
            else:
                self.logger.debug(f"Сообщение не требует сохранения (важность: {importance})")
            
            return should_save
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки сохранения: {e}")
            return False

# Тестирование модуля
if __name__ == "__main__":
    # Настройка логирования для тестов
    logging.basicConfig(level=logging.DEBUG)
    
    optimizer = ContextOptimizer()
    
    # Тестовые данные
    test_conversation = [
        {"role": "system", "content": "Ты Николь, робот-дворецкий"},
        {"role": "user", "content": "Привет! Как тебя зовут?"},
        {"role": "assistant", "content": "Меня зовут Николь."},
        {"role": "user", "content": "Расскажи о госпоже Кьяре"},
        {"role": "assistant", "content": "Кьяра - моя госпожа, директор фабрики."},
        # ... больше тестовых сообщений
    ] * 5  # Умножаем чтобы было больше сообщений
    
    print("🧪 Тест оптимизатора контекста...")
    compressed = optimizer.compress_conversation(test_conversation)
    print(f"✅ Результат: {len(test_conversation)} → {len(compressed)} сообщений")
