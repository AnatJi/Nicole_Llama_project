#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from llama_manager import LlamaCharacterManager

class MemoryManager(LlamaCharacterManager):
    def __init__(self, config_path="config", data_path="data"):
        super().__init__(config_path)
        self.data_path = data_path
        self.stream_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создаем папки если нет
        os.makedirs(os.path.join(data_path, "stream_memory"), exist_ok=True)
        
    def save_conversation(self, filename=None):
        if not filename:
            filename = "chat_{}.json".format(self.stream_id)
            
        filepath = os.path.join(self.data_path, filename)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'stream_id': self.stream_id,
            'conversation': self.conversation_history,
            'stats': self.get_conversation_stats()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return filepath
    
    def load_conversation(self, filename):
        filepath = os.path.join(self.data_path, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Загружаем историю, но сохраняем системный промпт
            system_msg = self.conversation_history[0]  # Сохраняем системное сообщение
            self.conversation_history = [system_msg] + data['conversation'][1:]
            
            return True
        except Exception as e:
            print("Ошибка загрузки: {}".format(e))
            return False
    
    def get_previous_streams(self):
        memory_dir = os.path.join(self.data_path, "stream_memory")
        streams = []
        
        if os.path.exists(memory_dir):
            for file in os.listdir(memory_dir):
                if file.endswith('.json'):
                    streams.append(file)
                    
        return sorted(streams)
    
    def auto_save(self):
        """Авто-сохранение каждые N сообщений"""
        stats = self.get_conversation_stats()
        if stats['total_messages'] % self.settings['memory']['save_interval'] == 0:
            filename = "stream_memory/auto_save_{}.json".format(self.stream_id)
            self.save_conversation(filename)
            print("💾 Авто-сохранение выполнено")
