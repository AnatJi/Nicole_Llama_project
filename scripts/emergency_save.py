#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
import logging

class EmergencySave:
    def __init__(self, data_path="data"):
        self.data_path = Path(data_path)
        self.emergency_dir = self.data_path / "emergency_backup"
        self.emergency_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("NicoleEmergency")
        
    def setup_emergency_handlers(self):
        """Устанавливает обработчики аварийного завершения"""
        try:
            signal.signal(signal.SIGINT, self._emergency_save_handler)
            signal.signal(signal.SIGTERM, self._emergency_save_handler)
            self.logger.info("Аварийные обработчики установлены")
        except Exception as e:
            self.logger.error(f"Ошибка установки обработчиков: {e}")
        
    def _emergency_save_handler(self, signum, frame):
        """Обработчик аварийного сохранения"""
        self.logger.critical(f"Получен сигнал {signum}, выполняется аварийное сохранение")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_emergency")
            backup_file = self.emergency_dir / f"{timestamp}.json"
            
            emergency_data = {
                'timestamp': datetime.now().isoformat(),
                'signal': signum,
                'last_messages': [],
                'system': 'Nicole Emergency Save'
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(emergency_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Аварийное сохранение завершено: {backup_file}")
        except Exception as e:
            self.logger.error(f"Ошибка аварийного сохранения: {e}")
        
        sys.exit(1)
