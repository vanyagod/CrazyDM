#!/usr/bin/env python3
"""
Демонстрационный скрипт PoE2 Trade Assistant
Показывает основную функциональность без внешних зависимостей
"""

import json
from datetime import datetime
from typing import List, Dict, Any


class SimpleItem:
    """Упрощенная модель предмета"""
    
    def __init__(self, name: str, item_type: str, price: float, currency: str = "chaos", ilvl: int = 0):
        self.name = name
        self.item_type = item_type
        self.price = price
        self.currency = currency
        self.ilvl = ilvl
        self.corrupted = False
        self.frame_type = 1  # 1=magic, 2=rare, 3=unique
    
    def __repr__(self):
        return f"Item({self.name}, {self.price} {self.currency})"


class SimpleFilter:
    """Упрощенная система фильтрации"""
    
    def __init__(self, name: str):
        self.name = name
        self.max_price = None
        self.min_price = None
        self.item_types = []
        self.min_ilvl = None
        self.unique_only = False
    
    def matches(self, item: SimpleItem) -> bool:
        """Проверка соответствия предмета фильтру"""
        
        # Проверка цены
        if self.max_price and item.price > self.max_price:
            return False
        
        if self.min_price and item.price < self.min_price:
            return False
        
        # Проверка типа
        if self.item_types and item.item_type not in self.item_types:
            return False
        
        # Проверка уровня
        if self.min_ilvl and item.ilvl < self.min_ilvl:
            return False
        
        # Проверка уникальности
        if self.unique_only and item.frame_type != 3:
            return False
        
        return True


class PriceAnalyzer:
    """Упрощенный анализатор цен"""
    
    def analyze_prices(self, items: List[SimpleItem]) -> Dict[str, Any]:
        """Анализ цен"""
        if not items:
            return {"count": 0}
        
        prices = [item.price for item in items]
        prices.sort()
        
        count = len(prices)
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / count
        median_price = prices[count // 2]
        
        return {
            "count": count,
            "min": min_price,
            "max": max_price,
            "average": avg_price,
            "median": median_price
        }
    
    def find_good_deals(self, items: List[SimpleItem], threshold: float = 0.8) -> List[SimpleItem]:
        """Поиск выгодных предложений"""
        stats = self.analyze_prices(items)
        
        if stats["count"] == 0:
            return []
        
        threshold_price = stats["average"] * threshold
        
        good_deals = [item for item in items if item.price <= threshold_price]
        good_deals.sort(key=lambda x: x.price)
        
        return good_deals


def create_demo_data() -> List[SimpleItem]:
    """Создание демонстрационных данных"""
    items = [
        # Оружие
        SimpleItem("Brightbeak", "War Hammer", 15.5, "chaos", 85),
        SimpleItem("Doryani's Catalyst", "Vaal Sceptre", 120.0, "chaos", 88),
        SimpleItem("Rare Sword", "One Handed Sword", 45.0, "chaos", 82),
        SimpleItem("Magic Axe", "Two Handed Axe", 8.5, "chaos", 75),
        SimpleItem("Kaom's Primacy", "Karui Maul", 200.0, "chaos", 90),
        
        # Броня
        SimpleItem("Belly of the Beast", "Full Wyrmscale", 85.0, "chaos", 84),
        SimpleItem("Rare Helmet", "Royal Burgonet", 25.0, "chaos", 80),
        SimpleItem("Lightning Coil", "Desert Brigandine", 150.0, "chaos", 86),
        SimpleItem("Magic Boots", "Dragonscale Boots", 12.0, "chaos", 78),
        
        # Украшения
        SimpleItem("Rare Ring", "Gold Ring", 35.0, "chaos", 85),
        SimpleItem("The Taming", "Prismatic Ring", 300.0, "chaos", 88),
        SimpleItem("Rare Amulet", "Jade Amulet", 55.0, "chaos", 83),
        
        # Валюта
        SimpleItem("Divine Orb", "Currency", 180.0, "chaos", 0),
        SimpleItem("Exalted Orb", "Currency", 145.0, "chaos", 0),
        SimpleItem("Ancient Orb", "Currency", 0.8, "chaos", 0),
    ]
    
    # Устанавливаем frame_type для уникальных предметов
    unique_names = ["Brightbeak", "Doryani's Catalyst", "Kaom's Primacy", "Belly of the Beast", 
                   "Lightning Coil", "The Taming"]
    
    for item in items:
        if item.name in unique_names:
            item.frame_type = 3  # Unique
        elif "Rare" in item.name:
            item.frame_type = 2  # Rare
        else:
            item.frame_type = 1  # Magic
    
    return items


def demo_basic_search():
    """Демонстрация базового поиска"""
    print("=" * 60)
    print("🔍 ДЕМОНСТРАЦИЯ БАЗОВОГО ПОИСКА")
    print("=" * 60)
    
    items = create_demo_data()
    
    print(f"Всего предметов в базе: {len(items)}")
    print("\nПредметы:")
    for item in items:
        rarity = "Unique" if item.frame_type == 3 else "Rare" if item.frame_type == 2 else "Magic"
        print(f"  • {item.name} ({rarity}) - {item.price} {item.currency}")


def demo_filtering():
    """Демонстрация фильтрации"""
    print("\n" + "=" * 60)
    print("🎯 ДЕМОНСТРАЦИЯ ФИЛЬТРАЦИИ")
    print("=" * 60)
    
    items = create_demo_data()
    
    # Фильтр выгодных предложений
    cheap_filter = SimpleFilter("Выгодные предложения")
    cheap_filter.max_price = 50.0
    
    cheap_items = [item for item in items if cheap_filter.matches(item)]
    
    print(f"\n📊 Предметы дешевле 50 хаосов ({len(cheap_items)} из {len(items)}):")
    for item in cheap_items:
        print(f"  • {item.name} - {item.price} chaos")
    
    # Фильтр уникальных предметов
    unique_filter = SimpleFilter("Уникальные предметы")
    unique_filter.unique_only = True
    
    unique_items = [item for item in items if unique_filter.matches(item)]
    
    print(f"\n⭐ Уникальные предметы ({len(unique_items)} из {len(items)}):")
    for item in unique_items:
        print(f"  • {item.name} - {item.price} chaos")
    
    # Комбинированный фильтр
    combo_filter = SimpleFilter("Доступные уникальные")
    combo_filter.unique_only = True
    combo_filter.max_price = 200.0
    
    combo_items = [item for item in items if combo_filter.matches(item)]
    
    print(f"\n🎯 Доступные уникальные предметы (<200 chaos): ({len(combo_items)} из {len(items)}):")
    for item in combo_items:
        print(f"  • {item.name} - {item.price} chaos")


def demo_price_analysis():
    """Демонстрация анализа цен"""
    print("\n" + "=" * 60)
    print("📈 ДЕМОНСТРАЦИЯ АНАЛИЗА ЦEN")
    print("=" * 60)
    
    items = create_demo_data()
    analyzer = PriceAnalyzer()
    
    # Общая статистика
    stats = analyzer.analyze_prices(items)
    
    print("\n📊 Общая статистика цен:")
    print(f"  • Количество предметов: {stats['count']}")
    print(f"  • Минимальная цена: {stats['min']:.1f} chaos")
    print(f"  • Максимальная цена: {stats['max']:.1f} chaos")
    print(f"  • Средняя цена: {stats['average']:.1f} chaos")
    print(f"  • Медианная цена: {stats['median']:.1f} chaos")
    
    # Поиск выгодных предложений
    good_deals = analyzer.find_good_deals(items, 0.7)  # 70% от средней цены
    
    print(f"\n🎯 Выгодные предложения (< {stats['average'] * 0.7:.1f} chaos):")
    for item in good_deals:
        savings = ((stats['average'] - item.price) / stats['average']) * 100
        print(f"  • {item.name} - {item.price} chaos (экономия {savings:.1f}%)")
    
    # Анализ по категориям
    weapon_items = [item for item in items if "Sword" in item.item_type or "Hammer" in item.item_type or 
                   "Axe" in item.item_type or "Sceptre" in item.item_type or "Maul" in item.item_type]
    
    if weapon_items:
        weapon_stats = analyzer.analyze_prices(weapon_items)
        print(f"\n⚔️ Статистика цен на оружие:")
        print(f"  • Количество: {weapon_stats['count']}")
        print(f"  • Средняя цена: {weapon_stats['average']:.1f} chaos")
        print(f"  • Диапазон: {weapon_stats['min']:.1f} - {weapon_stats['max']:.1f} chaos")


def demo_purchase_advisor():
    """Демонстрация советника по покупкам"""
    print("\n" + "=" * 60)
    print("🤖 ДЕМОНСТРАЦИЯ СОВЕТНИКА ПО ПОКУПКАМ")
    print("=" * 60)
    
    items = create_demo_data()
    analyzer = PriceAnalyzer()
    stats = analyzer.analyze_prices(items)
    
    print("\n💡 Рекомендации по покупкам:")
    
    for item in items:
        price_ratio = item.price / stats['average'] if stats['average'] > 0 else 1.0
        
        if price_ratio <= 0.6:
            decision = "🟢 КУПИТЬ"
            reason = "Отличная цена!"
        elif price_ratio <= 0.8:
            decision = "🟡 РАССМОТРЕТЬ"
            reason = "Выгодная цена"
        elif price_ratio >= 1.5:
            decision = "🔴 ПРОПУСТИТЬ"
            reason = "Переплата"
        else:
            decision = "⚪ ПОДОЖДАТЬ"
            reason = "Средняя цена"
        
        confidence = min(100, max(20, 100 - abs(price_ratio - 0.7) * 50))
        
        print(f"  • {item.name:<20} {decision} (уверенность: {confidence:.0f}%)")
        print(f"    💰 {item.price} chaos | {reason}")
        print()


def demo_build_filter():
    """Демонстрация фильтра для билда"""
    print("\n" + "=" * 60)
    print("🏗️ ДЕМОНСТРАЦИЯ ФИЛЬТРА ДЛЯ БИЛДА")
    print("=" * 60)
    
    items = create_demo_data()
    
    # Фильтр для мили-билда
    melee_filter = SimpleFilter("Мили-билд")
    melee_filter.item_types = ["War Hammer", "Two Handed Axe", "Karui Maul", "One Handed Sword"]
    melee_filter.max_price = 100.0
    melee_filter.min_ilvl = 80
    
    melee_items = [item for item in items if melee_filter.matches(item)]
    
    print("⚔️ Подходящие предметы для мили-билда:")
    print("   (Оружие ближнего боя, iLvl 80+, <100 chaos)")
    
    if melee_items:
        for item in melee_items:
            print(f"  • {item.name} ({item.item_type}) - {item.price} chaos, iLvl {item.ilvl}")
    else:
        print("  Подходящих предметов не найдено")
    
    # Фильтр для танк-билда
    tank_filter = SimpleFilter("Танк-билд")
    tank_filter.item_types = ["Full Wyrmscale", "Royal Burgonet", "Desert Brigandine"]
    tank_filter.max_price = 200.0
    
    tank_items = [item for item in items if tank_filter.matches(item)]
    
    print("\n🛡️ Подходящие предметы для танк-билда:")
    print("   (Тяжелая броня, <200 chaos)")
    
    if tank_items:
        for item in tank_items:
            print(f"  • {item.name} ({item.item_type}) - {item.price} chaos")
    else:
        print("  Подходящих предметов не найдено")


def main():
    """Главная функция демонстрации"""
    print("⚔️ PoE2 Trade Assistant - Демонстрация")
    print("🎓 Образовательный проект для анализа торговых данных")
    print()
    print("⚠️ ВАЖНО: Этот проект создан исключительно в образовательных целях.")
    print("   Автоматическая торговля может нарушать правила игры!")
    
    # Запуск всех демонстраций
    demo_basic_search()
    demo_filtering()
    demo_price_analysis()
    demo_purchase_advisor()
    demo_build_filter()
    
    print("\n" + "=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
    print("\nДля запуска полной версии:")
    print("1. Установите зависимости: pip install -r requirements.txt")
    print("2. Настройте .env файл")
    print("3. Запустите: python run.py gui")
    print("\nПодробная документация в файле USAGE.md")


if __name__ == "__main__":
    main()