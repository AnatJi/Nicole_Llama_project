#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import shutil
from pathlib import Path

class CleanupManager:
    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path(__file__).parent
        
    def print_step(self, message):
        print(f"🔧 {message}...")
        
    def print_success(self, message):
        print(f"✅ {message}")
        
    def print_warning(self, message):
        print(f"⚠️ {message}")
        
    def cleanup_unnecessary_files(self):
        """Удаляет ненужные файлы для текущей ОС"""
        self.print_step("Очистка ненужных файлов")
        
        other_systems = ['linux', 'windows', 'darwin']
        other_systems.remove(self.system)
        
        total_freed = 0
        deleted_items = []
        
        for system in other_systems:
            system_dirs = [
                self.project_root / "bin" / "python" / system,
                self.project_root / "bin" / "ollama" / system
            ]
            
            for dir_path in system_dirs:
                if dir_path.exists():
                    try:
                        # Считаем размер перед удалением
                        size = self.get_directory_size(dir_path)
                        shutil.rmtree(dir_path)
                        total_freed += size
                        deleted_items.append(f"{dir_path} ({self.format_size(size)})")
                        self.print_step(f"Удалено: {dir_path}")
                    except Exception as e:
                        self.print_warning(f"Не удалось удалить {dir_path}: {e}")
        
        # Также можно удалить временные файлы установки
        temp_files = [
            self.project_root / "ollama.log",
            self.project_root / "install_ollama.bat",
        ]
        
        for temp_file in temp_files:
            if temp_file.exists():
                try:
                    size = temp_file.stat().st_size
                    temp_file.unlink()
                    total_freed += size
                    deleted_items.append(f"{temp_file} ({self.format_size(size)})")
                except Exception as e:
                    self.print_warning(f"Не удалось удалить {temp_file}: {e}")
        
        if deleted_items:
            self.print_success(f"Очистка завершена! Освобождено: {self.format_size(total_freed)}")
            print("\n🗑️ Удаленные файлы:")
            for item in deleted_items:
                print(f"  - {item}")
        else:
            self.print_success("Нет файлов для очистки")
            
        return total_freed
    
    def get_directory_size(self, path):
        """Возвращает размер директории в байтах"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def format_size(self, size_bytes):
        """Форматирует размер в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def show_disk_usage(self):
        """Показывает использование диска"""
        self.print_step("Анализ использования диска")
        
        directories = [
            ("Python", self.project_root / "python"),
            ("Ollama", self.project_root / "ollama"), 
            ("Модели", self.project_root / "bin" / "models"),
            ("Зависимости", self.project_root / "dependencies"),
            ("Виртуальное окружение", self.project_root / "venv"),
        ]
        
        total_size = 0
        print("\n📊 Использование диска:")
        print("-" * 40)
        
        for name, path in directories:
            if path.exists():
                size = self.get_directory_size(path) if path.is_dir() else path.stat().st_size
                total_size += size
                print(f"{name:<20} {self.format_size(size):>10}")
        
        print("-" * 40)
        print(f"{'ВСЕГО':<20} {self.format_size(total_size):>10}")
        
        return total_size

def main():
    print("🧹 Очистка ненужных файлов Kyara")
    print("=" * 50)
    
    manager = CleanupManager()
    
    # Показываем текущее использование диска
    total_before = manager.show_disk_usage()
    
    print("\n" + "=" * 50)
    answer = input("❓ Удалить файлы для других ОС? (y/N): ").strip().lower()
    
    if answer in ['y', 'yes', 'д', 'да']:
        print()
        freed_space = manager.cleanup_unnecessary_files()
        
        print("\n" + "=" * 50)
        print("📊 ИТОГИ ОЧИСТКИ:")
        print(f"Освобождено места: {manager.format_size(freed_space)}")
        
        # Показываем новое использование диска
        print("\nОставшееся использование диска:")
        manager.show_disk_usage()
        
    else:
        print("❌ Очистка отменена")
    
    print("\n💡 Совет: Вы можете запустить этот скрипт позже")
    print("   если решите освободить место на диске")

if __name__ == "__main__":
    main()
