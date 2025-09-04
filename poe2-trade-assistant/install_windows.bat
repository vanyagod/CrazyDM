@echo off
echo ========================================
echo  PoE2 Trade Assistant - Windows Setup
echo ========================================
echo.

echo Проверка Python...
python --version
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo Скачайте и установите Python с python.org
    pause
    exit /b 1
)

echo.
echo Обновление pip...
python -m pip install --upgrade pip

echo.
echo Установка основных зависимостей...
python -m pip install requests aiohttp

echo.
echo Установка pydantic и настроек...
python -m pip install "pydantic>=2.5.0" pydantic-settings python-dotenv

echo.
echo Установка CLI и UI компонентов...
python -m pip install typer rich

echo.
echo Установка дополнительных компонентов...
python -m pip install schedule

echo.
echo Проверка установки...
python -c "import requests, aiohttp, pydantic, typer, rich; print('✅ Все основные модули установлены!')"

if %errorlevel% neq 0 (
    echo ❌ Ошибка при проверке модулей
    pause
    exit /b 1
)

echo.
echo ✅ Установка завершена!
echo.
echo Теперь вы можете запустить:
echo   python run.py gui     - Графический интерфейс
echo   python run.py search "item name"  - Поиск через командную строку
echo   python demo.py        - Демонстрация
echo.
pause