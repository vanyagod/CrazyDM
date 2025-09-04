"""
Автономное главное окно без внешних зависимостей
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MainWindowStandalone:
    """Автономное главное окно приложения"""
    
    def __init__(self, settings, api_available: bool = True):
        self.settings = settings
        self.api_available = api_available
        self.current_results: List[Dict[str, Any]] = []
        
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("PoE2 Trade Assistant - Автономная версия")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Создаем интерфейс
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        
        # Предупреждение
        warning_frame = ttk.Frame(self.root)
        warning_frame.pack(fill=tk.X, padx=10, pady=5)
        
        warning_text = "⚠️ ОБРАЗОВАТЕЛЬНЫЙ ПРОЕКТ - НЕ ДЛЯ АВТОМАТИЧЕСКОЙ ТОРГОВЛИ!"
        ttk.Label(warning_frame, text=warning_text, foreground="red", font=("Arial", 10, "bold")).pack()
        
        # Статус API
        status_text = f"🌐 API: {'Доступен' if self.api_available else 'Недоступен (демо режим)'}"
        ttk.Label(warning_frame, text=status_text, font=("Arial", 9)).pack()
        
        # Главное меню
        self.create_menu()
        
        # Создаем основные фреймы
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель (поиск и фильтры)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Правая панель (результаты)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Создаем секции
        self.create_search_section(left_frame)
        self.create_results_section(right_frame)
        self.create_status_bar()
    
    def create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Демо данные", command=self.load_demo_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_search_section(self, parent):
        """Создание секции поиска"""
        search_frame = ttk.LabelFrame(parent, text="Поиск предметов")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Название предмета
        ttk.Label(search_frame, text="Название предмета:").pack(anchor=tk.W, padx=5, pady=2)
        self.item_name_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.item_name_var, width=30).pack(fill=tk.X, padx=5, pady=2)
        
        # Лига
        ttk.Label(search_frame, text="Лига:").pack(anchor=tk.W, padx=5, pady=2)
        self.league_var = tk.StringVar(value=self.settings.league)
        league_combo = ttk.Combobox(search_frame, textvariable=self.league_var, width=27)
        league_combo['values'] = ["Necrosis", "Delirium", "Breach", "Ritual", "Necrosis HC", "Delirium HC", "Breach HC", "Ritual HC"]
        league_combo.pack(fill=tk.X, padx=5, pady=2)
        
        # Цена
        price_frame = ttk.Frame(search_frame)
        price_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(price_frame, text="Макс. цена:").pack(side=tk.LEFT)
        self.max_price_var = tk.StringVar()
        ttk.Entry(price_frame, textvariable=self.max_price_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # Валюта
        self.currency_var = tk.StringVar(value="chaos")
        currency_combo = ttk.Combobox(price_frame, textvariable=self.currency_var, width=10)
        currency_combo['values'] = ["chaos", "divine", "exalted", "ancient"]
        currency_combo.pack(side=tk.LEFT, padx=5)
        
        # Кнопки
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="🔍 Поиск", command=self.search_items).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="🎯 Демо", command=self.load_demo_data).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(button_frame, text="❌ Очистить", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))
        
        # Быстрые фильтры
        filter_frame = ttk.LabelFrame(search_frame, text="Быстрые фильтры")
        filter_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.unique_only = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Только уникальные", variable=self.unique_only).pack(anchor=tk.W, padx=5)
        
        self.cheap_only = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Дешевые (<50c)", variable=self.cheap_only).pack(anchor=tk.W, padx=5)
        
        self.currency_only = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Только валюта", variable=self.currency_only).pack(anchor=tk.W, padx=5)
    
    def create_results_section(self, parent):
        """Создание секции результатов"""
        results_frame = ttk.LabelFrame(parent, text="Результаты поиска")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Treeview для результатов
        columns = ("name", "type", "price", "currency", "ilvl", "seller")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        
        self.results_tree.heading("name", text="Название")
        self.results_tree.heading("type", text="Тип")
        self.results_tree.heading("price", text="Цена")
        self.results_tree.heading("currency", text="Валюта")
        self.results_tree.heading("ilvl", text="iLvl")
        self.results_tree.heading("seller", text="Продавец")
        
        self.results_tree.column("name", width=200)
        self.results_tree.column("type", width=150)
        self.results_tree.column("price", width=80)
        self.results_tree.column("currency", width=80)
        self.results_tree.column("ilvl", width=60)
        self.results_tree.column("seller", width=120)
        
        # Скроллбары для результатов
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        # Размещаем элементы
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязываем события
        self.results_tree.bind("<Double-1>", self.on_item_double_click)
    
    def create_status_bar(self):
        """Создание строки состояния"""
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def get_demo_data(self) -> List[Dict[str, Any]]:
        """Демонстрационные данные"""
        return [
            {"name": "Chaos Orb", "type": "Currency", "price": 1.0, "currency": "chaos", "ilvl": None, "seller": "DemoUser1", "frame_type": 5},
            {"name": "Divine Orb", "type": "Currency", "price": 180.0, "currency": "chaos", "ilvl": None, "seller": "DemoUser2", "frame_type": 5},
            {"name": "Exalted Orb", "type": "Currency", "price": 150.0, "currency": "chaos", "ilvl": None, "seller": "DemoUser3", "frame_type": 5},
            {"name": "Ancient Orb", "type": "Currency", "price": 0.8, "currency": "chaos", "ilvl": None, "seller": "DemoUser4", "frame_type": 5},
            {"name": "Brightbeak", "type": "War Hammer", "price": 15.5, "currency": "chaos", "ilvl": 85, "seller": "DemoUser5", "frame_type": 3},
            {"name": "Doryani's Catalyst", "type": "Vaal Sceptre", "price": 120.0, "currency": "chaos", "ilvl": 88, "seller": "DemoUser6", "frame_type": 3},
            {"name": "Rare Sword", "type": "One Handed Sword", "price": 45.0, "currency": "chaos", "ilvl": 82, "seller": "DemoUser7", "frame_type": 2},
            {"name": "Rare Ring", "type": "Gold Ring", "price": 35.0, "currency": "chaos", "ilvl": 85, "seller": "DemoUser8", "frame_type": 2},
            {"name": "Magic Boots", "type": "Dragonscale Boots", "price": 12.0, "currency": "chaos", "ilvl": 78, "seller": "DemoUser9", "frame_type": 1},
            {"name": "The Taming", "type": "Prismatic Ring", "price": 300.0, "currency": "chaos", "ilvl": 88, "seller": "DemoUser10", "frame_type": 3},
        ]
    
    def search_items(self):
        """Поиск предметов"""
        def run_search():
            try:
                self.status_var.set("Поиск предметов...")
                self.root.update()
                
                item_name = self.item_name_var.get().strip().lower()
                max_price_str = self.max_price_var.get().strip()
                
                if self.api_available:
                    # Имитация API запроса
                    time.sleep(1)  # Имитация задержки
                    
                    # Если API недоступен или возвращает ошибку, используем демо данные
                    results = self.get_demo_data()
                    
                    # Фильтрация по названию
                    if item_name:
                        results = [r for r in results if item_name in r['name'].lower()]
                    
                    # Фильтрация по цене
                    if max_price_str:
                        try:
                            max_price = float(max_price_str)
                            results = [r for r in results if r['price'] <= max_price]
                        except ValueError:
                            pass
                    
                    # Применяем быстрые фильтры
                    if self.unique_only.get():
                        results = [r for r in results if r['frame_type'] == 3]
                    
                    if self.cheap_only.get():
                        results = [r for r in results if r['price'] <= 50]
                    
                    if self.currency_only.get():
                        results = [r for r in results if r['type'] == 'Currency']
                    
                    # Обновляем результаты в главном потоке
                    self.root.after(0, lambda: self.update_results(results))
                    
                else:
                    # Демо режим
                    results = self.get_demo_data()
                    
                    if item_name:
                        results = [r for r in results if item_name in r['name'].lower()]
                    
                    self.root.after(0, lambda: self.update_results(results))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self.status_var.set(f"Ошибка поиска: {msg}"))
        
        # Запускаем поиск в отдельном потоке
        threading.Thread(target=run_search, daemon=True).start()
    
    def load_demo_data(self):
        """Загрузка демо данных"""
        results = self.get_demo_data()
        self.update_results(results)
        self.status_var.set(f"Загружены демо данные: {len(results)} предметов")
    
    def update_results(self, results: List[Dict[str, Any]]):
        """Обновление результатов поиска"""
        # Очищаем старые результаты
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Добавляем новые результаты
        for result in results:
            price_str = f"{result.get('price', 0):.1f}" if result.get('price') else "N/A"
            currency_str = result.get('currency', '')
            
            # Определяем цвет по типу рамки
            frame_type = result.get('frame_type', 0)
            tags = ()
            if frame_type == 3:  # Unique
                tags = ("unique",)
            elif frame_type == 2:  # Rare  
                tags = ("rare",)
            elif frame_type == 5:  # Currency
                tags = ("currency",)
            
            self.results_tree.insert("", tk.END, values=(
                result.get('name', 'Unknown'),
                result.get('type', 'Unknown'),
                price_str,
                currency_str,
                result.get('ilvl', 'N/A') if result.get('ilvl') else 'N/A',
                result.get('seller', 'Unknown')
            ), tags=tags)
        
        # Настраиваем цвета
        self.results_tree.tag_configure("unique", foreground="orange")
        self.results_tree.tag_configure("rare", foreground="yellow") 
        self.results_tree.tag_configure("currency", foreground="gold")
        
        self.status_var.set(f"Найдено {len(results)} предметов")
        self.current_results = results
    
    def clear_search(self):
        """Очистка поля поиска"""
        self.item_name_var.set("")
        self.max_price_var.set("")
        self.unique_only.set(False)
        self.cheap_only.set(False)
        self.currency_only.set(False)
        
        # Очищаем результаты
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.status_var.set("Поиск очищен")
    
    def on_item_double_click(self, event):
        """Обработка двойного клика по предмету"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        values = item['values']
        
        if values:
            name, item_type, price, currency, ilvl, seller = values
            
            # Анализ предмета
            analysis = f"📊 Анализ предмета: {name}\n\n"
            analysis += f"🎯 Тип: {item_type}\n"
            analysis += f"💰 Цена: {price} {currency}\n"
            analysis += f"📈 iLvl: {ilvl}\n"
            analysis += f"👤 Продавец: {seller}\n\n"
            
            # Простая рекомендация
            try:
                price_val = float(price)
                if price_val <= 10:
                    analysis += "✅ РЕКОМЕНДАЦИЯ: Очень выгодная цена!"
                elif price_val <= 50:
                    analysis += "🟡 РЕКОМЕНДАЦИЯ: Приемлемая цена"
                else:
                    analysis += "🔴 РЕКОМЕНДАЦИЯ: Дорого, подумайте дважды"
            except:
                analysis += "⚪ РЕКОМЕНДАЦИЯ: Проверьте цену вручную"
            
            analysis += "\n\n⚠️ Это демонстрационный анализ для образовательных целей!"
            
            messagebox.showinfo(f"Анализ: {name}", analysis)
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """PoE2 Trade Assistant v1.0 - Автономная версия

Образовательный проект для анализа торговых данных Path of Exile 2.

⚠️ ВАЖНО: Этот проект создан исключительно в образовательных целях.
Автоматическая торговля может нарушать правила игры.
Пожалуйста, соблюдайте условия использования Path of Exile 2.

Функции:
• Поиск и фильтрация предметов
• Анализ цен и рекомендации  
• Демонстрационные данные
• Образовательные материалы

Разработано с использованием Python и Tkinter."""
        
        messagebox.showinfo("О программе", about_text)
    
    def run(self):
        """Запуск главного цикла приложения"""
        self.root.mainloop()