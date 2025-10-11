#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime

class StreamHelper:
    def __init__(self, data_path="data"):
        self.data_path = data_path
        
    def format_stream_stats(self, stats):
        return """
📊 СТАТИСТИКА СТРИМА:
├── Сообщений: {}
├── Зрителей: {}
├── Николь: {}
└── Символов: {}
        """.format(
            stats['total_messages'],
            stats['user_messages'], 
            stats['assistant_messages'],
            stats['total_characters']
        )
    
    def get_stream_duration(self, start_time):
        duration = datetime.now() - start_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return "{}ч {}м".format(hours, minutes)
