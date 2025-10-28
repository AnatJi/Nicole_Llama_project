#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

class MemoryManager:
    def __init__(self, data_path="data"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger("NicoleMemory")
        self.long_term_memory = []
        self.stream_memory = []
        
    def save_conversation(self, conversation, stream_id=None):
        """Сохраняет текущую беседу с обработкой ошибок"""
        try:
            if not stream_id:
                stream_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                
            filename = f"chat_{stream_id}.json"
            filepath = self.data_path / filename
            
            data = {
                'stream_id': stream_id,
                'timestamp': datetime.now().isoformat(),
                'conversation': conversation,
                'summary': self._generate_summary(conversation),
                'message_count': len(conversation)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Беседа сохранена: {filename} ({len(conversation)} сообщений)")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения беседы: {e}")
            return None
