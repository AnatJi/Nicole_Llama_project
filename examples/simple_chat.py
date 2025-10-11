#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from llama_manager import LlamaCharacterManager

def main():
    print("Простой чат с Николь")
    manager = LlamaCharacterManager()
    
    while True:
        user_input = input("Ты: ")
        if user_input.lower() in ['выход', 'exit']:
            break
            
        response = manager.chat(user_input)
        print("Николь: {}".format(response))

if __name__ == "__main__":
    main()
