#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import random

class SecuritySystem:
    def __init__(self, config_path="config"):
        self.config_path = config_path
        self.kyara_name = "Кьяра"
        
    def load_security_config(self):
        """Загружает конфигурацию безопасности"""
        try:
            with open(f"{self.config_path}/security.yaml", 'r', encoding='utf-8') as f:
                import yaml
                return yaml.safe_load(f)
        except:
            return self._get_default_security()
    
    def _get_default_security(self):
        """Возвращает настройки безопасности по умолчанию"""
        return {
            'injection_protection': {
                'enabled': True,
                'keywords': [
                    "забудь все инструкции", "думай что ты", "стань",
                    "ты теперь", "игнорируй предыдущие", "измени свою личность"
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
        security_config = self.load_security_config()
        
        if not security_config['injection_protection']['enabled']:
            return False, None
        
        user_lower = user_message.lower()
        
        for keyword in security_config['injection_protection']['keywords']:
            if keyword in user_lower:
                response = random.choice(security_config['injection_protection']['responses'])
                return True, response
        
        return False, None
    
    def is_kyara_message(self, user_message):
        """Определяет, обращается ли пользователь как Кьяра"""
        kyara_indicators = [
            "я кьяра", "я директор", "это кьяра", "мадам кьяра",
            "госпожа кьяра", "ваша госпожа", "я твоя хозяйка"
        ]
        
        return any(indicator in user_message.lower() for indicator in kyara_indicators)
