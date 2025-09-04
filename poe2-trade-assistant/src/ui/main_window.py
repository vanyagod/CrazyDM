"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import threading
import json
from typing import List, Optional
import logging

from config.settings import Settings
from api.poe2_simple import SimplePoE2API
from api.models import SearchResult
from filters.item_filter import ItemFilter, FilterRule
from filters.preset_filters import PresetFilters

logger = logging.getLogger(__name__)


class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api = SimplePoE2API(settings)
        self.item_filter = ItemFilter()
        self.current_results: List[SearchResult] = []
        
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("PoE2 Trade Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Настраиваем стиль
        self.setup_style()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Загружаем предустановленные фильтры (отключено из-за проблем с валидацией)
        # self.load_preset_filters()
    
    def setup_style(self):
        """Настройка стиля интерфейса"""
        style = ttk.Style()
        
        if self.settings.theme == "dark":
            # Темная тема (если доступна)
            try:
                style.theme_use('clam')
                self.root.configure(bg='#2b2b2b')
            except:
                pass
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        
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
        self.create_filter_section(left_frame)
        self.create_results_section(right_frame)
        self.create_status_bar()
    
    def create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить фильтры", command=self.load_filters)
        file_menu.add_command(label="Сохранить фильтры", command=self.save_filters)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Инструменты
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Настройки", command=self.show_settings)
        tools_menu.add_command(label="Анализ цен", command=self.show_price_analysis)
        
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
        
        ttk.Label(price_frame, text="Мин. цена:").pack(side=tk.LEFT)
        self.min_price_var = tk.StringVar()
        ttk.Entry(price_frame, textvariable=self.min_price_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(price_frame, text="Макс. цена:").pack(side=tk.LEFT, padx=(10, 0))
        self.max_price_var = tk.StringVar()
        ttk.Entry(price_frame, textvariable=self.max_price_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Валюта
        self.currency_var = tk.StringVar(value="chaos")
        currency_combo = ttk.Combobox(price_frame, textvariable=self.currency_var, width=10)
        currency_combo['values'] = ["chaos", "divine", "exalted", "ancient"]
        currency_combo.pack(side=tk.LEFT, padx=5)
        
        # Кнопки
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Поиск", command=self.search_items).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Очистить", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_filter_section(self, parent):
        """Создание секции фильтров"""
        filter_frame = ttk.LabelFrame(parent, text="Фильтры")
        filter_frame.pack(fill=tk.BOTH, expand=True)
        
        # Список фильтров
        filter_list_frame = ttk.Frame(filter_frame)
        filter_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создаем Treeview для фильтров
        columns = ("name", "type", "enabled")
        self.filter_tree = ttk.Treeview(filter_list_frame, columns=columns, show="headings", height=10)
        
        self.filter_tree.heading("name", text="Название")
        self.filter_tree.heading("type", text="Тип")
        self.filter_tree.heading("enabled", text="Включен")
        
        self.filter_tree.column("name", width=150)
        self.filter_tree.column("type", width=80)
        self.filter_tree.column("enabled", width=60)
        
        # Скроллбар для списка фильтров
        filter_scrollbar = ttk.Scrollbar(filter_list_frame, orient=tk.VERTICAL, command=self.filter_tree.yview)
        self.filter_tree.configure(yscrollcommand=filter_scrollbar.set)
        
        self.filter_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        filter_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления фильтрами
        filter_button_frame = ttk.Frame(filter_frame)
        filter_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(filter_button_frame, text="Добавить", command=self.add_filter).pack(side=tk.LEFT)
        ttk.Button(filter_button_frame, text="Изменить", command=self.edit_filter).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(filter_button_frame, text="Удалить", command=self.remove_filter).pack(side=tk.LEFT, padx=(5, 0))
        
        # Предустановленные фильтры
        preset_frame = ttk.Frame(filter_frame)
        preset_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(preset_frame, text="Предустановки:").pack(anchor=tk.W)
        self.preset_var = tk.StringVar()
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, width=25)
        preset_combo['values'] = [
            "Выгодные предложения",
            "Уникальные предметы", 
            "Высокий уровень",
            "6-связанные",
            "Оружие",
            "Броня",
            "Украшения"
        ]
        preset_combo.pack(fill=tk.X, pady=2)
        
        ttk.Button(preset_frame, text="Применить пресет", command=self.apply_preset).pack(fill=tk.X, pady=2)
    
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
        results_v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        results_h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=results_v_scrollbar.set, xscrollcommand=results_h_scrollbar.set)
        
        # Размещаем элементы
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        results_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Привязываем события
        self.results_tree.bind("<Double-1>", self.on_item_double_click)
        self.results_tree.bind("<Button-3>", self.on_item_right_click)
    
    def create_status_bar(self):
        """Создание строки состояния"""
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_preset_filters(self):
        """Загрузка предустановленных фильтров"""
        try:
            presets = PresetFilters.get_all_presets()
            for preset in presets:
                self.item_filter.add_rule(preset)
            
            self.update_filter_list()
            logger.info(f"Loaded {len(presets)} preset filters")
        except Exception as e:
            logger.error(f"Failed to load preset filters: {e}")
    
    def update_filter_list(self):
        """Обновление списка фильтров"""
        # Очищаем список
        for item in self.filter_tree.get_children():
            self.filter_tree.delete(item)
        
        # Добавляем фильтры
        all_rules = (
            [(rule, "filter") for rule in self.item_filter.rules] +
            [(rule, "whitelist") for rule in self.item_filter.whitelist_rules] +
            [(rule, "blacklist") for rule in self.item_filter.blacklist_rules]
        )
        
        for rule, rule_type in all_rules:
            self.filter_tree.insert("", tk.END, values=(
                rule.name,
                rule_type,
                "Да" if rule.enabled else "Нет"
            ))
    
    def search_items(self):
        """Поиск предметов"""
        def run_search():
            try:
                self.status_var.set("Поиск предметов...")
                self.root.update()
                
                # Получаем параметры поиска
                item_name = self.item_name_var.get().strip()
                league = self.league_var.get()
                min_price = None
                max_price = None
                
                try:
                    if self.min_price_var.get().strip():
                        min_price = float(self.min_price_var.get())
                except ValueError:
                    pass
                
                try:
                    if self.max_price_var.get().strip():
                        max_price = float(self.max_price_var.get())
                except ValueError:
                    pass
                
                currency = self.currency_var.get()
                
                # Выполняем синхронный поиск
                raw_results = self.api.search_items_simple(
                    league=league,
                    item_name=item_name if item_name else None,
                    min_price=min_price,
                    max_price=max_price,
                    currency=currency
                )
                
                # Конвертируем в SearchResult объекты
                results = []
                for raw_item in raw_results:
                    try:
                        # Создаем упрощенные объекты
                        item = type('Item', (), {
                            'id': raw_item.get('name', 'unknown'),
                            'name': raw_item.get('name'),
                            'type_line': raw_item.get('type'),
                            'ilvl': raw_item.get('ilvl'),
                            'corrupted': raw_item.get('corrupted', False),
                            'frame_type': raw_item.get('frame_type', 0)
                        })()
                        
                        price = None
                        if raw_item.get('price'):
                            price = type('PriceData', (), {
                                'amount': raw_item.get('price', 0),
                                'currency': raw_item.get('currency', 'chaos'),
                                'type': 'fixed'
                            })()
                        
                        result = type('SearchResult', (), {
                            'item': item,
                            'price': price,
                            'listing': {'account': {'name': raw_item.get('seller', 'Unknown')}},
                            'price_chaos': raw_item.get('price', 0) if raw_item.get('currency') == 'chaos' else None
                        })()
                        
                        results.append(result)
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse item: {e}")
                        continue
                
                # Применяем фильтры (упрощенно)
                filtered_results = results  # Пока без сложной фильтрации
                
                # Обновляем результаты в главном потоке
                self.root.after(0, lambda: self.update_results_simple(raw_results))
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Search failed: {error_msg}")
                self.root.after(0, lambda msg=error_msg: self.status_var.set(f"Ошибка поиска: {msg}"))
        
        # Запускаем поиск в отдельном потоке
        threading.Thread(target=run_search, daemon=True).start()
    
    def update_results(self, results: List[SearchResult]):
        """Обновление результатов поиска"""
        # Очищаем старые результаты
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Добавляем новые результаты
        self.current_results = results
        
        for result in results:
            item = result.item
            price_str = f"{result.price.amount:.1f}" if result.price else "N/A"
            currency_str = result.price.currency if result.price else ""
            
            self.results_tree.insert("", tk.END, values=(
                item.name or "Unknown",
                item.type_line or "Unknown",
                price_str,
                currency_str,
                item.ilvl or "N/A",
                result.listing.get("account", {}).get("name", "Unknown") if result.listing else "Unknown"
            ))
        
        self.status_var.set(f"Найдено {len(results)} предметов")
    
    def update_results_simple(self, raw_results: List[Dict[str, Any]]):
        """Упрощенное обновление результатов"""
        # Очищаем старые результаты
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Добавляем новые результаты
        for result in raw_results:
            price_str = f"{result.get('price', 'N/A'):.1f}" if result.get('price') else "N/A"
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
                result.get('ilvl', 'N/A'),
                result.get('seller', 'Unknown')
            ), tags=tags)
        
        # Настраиваем цвета
        self.results_tree.tag_configure("unique", foreground="orange")
        self.results_tree.tag_configure("rare", foreground="yellow") 
        self.results_tree.tag_configure("currency", foreground="gold")
        
        self.status_var.set(f"Найдено {len(raw_results)} предметов")
    
    def clear_search(self):
        """Очистка поля поиска"""
        self.item_name_var.set("")
        self.min_price_var.set("")
        self.max_price_var.set("")
    
    def add_filter(self):
        """Добавление нового фильтра"""
        # TODO: Открыть диалог создания фильтра
        messagebox.showinfo("Информация", "Функция создания фильтров будет добавлена в следующих версиях")
    
    def edit_filter(self):
        """Редактирование фильтра"""
        # TODO: Открыть диалог редактирования фильтра
        messagebox.showinfo("Информация", "Функция редактирования фильтров будет добавлена в следующих версиях")
    
    def remove_filter(self):
        """Удаление фильтра"""
        selected = self.filter_tree.selection()
        if not selected:
            return
        
        item = self.filter_tree.item(selected[0])
        filter_name = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить фильтр '{filter_name}'?"):
            self.item_filter.remove_rule(filter_name)
            self.update_filter_list()
    
    def apply_preset(self):
        """Применение предустановленного фильтра"""
        preset_name = self.preset_var.get()
        if not preset_name:
            return
        
        # Маппинг названий на фильтры
        preset_map = {
            "Выгодные предложения": PresetFilters.good_deals_filter,
            "Уникальные предметы": PresetFilters.unique_items_filter,
            "Высокий уровень": PresetFilters.high_ilvl_filter,
            "6-связанные": PresetFilters.six_link_filter,
            "Оружие": PresetFilters.weapon_filter,
            "Броня": PresetFilters.armor_filter,
            "Украшения": PresetFilters.jewelry_filter
        }
        
        if preset_name in preset_map:
            filter_rule = preset_map[preset_name]()
            self.item_filter.add_rule(filter_rule)
            self.update_filter_list()
            self.status_var.set(f"Добавлен фильтр: {preset_name}")
    
    def on_item_double_click(self, event):
        """Обработка двойного клика по предмету"""
        selected = self.results_tree.selection()
        if not selected:
            return
        
        # TODO: Открыть детальную информацию о предмете
        messagebox.showinfo("Информация", "Детальный просмотр предметов будет добавлен в следующих версиях")
    
    def on_item_right_click(self, event):
        """Обработка правого клика по предмету"""
        # TODO: Показать контекстное меню
        pass
    
    def load_filters(self):
        """Загрузка фильтров из файла"""
        filename = filedialog.askopenfilename(
            title="Загрузить фильтры",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.item_filter.import_rules(data)
                self.update_filter_list()
                self.status_var.set(f"Фильтры загружены из {filename}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить фильтры: {e}")
    
    def save_filters(self):
        """Сохранение фильтров в файл"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить фильтры",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = self.item_filter.export_rules()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.status_var.set(f"Фильтры сохранены в {filename}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить фильтры: {e}")
    
    def show_settings(self):
        """Показать окно настроек"""
        # TODO: Создать окно настроек
        messagebox.showinfo("Информация", "Окно настроек будет добавлено в следующих версиях")
    
    def show_price_analysis(self):
        """Показать анализ цен"""
        # TODO: Создать окно анализа цен
        messagebox.showinfo("Информация", "Анализ цен будет добавлен в следующих версиях")
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """PoE2 Trade Assistant v1.0

Образовательный проект для анализа торговых данных Path of Exile 2.

⚠️ ВАЖНО: Этот проект создан исключительно в образовательных целях.
Автоматическая торговля может нарушать правила игры.
Пожалуйста, соблюдайте условия использования Path of Exile 2.

Разработано с использованием Python и Tkinter."""
        
        messagebox.showinfo("О программе", about_text)
    
    def run(self):
        """Запуск главного цикла приложения"""
        try:
            self.root.mainloop()
        finally:
            # Закрываем API соединения
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.api.close())
                loop.close()
            except:
                pass