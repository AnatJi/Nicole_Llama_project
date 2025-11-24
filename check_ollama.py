#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

def check_ollama_installation():
    print("🔍 Проверка установки Ollama...")
    
    # Проверяем наличие бинарника
    ollama_paths = [
        Path("ollama/ollama"),
        Path("ollama/bin/ollama"),
    ]
    
    ollama_binary = None
    for path in ollama_paths:
        if path.exists():
            ollama_binary = path
            print(f"✅ Найден бинарник Ollama: {path}")
            break
    
    if not ollama_binary:
        print("❌ Бинарник Ollama не найден")
        return False
    
    # Проверяем права доступа
    import os
    if os.access(ollama_binary, os.X_OK):
        print("✅ Бинарник исполняемый")
    else:
        print("❌ Бинарник не исполняемый, исправляем...")
        os.chmod(ollama_binary, 0o755)
        print("✅ Права исправлены")
    
    # Проверяем запущен ли Ollama
    print("\n🔍 Проверка запуска Ollama...")
    try:
        # Проверяем процессы
        result = subprocess.run(['pgrep', '-f', 'ollama'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama процесс запущен")
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"   PID: {pid}")
        else:
            print("❌ Ollama процесс не найден")
    except Exception as e:
        print(f"⚠️ Ошибка проверки процессов: {e}")
    
    # Проверяем доступность API
    print("\n🔍 Проверка API Ollama...")
    try:
        result = subprocess.run([
            'curl', '-s', 'http://localhost:11434/api/tags'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ API Ollama доступен")
            try:
                import json
                data = json.loads(result.stdout)
                if 'models' in data:
                    print(f"✅ Найдено моделей: {len(data['models'])}")
                    for model in data['models']:
                        print(f"   - {model.get('name', 'Unknown')}")
            except:
                print("📄 Ответ API:", result.stdout[:200])
        else:
            print("❌ API не доступен")
            print("Ошибка:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при проверке API")
    except Exception as e:
        print(f"❌ Ошибка проверки API: {e}")
    
    # Проверяем можем ли запустить Ollama вручную
    print("\n🔍 Попытка запуска Ollama...")
    try:
        # Запускаем в фоне
        process = subprocess.Popen([
            str(ollama_binary), 'serve'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        
        import time
        time.sleep(3)
        
        # Проверяем процесс
        if process.poll() is None:
            print("✅ Ollama запущен успешно")
            print(f"   PID: {process.pid}")
            
            # Даем время на инициализацию
            time.sleep(2)
            
            # Проверяем API
            result = subprocess.run([
                'curl', '-s', 'http://localhost:11434/api/tags'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ API отвечает после запуска")
            else:
                print("❌ API не отвечает после запуска")
            
            # Завершаем процесс
            process.terminate()
            process.wait()
            print("✅ Процесс Ollama завершен")
        else:
            stdout, stderr = process.communicate()
            print("❌ Ollama завершился сразу")
            print("STDOUT:", stdout.decode()[:200])
            print("STDERR:", stderr.decode()[:200])
            
    except Exception as e:
        print(f"❌ Ошибка запуска Ollama: {e}")

def main():
    print("🩺 Диагностика Ollama")
    print("=" * 50)
    check_ollama_installation()
    print("=" * 50)
    print("\n💡 Если есть проблемы:")
    print("1. Запустите вручную: ./ollama/ollama serve")
    print("2. Проверьте логи: tail -f ollama.log")
    print("3. Переустановите: python install.py")

if __name__ == "__main__":
    main()
