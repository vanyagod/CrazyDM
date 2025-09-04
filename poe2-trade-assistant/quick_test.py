#!/usr/bin/env python3
"""
Быстрый тест для проверки работоспособности
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Тест импортов"""
    print("🔍 Тестируем импорты...")
    
    try:
        from config.settings import Settings
        print("✅ Settings импортирован")
    except Exception as e:
        print(f"❌ Settings: {e}")
        return False
    
    try:
        from api.poe2_simple import SimplePoE2API
        print("✅ SimplePoE2API импортирован")
    except Exception as e:
        print(f"❌ SimplePoE2API: {e}")
        return False
    
    try:
        from ui.main_window import MainWindow
        print("✅ MainWindow импортирован")
    except Exception as e:
        print(f"❌ MainWindow: {e}")
        return False
    
    return True

def test_settings():
    """Тест настроек"""
    print("\n⚙️ Тестируем настройки...")
    
    try:
        from config.settings import Settings
        settings = Settings()
        print(f"✅ API URL: {settings.poe_api_base_url}")
        print(f"✅ League: {settings.league}")
        print(f"✅ Request delay: {settings.request_delay}")
        return True
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False

def test_api():
    """Тест API"""
    print("\n🌐 Тестируем API...")
    
    try:
        from config.settings import Settings
        from api.poe2_simple import SimplePoE2API
        
        settings = Settings()
        api = SimplePoE2API(settings)
        
        # Тест демо данных
        demo_data = api._get_demo_data()
        print(f"✅ Демо данных: {len(demo_data)} предметов")
        
        for item in demo_data[:3]:
            print(f"   • {item['name']} - {item['price']} {item['currency']}")
        
        return True
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

def test_gui_creation():
    """Тест создания GUI (без запуска)"""
    print("\n🖥️ Тестируем создание GUI...")
    
    try:
        from config.settings import Settings
        from ui.main_window import MainWindow
        
        settings = Settings()
        
        # Создаем окно но не запускаем mainloop
        app = MainWindow(settings)
        print("✅ GUI создан успешно")
        
        # Проверяем основные компоненты
        if hasattr(app, 'root'):
            print("✅ Главное окно создано")
        if hasattr(app, 'api'):
            print("✅ API клиент подключен")
        if hasattr(app, 'item_filter'):
            print("✅ Система фильтров готова")
        
        # Закрываем окно
        app.root.destroy()
        
        return True
    except Exception as e:
        print(f"❌ GUI error: {e}")
        return False

def main():
    """Главная функция теста"""
    print("🧪 PoE2 Trade Assistant - Быстрый тест")
    print("=" * 50)
    
    tests = [
        ("Импорты", test_imports),
        ("Настройки", test_settings), 
        ("API", test_api),
        ("GUI", test_gui_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: ПРОЙДЕН")
            else:
                print(f"❌ {test_name}: ПРОВАЛЕН")
        except Exception as e:
            print(f"❌ {test_name}: ОШИБКА - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Приложение готово к работе.")
        print("\nДля запуска используйте:")
        print("  python run.py gui")
    else:
        print("⚠️ Некоторые тесты провалены. Проверьте ошибки выше.")
        print("\nДля демо версии используйте:")
        print("  python demo.py")

if __name__ == "__main__":
    main()