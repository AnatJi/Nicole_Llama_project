#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def check_python():
    print("🔍 Проверка Python...")
    paths_to_check = [
        "python/local/bin/python3",
        "python/local/bin/python", 
        "python/local/python3",
        "python/local/python",
        "venv/bin/python3",
        "venv/bin/python"
    ]
    
    for path in paths_to_check:
        full_path = Path(path)
        if full_path.exists():
            print(f"✅ Найден: {path}")
            try:
                result = subprocess.run([str(full_path), "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   Версия: {result.stdout.strip()}")
                    return str(full_path)
            except:
                pass
                
    print("❌ Python не найден")
    return None

def check_pip(python_path):
    print("🔍 Проверка pip...")
    try:
        result = subprocess.run([python_path, "-m", "pip", "--version"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Pip доступен: {result.stdout.split()[1]}")
            return True
    except:
        pass
        
    print("❌ Pip не доступен")
    return False

def check_dependencies(python_path):
    print("🔍 Проверка зависимостей...")
    dependencies = ["requests", "yaml", "json", "os"]
    
    for dep in dependencies:
        try:
            if dep == "yaml":
                subprocess.run([python_path, "-c", f"import {dep}"], 
                             capture_output=True, check=True)
            else:
                subprocess.run([python_path, "-c", f"import {dep}"], 
                             capture_output=True, check=True)
            print(f"✅ {dep}")
        except:
            print(f"❌ {dep}")
            
def main():
    print("🩺 Диагностика установки Kyara")
    print("=" * 50)
    
    python_path = check_python()
    if python_path:
        check_pip(python_path)
        check_dependencies(python_path)
    
    print("=" * 50)
    print("💡 Если есть проблемы, запустите: python install.py")

if __name__ == "__main__":
    main()
