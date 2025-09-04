"""
Предустановленные фильтры для популярных случаев использования
"""

from typing import List
from .item_filter import FilterRule, FilterCondition, FilterOperator


class PresetFilters:
    """Класс с предустановленными фильтрами"""
    
    @staticmethod
    def good_deals_filter(max_price_chaos: float = 50) -> FilterRule:
        """Фильтр для поиска выгодных предложений"""
        return FilterRule(
            name="Good Deals",
            description=f"Items priced under {max_price_chaos} chaos",
            conditions=[
                FilterCondition(
                    field="price_chaos",
                    operator=FilterOperator.LESS_EQUAL,
                    value=max_price_chaos
                ),
                FilterCondition(
                    field="price",
                    operator=FilterOperator.NOT_EQUALS,
                    value=None
                )
            ],
            logic="and",
            priority=100
        )
    
    @staticmethod
    def unique_items_filter() -> FilterRule:
        """Фильтр для уникальных предметов"""
        return FilterRule(
            name="Unique Items",
            description="Only unique items (orange frame)",
            conditions=[
                FilterCondition(
                    field="item.frame_type",
                    operator=FilterOperator.EQUALS,
                    value=3  # Unique items have frame_type = 3
                )
            ],
            priority=90
        )
    
    @staticmethod
    def high_ilvl_filter(min_ilvl: int = 80) -> FilterRule:
        """Фильтр для предметов с высоким уровнем"""
        return FilterRule(
            name=f"High iLvl ({min_ilvl}+)",
            description=f"Items with item level {min_ilvl} or higher",
            conditions=[
                FilterCondition(
                    field="item.ilvl",
                    operator=FilterOperator.GREATER_EQUAL,
                    value=min_ilvl
                )
            ],
            priority=80
        )
    
    @staticmethod
    def six_link_filter() -> FilterRule:
        """Фильтр для 6-линкованных предметов"""
        return FilterRule(
            name="6-Link Items",
            description="Items with 6 linked sockets",
            conditions=[
                FilterCondition(
                    field="item.socket_links",
                    operator=FilterOperator.EQUALS,
                    value=6
                )
            ],
            priority=95
        )
    
    @staticmethod
    def corrupted_filter(corrupted: bool = False) -> FilterRule:
        """Фильтр для некоррапченных/коррапченных предметов"""
        return FilterRule(
            name=f"{'Corrupted' if corrupted else 'Non-Corrupted'} Items",
            description=f"Only {'corrupted' if corrupted else 'non-corrupted'} items",
            conditions=[
                FilterCondition(
                    field="item.corrupted",
                    operator=FilterOperator.EQUALS,
                    value=corrupted
                )
            ],
            priority=70
        )
    
    @staticmethod
    def weapon_filter(weapon_types: List[str] = None) -> FilterRule:
        """Фильтр для оружия определенных типов"""
        if weapon_types is None:
            weapon_types = ["Sword", "Axe", "Mace", "Bow", "Staff", "Wand", "Dagger", "Claw"]
        
        return FilterRule(
            name="Weapon Filter",
            description=f"Weapons of types: {', '.join(weapon_types)}",
            conditions=[
                FilterCondition(
                    field="item.type_line",
                    operator=FilterOperator.REGEX,
                    value=f"({'|'.join(weapon_types)})"
                )
            ],
            priority=60
        )
    
    @staticmethod
    def armor_filter(armor_types: List[str] = None) -> FilterRule:
        """Фильтр для брони определенных типов"""
        if armor_types is None:
            armor_types = ["Helmet", "Body Armour", "Gloves", "Boots", "Shield"]
        
        return FilterRule(
            name="Armor Filter",
            description=f"Armor of types: {', '.join(armor_types)}",
            conditions=[
                FilterCondition(
                    field="item.type_line",
                    operator=FilterOperator.REGEX,
                    value=f"({'|'.join(armor_types)})"
                )
            ],
            priority=60
        )
    
    @staticmethod
    def jewelry_filter() -> FilterRule:
        """Фильтр для украшений"""
        return FilterRule(
            name="Jewelry Filter",
            description="Rings, amulets, and belts",
            conditions=[
                FilterCondition(
                    field="item.type_line",
                    operator=FilterOperator.REGEX,
                    value="(Ring|Amulet|Belt)"
                )
            ],
            priority=60
        )
    
    @staticmethod
    def flask_filter() -> FilterRule:
        """Фильтр для флаконов"""
        return FilterRule(
            name="Flask Filter",
            description="All types of flasks",
            conditions=[
                FilterCondition(
                    field="item.type_line",
                    operator=FilterOperator.CONTAINS,
                    value="Flask"
                )
            ],
            priority=50
        )
    
    @staticmethod
    def gem_filter(min_level: int = 1, max_level: int = 21) -> FilterRule:
        """Фильтр для гемов"""
        return FilterRule(
            name=f"Gem Filter (Lvl {min_level}-{max_level})",
            description=f"Gems with level between {min_level} and {max_level}",
            conditions=[
                FilterCondition(
                    field="item.type_line",
                    operator=FilterOperator.REGEX,
                    value="(Skill Gem|Support Gem|Gem)"
                ),
                FilterCondition(
                    field="item.properties",
                    operator=FilterOperator.REGEX,
                    value=f"Level: ([{min_level}-{max_level}])"
                )
            ],
            logic="and",
            priority=60
        )
    
    @staticmethod
    def currency_filter(currencies: List[str] = None) -> FilterRule:
        """Фильтр для валюты"""
        if currencies is None:
            currencies = ["Divine Orb", "Chaos Orb", "Exalted Orb", "Ancient Orb"]
        
        return FilterRule(
            name="Currency Filter",
            description=f"Currency: {', '.join(currencies)}",
            conditions=[
                FilterCondition(
                    field="item.name",
                    operator=FilterOperator.IN,
                    value=currencies
                )
            ],
            priority=70
        )
    
    @staticmethod
    def recently_listed_filter(hours: int = 1) -> FilterRule:
        """Фильтр для недавно выставленных предметов"""
        return FilterRule(
            name=f"Recently Listed ({hours}h)",
            description=f"Items listed within the last {hours} hours",
            conditions=[
                # Это условие потребует дополнительной логики для работы с датами
                # Пока оставим как пример
                FilterCondition(
                    field="indexed_at",
                    operator=FilterOperator.GREATER,
                    value=f"-{hours}h"  # Специальный формат для относительного времени
                )
            ],
            priority=85
        )
    
    @staticmethod
    def get_all_presets() -> List[FilterRule]:
        """Получить все предустановленные фильтры"""
        return [
            PresetFilters.good_deals_filter(),
            PresetFilters.unique_items_filter(),
            PresetFilters.high_ilvl_filter(),
            PresetFilters.six_link_filter(),
            PresetFilters.corrupted_filter(False),
            PresetFilters.weapon_filter(),
            PresetFilters.armor_filter(),
            PresetFilters.jewelry_filter(),
            PresetFilters.flask_filter(),
            PresetFilters.gem_filter(),
            PresetFilters.currency_filter(),
            PresetFilters.recently_listed_filter()
        ]
    
    @staticmethod
    def create_build_filter(
        build_name: str,
        required_stats: List[str],
        item_types: List[str] = None,
        max_price: float = None
    ) -> FilterRule:
        """Создать фильтр для конкретного билда"""
        conditions = []
        
        # Фильтр по типам предметов
        if item_types:
            conditions.append(
                FilterCondition(
                    field="item.type_line",
                    operator=FilterOperator.REGEX,
                    value=f"({'|'.join(item_types)})"
                )
            )
        
        # Фильтр по требуемым статам
        for stat in required_stats:
            conditions.append(
                FilterCondition(
                    field="item.explicit_mods",
                    operator=FilterOperator.REGEX,
                    value=stat
                )
            )
        
        # Фильтр по цене
        if max_price:
            conditions.append(
                FilterCondition(
                    field="price_chaos",
                    operator=FilterOperator.LESS_EQUAL,
                    value=max_price
                )
            )
        
        return FilterRule(
            name=f"{build_name} Build Filter",
            description=f"Items suitable for {build_name} build",
            conditions=conditions,
            logic="and",
            priority=100
        )