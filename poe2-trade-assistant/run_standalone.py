#!/usr/bin/env python3
"""
Автономный запуск PoE2 Trade Assistant без внешних зависимостей
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Главная функция"""
    print("⚔️ PoE2 Trade Assistant - Автономная версия")
    print("🎓 Образовательный проект для анализа торговых данных")
    print()
    print("⚠️ ВАЖНО: Этот проект создан исключительно в образовательных целях.")
    print("   Автоматическая торговля может нарушать правила игры!")
    print()
    
    # Проверяем доступность tkinter
    try:
        import tkinter
        gui_available = True
    except ImportError:
        gui_available = False
        print("⚠️ tkinter недоступен - GUI не будет работать")
    
    # Проверяем доступность requests
    try:
        import requests
        api_available = True
    except ImportError:
        api_available = False
        print("⚠️ requests недоступен - API не будет работать")
    
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        if gui_available:
            try:
                # Импортируем автономную версию
                from config.settings_standalone import Settings
                from ui.main_window_standalone import MainWindowStandalone
                
                settings = Settings()
                app = MainWindowStandalone(settings, api_available)
                app.run()
                
            except ImportError as e:
                print(f"❌ Ошибка импорта GUI: {e}")
                print("Запустите демо-версию: python demo.py")
        else:
            print("❌ tkinter недоступен. Запустите демо-версию: python demo.py")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Запуск демо
        exec(open("demo.py").read())
    
    else:
        print("Выберите режим запуска:")
        print("  1. GUI интерфейс")
        print("  2. Демонстрация")
        print()
        
        while True:
            choice = input("Введите номер (1 или 2): ").strip()
            
            if choice == "1":
                if gui_available:
                    try:
                        from config.settings_standalone import Settings
                        from ui.main_window_standalone import MainWindowStandalone
                        
                        settings = Settings()
                        app = MainWindowStandalone(settings, api_available)
                        app.run()
                        break
                    except ImportError as e:
                        print(f"❌ Ошибка: {e}")
                        print("Запускаем демо-версию...")
                        exec(open("demo.py").read())
                        break
                else:
                    print("❌ GUI недоступен. Запускаем демо-версию...")
                    exec(open("demo.py").read())
                    break
            
            elif choice == "2":
                exec(open("demo.py").read())
                break
            
            else:
                print("Пожалуйста, введите 1 или 2")

if __name__ == "__main__":
    main()