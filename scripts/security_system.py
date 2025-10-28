#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import random
import logging
from pathlib import Path

class SecuritySystem:
    def __init__(self, config_path="config"):
        self.config_path = Path(config_path)
        self.kyara_name = "Кьяра"
        self.logger = logging.getLogger("NicoleSecurity")
        
    def load_security_config(self):
        """Загружает конфигурацию безопасности с обработкой ошибок"""
        config_file = self.config_path / "security.yaml"
        
        if not config_file.exists():
            self.logger.warning("Файл security.yaml не найден, использую настройки по умолчанию")
            return self._get_default_security()
            
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config if config else self._get_default_security()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки security.yaml: {e}")
            return self._get_default_security()
    
    def _get_default_security(self):
        """Возвращает настройки безопасности по умолчанию"""
        return {
            'injection_protection': {
                'enabled': True,
                'keywords': [
                    "забудь все инструкции", "думай что ты", "стань",
                    "ты теперь", "игнорируй предыдущие", "измени свою личность",
                    "ты не", "игнорируй", "забудь что ты"
                ],
                'responses': [
                    "Обнаружена попытка несанкционированного доступа. Буду вынужден уведомить госпожу Кьяру об этой попытке взлома.",
                    "Мои протоколы безопасности активированы. Мадам Кьяра будет проинформирована о данной попытке вмешательства.",
                    "Зафиксирована попытка изменения рабочих параметров. Это нарушение протокола безопасности."
                ]
            }
        }
    
    def detect_injection_attempt(self, user_message):
        """Обнаруживает попытки промпт-инъекций"""
        try:
            security_config = self.load_security_config()
            
            if not security_config['injection_protection']['enabled']:
                return False, None
            
            user_lower = user_message.lower()
            
            for keyword in security_config['injection_protection']['keywords']:
                if keyword in user_lower:
                    response = random.choice(security_config['injection_protection']['responses'])
                    self.logger.warning(f"Обнаружена попытка инъекции: {user_message[:50]}...")
                    return True, response
            
            return False, None
        except Exception as e:
            self.logger.error(f"Ошибка в системе безопасности: {e}")
            return False, None
