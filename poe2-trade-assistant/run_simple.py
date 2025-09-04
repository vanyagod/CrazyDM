#!/usr/bin/env python3
"""
Упрощенный скрипт запуска PoE2 Trade Assistant для Windows
Работает с минимальными зависимостями
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Упрощенная точка входа"""
    print("⚔️ PoE2 Trade Assistant")
    print("🎓 Образовательный проект для анализа торговых данных")
    print()
    print("⚠️ ВАЖНО: Этот проект создан исключительно в образовательных целях.")
    print("   Автоматическая торговля может нарушать правила игры!")
    print()
    
    # Проверяем доступность модулей
    missing_modules = []
    
    try:
        import requests
    except ImportError:
        missing_modules.append("requests")
    
    try:
        import tkinter
        gui_available = True
    except ImportError:
        gui_available = False
        print("⚠️ tkinter недоступен - GUI не будет работать")
    
    if missing_modules:
        print(f"❌ Отсутствуют модули: {', '.join(missing_modules)}")
        print("Установите их командой:")
        for module in missing_modules:
            print(f"   python -m pip install {module}")
        print()
        print("Или запустите демо-версию: python demo.py")
        return
    
    # Определяем режим запуска
    if len(sys.argv) > 1:
        if sys.argv[1] == "gui" and gui_available:
            try:
                from ui.main_window import MainWindow
                from config.settings import Settings
                
                settings = Settings()
                app = MainWindow(settings)
                app.run()
            except ImportError as e:
                print(f"❌ Ошибка импорта: {e}")
                print("Установите недостающие зависимости:")
                print("   python -m pip install pydantic")
        
        elif sys.argv[1] == "demo":
            # Запуск демо
            import demo
            demo.main()
        
        else:
            print("Доступные команды:")
            print("  python run_simple.py gui   - запуск GUI (если доступен)")
            print("  python run_simple.py demo  - запуск демонстрации")
            print("  python demo.py             - прямой запуск демо")
    
    else:
        print("Выберите режим запуска:")
        print("  1. Демонстрация (работает всегда)")
        print("  2. GUI интерфейс (требует дополнительные модули)")
        print()
        
        choice = input("Введите номер (1 или 2): ").strip()
        
        if choice == "1":
            exec(open("demo.py").read())
        elif choice == "2" and gui_available:
            try:
                from ui.main_window import MainWindow
                from config.settings import Settings
                
                settings = Settings()
                app = MainWindow(settings)
                app.run()
            except ImportError as e:
                print(f"❌ Ошибка: {e}")
                print("Запустите демо-версию: python demo.py")
        else:
            print("Запускаем демо-версию...")
            exec(open("demo.py").read())

if __name__ == "__main__":
    main()