"""
Базовые тесты для PoE2 Trade Assistant
"""

import unittest
import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.settings import Settings
from filters.item_filter import ItemFilter, FilterRule, FilterCondition, FilterOperator
from api.models import Item, SearchResult, PriceData


class TestSettings(unittest.TestCase):
    """Тесты настроек"""
    
    def test_settings_creation(self):
        """Тест создания настроек"""
        settings = Settings()
        self.assertIsNotNone(settings)
        self.assertTrue(settings.poe_api_base_url)
        self.assertTrue(settings.league)
    
    def test_headers(self):
        """Тест заголовков для API"""
        settings = Settings()
        headers = settings.get_headers()
        self.assertIn("User-Agent", headers)
        self.assertIn("Accept", headers)


class TestFilters(unittest.TestCase):
    """Тесты фильтрации"""
    
    def setUp(self):
        """Подготовка для тестов"""
        self.item_filter = ItemFilter()
        
        # Создаем тестовый предмет
        test_item = Item(
            id="test_id",
            name="Test Sword",
            type_line="One Handed Sword",
            ilvl=85,
            frame_type=2,  # Rare
            corrupted=False
        )
        
        test_price = PriceData(
            amount=50.0,
            currency="chaos",
            type="fixed"
        )
        
        self.test_result = SearchResult(
            item=test_item,
            listing={},
            price=test_price
        )
    
    def test_filter_creation(self):
        """Тест создания фильтра"""
        condition = FilterCondition(
            field="item.ilvl",
            operator=FilterOperator.GREATER_EQUAL,
            value=80
        )
        
        rule = FilterRule(
            name="High iLvl",
            conditions=[condition]
        )
        
        self.item_filter.add_rule(rule)
        self.assertEqual(len(self.item_filter.rules), 1)
    
    def test_filter_matching(self):
        """Тест соответствия фильтру"""
        condition = FilterCondition(
            field="item.ilvl",
            operator=FilterOperator.GREATER_EQUAL,
            value=80
        )
        
        rule = FilterRule(
            name="High iLvl",
            conditions=[condition]
        )
        
        # Тест с подходящим предметом
        self.assertTrue(rule.matches(self.test_result))
        
        # Тест с неподходящим предметом
        self.test_result.item.ilvl = 70
        self.assertFalse(rule.matches(self.test_result))
    
    def test_price_filtering(self):
        """Тест фильтрации по цене"""
        condition = FilterCondition(
            field="price.amount",
            operator=FilterOperator.LESS_EQUAL,
            value=100.0
        )
        
        rule = FilterRule(
            name="Affordable Items",
            conditions=[condition]
        )
        
        self.assertTrue(rule.matches(self.test_result))


class TestModels(unittest.TestCase):
    """Тесты моделей данных"""
    
    def test_item_creation(self):
        """Тест создания предмета"""
        item = Item(
            id="test_id",
            name="Test Item",
            type_line="Test Type"
        )
        
        self.assertEqual(item.id, "test_id")
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.type_line, "Test Type")
    
    def test_price_data(self):
        """Тест данных о цене"""
        price = PriceData(
            amount=25.5,
            currency="chaos",
            type="fixed"
        )
        
        self.assertEqual(price.amount, 25.5)
        self.assertEqual(price.currency, "chaos")
        self.assertEqual(price.type, "fixed")
    
    def test_search_result_price_chaos(self):
        """Тест конвертации цены в хаосы"""
        item = Item(id="test", name="Test", type_line="Test")
        
        # Тест с хаосами
        price_chaos = PriceData(amount=10.0, currency="chaos")
        result = SearchResult(item=item, listing={}, price=price_chaos)
        self.assertEqual(result.price_chaos, 10.0)
        
        # Тест с дивайнами
        price_divine = PriceData(amount=1.0, currency="divine")
        result = SearchResult(item=item, listing={}, price=price_divine)
        self.assertEqual(result.price_chaos, 200.0)  # По умолчанию 1 divine = 200 chaos


if __name__ == '__main__':
    unittest.main()