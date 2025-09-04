#!/usr/bin/env python3
"""
PoE2 Trade Assistant - Главный модуль
Образовательный проект для анализа торговых данных Path of Exile 2
"""

import asyncio
import logging
from pathlib import Path
import typer
from rich.console import Console
from rich.logging import RichHandler

from api.poe_api import PoEAPI
from ui.main_window import MainWindow
from config.settings import Settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)
console = Console()

app = typer.Typer(
    name="poe2-trade-assistant",
    help="PoE2 Trade Assistant - анализ торговых данных Path of Exile 2"
)


@app.command()
def gui():
    """Запустить графический интерфейс"""
    console.print("🚀 Запуск PoE2 Trade Assistant GUI...", style="bold green")
    
    try:
        # Загружаем настройки
        settings = Settings()
        
        # Запускаем GUI
        main_window = MainWindow(settings)
        main_window.run()
        
    except Exception as e:
        console.print(f"❌ Ошибка при запуске GUI: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def search(
    item_name: str = typer.Argument(..., help="Название предмета для поиска"),
    league: str = typer.Option("Hardcore", help="Лига"),
    max_price: float = typer.Option(None, help="Максимальная цена"),
    min_price: float = typer.Option(None, help="Минимальная цена")
):
    """Поиск предметов через командную строку"""
    console.print(f"🔍 Поиск предмета: {item_name}", style="bold blue")
    
    async def run_search():
        try:
            settings = Settings()
            api = PoEAPI(settings)
            
            search_params = {
                "name": item_name,
                "league": league
            }
            
            if max_price:
                search_params["max_price"] = max_price
            if min_price:
                search_params["min_price"] = min_price
            
            results = await api.search_items(**search_params)
            
            console.print(f"📊 Найдено {len(results)} предметов:", style="bold green")
            for item in results[:10]:  # Показываем первые 10 результатов
                console.print(f"  • {item.get('name', 'Unknown')} - {item.get('price', 'N/A')} {item.get('currency', '')}")
                
        except Exception as e:
            console.print(f"❌ Ошибка поиска: {e}", style="bold red")
            raise typer.Exit(1)
    
    asyncio.run(run_search())


@app.command()
def monitor(
    config_file: str = typer.Option("config/filters.json", help="Файл с фильтрами для мониторинга")
):
    """Запустить мониторинг предметов"""
    console.print("👁️  Запуск мониторинга предметов...", style="bold yellow")
    
    # TODO: Реализовать мониторинг
    console.print("🚧 Мониторинг пока не реализован", style="bold red")


@app.command()
def analyze(
    item_name: str = typer.Argument(..., help="Название предмета для анализа"),
    days: int = typer.Option(7, help="Количество дней для анализа")
):
    """Анализ цен на предмет"""
    console.print(f"📈 Анализ цен на {item_name} за последние {days} дней", style="bold cyan")
    
    # TODO: Реализовать анализ
    console.print("🚧 Анализ цен пока не реализован", style="bold red")


def main():
    """Точка входа в приложение"""
    console.print("""
    ⚔️  PoE2 Trade Assistant ⚔️
    
    ⚠️  ВАЖНО: Этот проект создан исключительно в образовательных целях.
    Автоматическая торговля может нарушать правила игры.
    Пожалуйста, соблюдайте условия использования Path of Exile 2.
    """, style="bold blue")
    
    app()


if __name__ == "__main__":
    main()