"""
Анализатор цен предметов
"""

import statistics
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from api.models import SearchResult, PriceData

logger = logging.getLogger(__name__)


class PriceStats:
    """Статистика цен"""
    
    def __init__(self, prices: List[float]):
        self.prices = sorted(prices)
        self.count = len(prices)
        
        if self.count > 0:
            self.min_price = min(prices)
            self.max_price = max(prices)
            self.mean_price = statistics.mean(prices)
            self.median_price = statistics.median(prices)
            
            if self.count > 1:
                self.std_dev = statistics.stdev(prices)
            else:
                self.std_dev = 0.0
                
            # Квартили
            self.q1 = self._percentile(prices, 25)
            self.q3 = self._percentile(prices, 75)
            
            # Выбросы (outliers)
            iqr = self.q3 - self.q1
            self.outlier_threshold_low = self.q1 - 1.5 * iqr
            self.outlier_threshold_high = self.q3 + 1.5 * iqr
            
        else:
            self.min_price = 0
            self.max_price = 0
            self.mean_price = 0
            self.median_price = 0
            self.std_dev = 0
            self.q1 = 0
            self.q3 = 0
            self.outlier_threshold_low = 0
            self.outlier_threshold_high = 0
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Вычислить процентиль"""
        if not data:
            return 0
        
        k = (len(data) - 1) * (percentile / 100)
        f = int(k)
        c = k - f
        
        if f == len(data) - 1:
            return data[f]
        
        return data[f] * (1 - c) + data[f + 1] * c
    
    def is_outlier(self, price: float) -> bool:
        """Проверить, является ли цена выбросом"""
        return price < self.outlier_threshold_low or price > self.outlier_threshold_high
    
    def price_category(self, price: float) -> str:
        """Определить категорию цены"""
        if self.is_outlier(price):
            if price < self.outlier_threshold_low:
                return "very_cheap"
            else:
                return "very_expensive"
        elif price <= self.q1:
            return "cheap"
        elif price <= self.median_price:
            return "below_average"
        elif price <= self.q3:
            return "above_average"
        else:
            return "expensive"


class PriceAnalyzer:
    """Анализатор цен предметов"""
    
    def __init__(self):
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
    
    def analyze_prices(self, results: List[SearchResult], currency: str = "chaos") -> PriceStats:
        """Анализ цен из результатов поиска"""
        prices = []
        
        for result in results:
            if result.price:
                if currency == "chaos":
                    price = result.price_chaos
                else:
                    # Конвертируем в указанную валюту (упрощенно)
                    price = result.price.amount if result.price.currency == currency else None
                
                if price is not None and price > 0:
                    prices.append(price)
        
        return PriceStats(prices)
    
    def find_good_deals(self, results: List[SearchResult], threshold: float = 0.8) -> List[SearchResult]:
        """Найти выгодные предложения (цена ниже среднего * threshold)"""
        stats = self.analyze_prices(results)
        
        if stats.count == 0:
            return []
        
        threshold_price = stats.mean_price * threshold
        good_deals = []
        
        for result in results:
            if result.price_chaos and result.price_chaos <= threshold_price:
                good_deals.append(result)
        
        # Сортируем по цене
        good_deals.sort(key=lambda x: x.price_chaos or 0)
        
        logger.info(f"Found {len(good_deals)} good deals below {threshold_price:.1f} chaos")
        return good_deals
    
    def compare_prices(
        self, 
        item_name: str, 
        current_results: List[SearchResult],
        historical_data: Optional[List[Tuple[datetime, float]]] = None
    ) -> Dict[str, Any]:
        """Сравнить текущие цены с историческими данными"""
        
        current_stats = self.analyze_prices(current_results)
        comparison = {
            "item_name": item_name,
            "current_stats": current_stats,
            "historical_stats": None,
            "price_change": None,
            "trend": "unknown"
        }
        
        if historical_data and len(historical_data) > 0:
            historical_prices = [price for _, price in historical_data]
            historical_stats = PriceStats(historical_prices)
            
            comparison["historical_stats"] = historical_stats
            
            if historical_stats.mean_price > 0:
                price_change = (current_stats.mean_price - historical_stats.mean_price) / historical_stats.mean_price
                comparison["price_change"] = price_change
                
                if price_change > 0.1:
                    comparison["trend"] = "rising"
                elif price_change < -0.1:
                    comparison["trend"] = "falling"
                else:
                    comparison["trend"] = "stable"
        
        return comparison
    
    def detect_price_anomalies(self, results: List[SearchResult]) -> Dict[str, List[SearchResult]]:
        """Обнаружить аномалии в ценах"""
        stats = self.analyze_prices(results)
        
        anomalies = {
            "very_cheap": [],
            "very_expensive": [],
            "potential_errors": []
        }
        
        for result in results:
            if not result.price_chaos:
                continue
            
            price = result.price_chaos
            category = stats.price_category(price)
            
            if category == "very_cheap":
                anomalies["very_cheap"].append(result)
            elif category == "very_expensive":
                anomalies["very_expensive"].append(result)
            
            # Дополнительная проверка на потенциальные ошибки
            if price < 0.01 or price > stats.mean_price * 100:
                anomalies["potential_errors"].append(result)
        
        return anomalies
    
    def calculate_fair_price(self, results: List[SearchResult], method: str = "median") -> Optional[float]:
        """Вычислить справедливую цену предмета"""
        stats = self.analyze_prices(results)
        
        if stats.count == 0:
            return None
        
        if method == "median":
            return stats.median_price
        elif method == "mean":
            return stats.mean_price
        elif method == "trimmed_mean":
            # Урезанное среднее (исключаем выбросы)
            filtered_prices = [p for p in stats.prices if not stats.is_outlier(p)]
            return statistics.mean(filtered_prices) if filtered_prices else stats.median_price
        elif method == "mode":
            try:
                return statistics.mode(stats.prices)
            except statistics.StatisticsError:
                return stats.median_price
        else:
            return stats.median_price
    
    def add_price_history(self, item_name: str, price: float, timestamp: Optional[datetime] = None):
        """Добавить цену в историю"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if item_name not in self.price_history:
            self.price_history[item_name] = []
        
        self.price_history[item_name].append((timestamp, price))
        
        # Ограничиваем историю (например, последние 1000 записей)
        if len(self.price_history[item_name]) > 1000:
            self.price_history[item_name] = self.price_history[item_name][-1000:]
    
    def get_price_history(self, item_name: str, days: int = 7) -> List[Tuple[datetime, float]]:
        """Получить историю цен за указанный период"""
        if item_name not in self.price_history:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return [
            (timestamp, price) 
            for timestamp, price in self.price_history[item_name]
            if timestamp >= cutoff_date
        ]
    
    def generate_price_report(self, results: List[SearchResult], item_name: str = "Unknown") -> Dict[str, Any]:
        """Сгенерировать отчет по ценам"""
        stats = self.analyze_prices(results)
        anomalies = self.detect_price_anomalies(results)
        good_deals = self.find_good_deals(results)
        fair_price = self.calculate_fair_price(results, "trimmed_mean")
        
        report = {
            "item_name": item_name,
            "timestamp": datetime.now().isoformat(),
            "total_listings": len(results),
            "valid_prices": stats.count,
            "price_stats": {
                "min": stats.min_price,
                "max": stats.max_price,
                "mean": stats.mean_price,
                "median": stats.median_price,
                "std_dev": stats.std_dev,
                "q1": stats.q1,
                "q3": stats.q3
            },
            "fair_price": fair_price,
            "anomalies": {
                "very_cheap_count": len(anomalies["very_cheap"]),
                "very_expensive_count": len(anomalies["very_expensive"]),
                "potential_errors_count": len(anomalies["potential_errors"])
            },
            "good_deals_count": len(good_deals),
            "recommendations": self._generate_recommendations(stats, anomalies, good_deals)
        }
        
        return report
    
    def _generate_recommendations(
        self, 
        stats: PriceStats, 
        anomalies: Dict[str, List[SearchResult]], 
        good_deals: List[SearchResult]
    ) -> List[str]:
        """Сгенерировать рекомендации на основе анализа"""
        recommendations = []
        
        if len(good_deals) > 0:
            recommendations.append(f"Найдено {len(good_deals)} выгодных предложений")
        
        if len(anomalies["very_cheap"]) > 0:
            recommendations.append(f"Обратите внимание на {len(anomalies['very_cheap'])} очень дешевых предметов - возможно, это выгодные покупки")
        
        if len(anomalies["potential_errors"]) > 0:
            recommendations.append(f"Найдено {len(anomalies['potential_errors'])} подозрительных цен - проверьте их вручную")
        
        if stats.std_dev > stats.mean_price * 0.5:
            recommendations.append("Цены сильно варьируются - рынок нестабилен")
        
        if stats.count < 5:
            recommendations.append("Мало предложений на рынке - цены могут быть неточными")
        
        return recommendations