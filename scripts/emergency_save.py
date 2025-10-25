#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import signal
import sys
from datetime import datetime

class EmergencySave:
    def __init__(self, data_path="data"):
        self.data_path = data_path
        self.emergency_dir = os.path.join(data_path, "emergency_backup")
        os.makedirs(self.emergency_dir, exist_ok=True)
        
    def setup_emergency_handlers(self):
        """Устанавливает обработчики аварийного завершения"""
        signal.signal(signal.SIGINT, self._emergency_save_handler)
        signal.signal(signal.SIGTERM, self._emergency_save_handler)
        
    def _emergency_save_handler(self, signum, frame):
        """Обработчик аварийного сохранения"""
        print(f"\n🚨 Обнаружен сигнал {signum}. Выполняю аварийное сохранение...")
        
        # Здесь будет вызываться метод сохранения из memory_manager
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_emergency")
        backup_file = os.path.join(self.emergency_dir, f"{timestamp}.json")
        
        # Сохраняем минимальную информацию для восстановления
        emergency_data = {
            'timestamp': datetime.now().isoformat(),
            'signal': signum,
            'last_messages': []  # Будет заполнено извне
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(emergency_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Аварийное сохранение завершено: {backup_file}")
        sys.exit(1)
    
    def save_emergency_state(self, conversation_state):
        """Сохраняет текущее состояние для аварийного восстановления"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.emergency_dir, f"{timestamp}.json")
        
        emergency_data = {
            'timestamp': datetime.now().isoformat(),
            'conversation_state': conversation_state,
            'message_count': len(conversation_state.get('conversation_history', []))
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(emergency_data, f, ensure_ascii=False, indent=2)
        
        return backup_file
