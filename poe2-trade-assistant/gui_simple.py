#!/usr/bin/env python3
"""
Упрощенная версия GUI для PoE2 Trade Assistant
Работает только со стандартной библиотекой Python
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import urllib.request
import urllib.parse
from datetime import datetime


class SimplePoEGUI:
    """Упрощенный GUI для PoE2 Trade Assistant"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PoE2 Trade Assistant - Простая версия")
        self.root.geometry("900x700")
        
        # Данные
        self.current_results = []
        
        self.create_widgets()
        
    def create_widgets(self):
        """Создание интерфейса"""
        
        # Предупреждение
        warning_frame = ttk.Frame(self.root)
        warning_frame.pack(fill=tk.X, padx=10, pady=5)
        
        warning_text = "⚠️ ОБРАЗОВАТЕЛЬНЫЙ ПРОЕКТ - НЕ ДЛЯ АВТОМАТИЧЕСКОЙ ТОРГОВЛИ!"
        ttk.Label(warning_frame, text=warning_text, foreground="red", font=("Arial", 10, "bold")).pack()
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - поиск
        left_frame = ttk.LabelFrame(main_frame, text="Поиск предметов")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Поля поиска
        ttk.Label(left_frame, text="Название предмета:").pack(anchor=tk.W, padx=5, pady=2)
        self.item_name = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.item_name, width=25).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Лига:").pack(anchor=tk.W, padx=5, pady=2)
        self.league = tk.StringVar(value="Hardcore")
        league_combo = ttk.Combobox(left_frame, textvariable=self.league, width=22)
        league_combo['values'] = ["Hardcore", "Standard", "Hardcore SSF", "SSF"]
        league_combo.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Макс. цена:").pack(anchor=tk.W, padx=5, pady=2)
        self.max_price = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.max_price, width=25).pack(fill=tk.X, padx=5, pady=2)
        
        # Кнопки
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(button_frame, text="🔍 Поиск", command=self.search_demo).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="🎯 Демо данные", command=self.load_demo_data).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="❌ Очистить", command=self.clear_results).pack(fill=tk.X, pady=2)
        
        # Фильтры
        filter_frame = ttk.LabelFrame(left_frame, text="Быстрые фильтры")
        filter_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.unique_only = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Только уникальные", variable=self.unique_only).pack(anchor=tk.W, padx=5)
        
        self.cheap_only = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Дешевые (<50c)", variable=self.cheap_only).pack(anchor=tk.W, padx=5)
        
        # Правая панель - результаты
        right_frame = ttk.LabelFrame(main_frame, text="Результаты поиска")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Таблица результатов
        columns = ("name", "type", "price", "currency", "rarity")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("name", text="Название")
        self.tree.heading("type", text="Тип")
        self.tree.heading("price", text="Цена")
        self.tree.heading("currency", text="Валюта")
        self.tree.heading("rarity", text="Редкость")
        
        self.tree.column("name", width=200)
        self.tree.column("type", width=150)
        self.tree.column("price", width=80)
        self.tree.column("currency", width=80)
        self.tree.column("rarity", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка событий
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        # Статус бар
        self.status = tk.StringVar()
        self.status.set("Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(self.root, text="Информация")
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        info_text = """
🎓 Образовательный проект для изучения анализа торговых данных
⚠️ НЕ используйте для автоматической торговли!
📊 Демонстрирует принципы поиска и фильтрации предметов
        """.strip()
        
        ttk.Label(info_frame, text=info_text, font=("Arial", 9)).pack(padx=5, pady=5)
    
    def create_demo_items(self):
        """Создание демонстрационных предметов"""
        return [
            {"name": "Brightbeak", "type": "War Hammer", "price": 15.5, "currency": "chaos", "rarity": "Unique"},
            {"name": "Doryani's Catalyst", "type": "Vaal Sceptre", "price": 120.0, "currency": "chaos", "rarity": "Unique"},
            {"name": "Rare Sword", "type": "One Handed Sword", "price": 45.0, "currency": "chaos", "rarity": "Rare"},
            {"name": "Magic Axe", "type": "Two Handed Axe", "price": 8.5, "currency": "chaos", "rarity": "Magic"},
            {"name": "Kaom's Primacy", "type": "Karui Maul", "price": 200.0, "currency": "chaos", "rarity": "Unique"},
            {"name": "Belly of the Beast", "type": "Full Wyrmscale", "price": 85.0, "currency": "chaos", "rarity": "Unique"},
            {"name": "Rare Helmet", "type": "Royal Burgonet", "price": 25.0, "currency": "chaos", "rarity": "Rare"},
            {"name": "Lightning Coil", "type": "Desert Brigandine", "price": 150.0, "currency": "chaos", "rarity": "Unique"},
            {"name": "Magic Boots", "type": "Dragonscale Boots", "price": 12.0, "currency": "chaos", "rarity": "Magic"},
            {"name": "Rare Ring", "type": "Gold Ring", "price": 35.0, "currency": "chaos", "rarity": "Rare"},
            {"name": "The Taming", "type": "Prismatic Ring", "price": 300.0, "currency": "chaos", "rarity": "Unique"},
            {"name": "Divine Orb", "type": "Currency", "price": 180.0, "currency": "chaos", "rarity": "Currency"},
            {"name": "Exalted Orb", "type": "Currency", "price": 145.0, "currency": "chaos", "rarity": "Currency"},
            {"name": "Ancient Orb", "type": "Currency", "price": 0.8, "currency": "chaos", "rarity": "Currency"},
        ]
    
    def load_demo_data(self):
        """Загрузка демонстрационных данных"""
        self.current_results = self.create_demo_items()
        self.apply_filters_and_update()
        self.status.set(f"Загружено {len(self.current_results)} демо предметов")
    
    def apply_filters_and_update(self):
        """Применение фильтров и обновление отображения"""
        filtered_results = self.current_results.copy()
        
        # Фильтр по имени
        name_filter = self.item_name.get().strip().lower()
        if name_filter:
            filtered_results = [item for item in filtered_results 
                              if name_filter in item["name"].lower()]
        
        # Фильтр только уникальные
        if self.unique_only.get():
            filtered_results = [item for item in filtered_results 
                              if item["rarity"] == "Unique"]
        
        # Фильтр дешевые
        if self.cheap_only.get():
            filtered_results = [item for item in filtered_results 
                              if item["price"] <= 50.0]
        
        # Фильтр по цене
        max_price_str = self.max_price.get().strip()
        if max_price_str:
            try:
                max_price = float(max_price_str)
                filtered_results = [item for item in filtered_results 
                                  if item["price"] <= max_price]
            except ValueError:
                pass
        
        self.update_tree(filtered_results)
    
    def update_tree(self, items):
        """Обновление таблицы результатов"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавляем новые элементы
        for item in items:
            # Определяем цвет по редкости
            rarity = item["rarity"]
            tags = ()
            if rarity == "Unique":
                tags = ("unique",)
            elif rarity == "Rare":
                tags = ("rare",)
            elif rarity == "Currency":
                tags = ("currency",)
            
            self.tree.insert("", tk.END, values=(
                item["name"],
                item["type"],
                f"{item['price']:.1f}",
                item["currency"],
                item["rarity"]
            ), tags=tags)
        
        # Настраиваем цвета
        self.tree.tag_configure("unique", foreground="orange")
        self.tree.tag_configure("rare", foreground="yellow")
        self.tree.tag_configure("currency", foreground="gold")
        
        self.status.set(f"Показано {len(items)} предметов")
    
    def search_demo(self):
        """Демонстрационный поиск"""
        self.status.set("Выполняется поиск...")
        self.root.update()
        
        # Имитация поиска
        import time
        time.sleep(1)
        
        # Загружаем демо данные если их нет
        if not self.current_results:
            self.current_results = self.create_demo_items()
        
        self.apply_filters_and_update()
        
        messagebox.showinfo("Поиск", 
                          "Это демонстрационный поиск!\n\n"
                          "В реальной версии здесь был бы запрос к API Path of Exile.\n"
                          "Показаны тестовые данные для демонстрации функциональности.")
    
    def clear_results(self):
        """Очистка результатов"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_results = []
        self.item_name.set("")
        self.max_price.set("")
        self.unique_only.set(False)
        self.cheap_only.set(False)
        self.status.set("Результаты очищены")
    
    def on_item_double_click(self, event):
        """Обработка двойного клика по предмету"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if values:
            name, item_type, price, currency, rarity = values
            
            # Анализ предмета
            analysis = self.analyze_item(name, float(price), rarity)
            
            messagebox.showinfo(f"Анализ: {name}", analysis)
    
    def analyze_item(self, name, price, rarity):
        """Простой анализ предмета"""
        analysis = f"📊 Анализ предмета: {name}\n\n"
        
        # Анализ цены
        if price <= 10:
            price_analysis = "🟢 Очень дешево - возможно выгодная покупка!"
        elif price <= 50:
            price_analysis = "🟡 Доступная цена"
        elif price <= 100:
            price_analysis = "🟠 Средняя цена"
        else:
            price_analysis = "🔴 Дорого - подумайте дважды"
        
        analysis += f"💰 Цена: {price} chaos - {price_analysis}\n\n"
        
        # Анализ редкости
        if rarity == "Unique":
            rarity_analysis = "⭐ Уникальный предмет - может иметь особые свойства"
        elif rarity == "Rare":
            rarity_analysis = "🟡 Редкий предмет - проверьте характеристики"
        elif rarity == "Currency":
            rarity_analysis = "💎 Валюта - стабильная ценность"
        else:
            rarity_analysis = "⚪ Обычный предмет"
        
        analysis += f"🎯 Редкость: {rarity_analysis}\n\n"
        
        # Рекомендация
        if price <= 20 and rarity in ["Unique", "Rare"]:
            recommendation = "✅ РЕКОМЕНДУЕТСЯ К ПОКУПКЕ"
        elif price > 100:
            recommendation = "❌ НЕ РЕКОМЕНДУЕТСЯ - СЛИШКОМ ДОРОГО"
        else:
            recommendation = "⚪ НЕЙТРАЛЬНО - НА ВАШ ВЫБОР"
        
        analysis += f"🤖 Рекомендация: {recommendation}\n\n"
        analysis += "⚠️ Это демонстрационный анализ для образовательных целей!"
        
        return analysis
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def main():
    """Главная функция"""
    try:
        app = SimplePoEGUI()
        app.run()
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("tkinter недоступен. Запустите демо-версию: python demo.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Попробуйте запустить: python demo.py")


if __name__ == "__main__":
    main()