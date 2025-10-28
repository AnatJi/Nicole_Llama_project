#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import yaml
import os
import sys
import logging
from pathlib import Path

class ConfigLoader:
    def __init__(self, config_path="config"):
        # Кроссплатформенные пути
        self.base_dir = Path(__file__).parent.parent
        self.config_path = self.base_dir / config_path
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("NicoleConfig")
    
    def _load_yaml_safe(self, filename):
        """Безопасная загрузка YAML файла с обработкой ошибок"""
        file_path = self.config_path / filename
        
        if not file_path.exists():
            self.logger.error(f"Конфиг файл не найден: {file_path}")
            return {}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            self.logger.error(f"Ошибка YAML в файле {filename}: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Ошибка чтения {filename}: {e}")
            return {}
    
    def load_character(self):
        return self._load_yaml_safe("character.yaml")
    
    def load_backstory(self):
        return self._load_yaml_safe("backstory.yaml")
    
    def load_settings(self):
        return self._load_yaml_safe("settings.yaml")
    
    def load_security(self):
        return self._load_yaml_safe("security.yaml")
    
    def build_system_prompt(self):
        """Собирает финальный системный промпт из всех конфигов"""
        character = self.load_character()
        backstory = self.load_backstory()
        security = self.load_security()
        
        if not all([character, backstory, security]):
            self.logger.error("Не удалось загрузить конфигурации")
            return "Активирован аварийный режим. Системные конфигурации недоступны."
        
        prompt_parts = [
            f"ТЫ - {character.get('name', 'Николь')}. {character.get('role', 'Дворецкий и телохранитель')}.",
            "",
            "НЕПРЕМЕННЫЕ ФАКТЫ:",
            f"- Ты {character.get('identity', {}).get('type', 'робот-андроид')}",
            f"- Твоя госпожа - {backstory.get('relationships', {}).get('kyara', {}).get('role', 'Кьяра')}",
            f"- Ты абсолютно предан {backstory.get('background', {}).get('owner', 'Кьяре')}",
        ]
        
        # Добавляем функционирующие возможности
        capabilities = character.get('current_capabilities', {}).get('functioning', [])
        if capabilities:
            prompt_parts.append(f"- Твои функции: {', '.join(capabilities)}")
        
        # Добавляем характер
        traits = character.get('personality', {}).get('main_traits', [])
        if traits:
            prompt_parts.extend(["", "ХАРАКТЕР:", ', '.join(traits)])
        
        # Добавляем манеры
        mannerisms = character.get('personality', {}).get('mannerisms', [])
        if mannerisms:
            prompt_parts.extend(["", "МАНЕРА ОБЩЕНИЯ:"])
            prompt_parts.extend([f"- {manner}" for manner in mannerisms])
        
        # Добавляем правила
        rules = character.get('rules', [])
        if rules:
            prompt_parts.extend(["", "ЖЕСТКИЕ ПРАВИЛА:"])
            prompt_parts.extend([f"- {rule}" for rule in rules])
        
        prompt_parts.extend([
            "",
            "ОБЩАЙСЯ В СООТВЕТСТВИИ С РОЛЬЮ:"
        ])
        
        return "\n".join(prompt_parts)
