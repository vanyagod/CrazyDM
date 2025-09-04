"""
Система фильтрации предметов
"""

import re
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel
import logging

from api.models import Item, SearchResult

logger = logging.getLogger(__name__)


class FilterOperator(str, Enum):
    """Операторы для фильтров"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER = "gt"
    GREATER_EQUAL = "gte"
    LESS = "lt"
    LESS_EQUAL = "lte"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX = "regex"
    IN = "in"
    NOT_IN = "not_in"


class FilterCondition(BaseModel):
    """Условие фильтрации"""
    field: str  # Поле для проверки (например, "name", "price.amount", "item.ilvl")
    operator: FilterOperator
    value: Union[str, int, float, List[Any]]
    case_sensitive: bool = False
    
    def evaluate(self, obj: Any) -> bool:
        """Проверить условие на объекте"""
        try:
            # Получаем значение поля из объекта
            field_value = self._get_field_value(obj, self.field)
            
            # Специальная обработка для проверки на None
            if self.operator == FilterOperator.NOT_EQUALS and self.value is None:
                return field_value is not None
            elif self.operator == FilterOperator.EQUALS and self.value is None:
                return field_value is None
            
            if field_value is None and self.value is not None:
                return False
            
            # Применяем оператор
            return self._apply_operator(field_value, self.operator, self.value)
            
        except Exception as e:
            logger.warning(f"Error evaluating filter condition {self.field} {self.operator} {self.value}: {e}")
            return False
    
    def _get_field_value(self, obj: Any, field_path: str) -> Any:
        """Получить значение поля по пути (поддерживает вложенные поля)"""
        parts = field_path.split(".")
        current = obj
        
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _apply_operator(self, field_value: Any, operator: FilterOperator, filter_value: Any) -> bool:
        """Применить оператор сравнения"""
        
        # Обработка строк с учетом регистра
        if isinstance(field_value, str) and isinstance(filter_value, str) and not self.case_sensitive:
            field_value = field_value.lower()
            filter_value = filter_value.lower()
        
        if operator == FilterOperator.EQUALS:
            return field_value == filter_value
        
        elif operator == FilterOperator.NOT_EQUALS:
            return field_value != filter_value
        
        elif operator == FilterOperator.GREATER:
            return field_value > filter_value
        
        elif operator == FilterOperator.GREATER_EQUAL:
            return field_value >= filter_value
        
        elif operator == FilterOperator.LESS:
            return field_value < filter_value
        
        elif operator == FilterOperator.LESS_EQUAL:
            return field_value <= filter_value
        
        elif operator == FilterOperator.CONTAINS:
            return str(filter_value) in str(field_value)
        
        elif operator == FilterOperator.NOT_CONTAINS:
            return str(filter_value) not in str(field_value)
        
        elif operator == FilterOperator.REGEX:
            pattern = re.compile(str(filter_value), re.IGNORECASE if not self.case_sensitive else 0)
            return bool(pattern.search(str(field_value)))
        
        elif operator == FilterOperator.IN:
            return field_value in filter_value
        
        elif operator == FilterOperator.NOT_IN:
            return field_value not in filter_value
        
        else:
            raise ValueError(f"Unknown operator: {operator}")


class FilterRule(BaseModel):
    """Правило фильтрации"""
    name: str
    description: Optional[str] = None
    conditions: List[FilterCondition]
    logic: str = "and"  # "and" или "or"
    enabled: bool = True
    priority: int = 0  # Приоритет применения (больше = выше приоритет)
    
    def matches(self, item: SearchResult) -> bool:
        """Проверить, соответствует ли предмет правилу"""
        if not self.enabled or not self.conditions:
            return True
        
        results = [condition.evaluate(item) for condition in self.conditions]
        
        if self.logic == "and":
            return all(results)
        elif self.logic == "or":
            return any(results)
        else:
            raise ValueError(f"Unknown logic operator: {self.logic}")


class ItemFilter:
    """Основной класс для фильтрации предметов"""
    
    def __init__(self):
        self.rules: List[FilterRule] = []
        self.whitelist_rules: List[FilterRule] = []  # Правила белого списка (всегда пропускать)
        self.blacklist_rules: List[FilterRule] = []  # Правила черного списка (всегда блокировать)
    
    def add_rule(self, rule: FilterRule, rule_type: str = "filter"):
        """Добавить правило фильтрации"""
        if rule_type == "whitelist":
            self.whitelist_rules.append(rule)
        elif rule_type == "blacklist":
            self.blacklist_rules.append(rule)
        else:
            self.rules.append(rule)
        
        # Сортируем по приоритету
        self._sort_rules()
    
    def remove_rule(self, rule_name: str):
        """Удалить правило по имени"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        self.whitelist_rules = [r for r in self.whitelist_rules if r.name != rule_name]
        self.blacklist_rules = [r for r in self.blacklist_rules if r.name != rule_name]
    
    def _sort_rules(self):
        """Сортировать правила по приоритету"""
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        self.whitelist_rules.sort(key=lambda r: r.priority, reverse=True)
        self.blacklist_rules.sort(key=lambda r: r.priority, reverse=True)
    
    def filter_items(self, items: List[SearchResult]) -> List[SearchResult]:
        """Отфильтровать список предметов"""
        filtered = []
        
        for item in items:
            if self.should_include(item):
                filtered.append(item)
        
        logger.info(f"Filtered {len(items)} items down to {len(filtered)}")
        return filtered
    
    def should_include(self, item: SearchResult) -> bool:
        """Определить, должен ли предмет быть включен в результаты"""
        
        # Сначала проверяем черный список
        for rule in self.blacklist_rules:
            if rule.matches(item):
                logger.debug(f"Item blocked by blacklist rule: {rule.name}")
                return False
        
        # Затем проверяем белый список
        for rule in self.whitelist_rules:
            if rule.matches(item):
                logger.debug(f"Item allowed by whitelist rule: {rule.name}")
                return True
        
        # Если нет правил белого списка, проверяем обычные фильтры
        if not self.whitelist_rules:
            for rule in self.rules:
                if not rule.matches(item):
                    logger.debug(f"Item filtered out by rule: {rule.name}")
                    return False
        
        return True
    
    def get_matching_rules(self, item: SearchResult) -> List[FilterRule]:
        """Получить все правила, которым соответствует предмет"""
        matching = []
        
        for rule_list in [self.whitelist_rules, self.blacklist_rules, self.rules]:
            for rule in rule_list:
                if rule.matches(item):
                    matching.append(rule)
        
        return matching
    
    def export_rules(self) -> Dict[str, Any]:
        """Экспортировать правила в словарь"""
        return {
            "rules": [rule.dict() for rule in self.rules],
            "whitelist_rules": [rule.dict() for rule in self.whitelist_rules],
            "blacklist_rules": [rule.dict() for rule in self.blacklist_rules]
        }
    
    def import_rules(self, data: Dict[str, Any]):
        """Импортировать правила из словаря"""
        self.rules = [FilterRule(**rule) for rule in data.get("rules", [])]
        self.whitelist_rules = [FilterRule(**rule) for rule in data.get("whitelist_rules", [])]
        self.blacklist_rules = [FilterRule(**rule) for rule in data.get("blacklist_rules", [])]
        
        self._sort_rules()
    
    def clear_rules(self):
        """Очистить все правила"""
        self.rules.clear()
        self.whitelist_rules.clear()
        self.blacklist_rules.clear()