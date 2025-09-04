"""
Советник по покупкам (образовательный модуль)

⚠️ ВАЖНО: Этот модуль создан исключительно в образовательных целях.
Автоматическая покупка предметов может нарушать правила игры.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from api.models import SearchResult
from analysis.price_analyzer import PriceAnalyzer
from filters.item_filter import ItemFilter

logger = logging.getLogger(__name__)


class PurchaseDecision(str, Enum):
    """Решения по покупке"""
    BUY = "buy"
    WAIT = "wait"
    SKIP = "skip"
    INVESTIGATE = "investigate"


class PurchaseRecommendation:
    """Рекомендация по покупке"""
    
    def __init__(
        self,
        item: SearchResult,
        decision: PurchaseDecision,
        confidence: float,
        reasons: List[str],
        estimated_fair_price: Optional[float] = None
    ):
        self.item = item
        self.decision = decision
        self.confidence = confidence  # 0.0 - 1.0
        self.reasons = reasons
        self.estimated_fair_price = estimated_fair_price
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"PurchaseRecommendation({self.decision}, confidence={self.confidence:.2f})"


class PurchaseAdvisor:
    """
    Советник по покупкам - анализирует предметы и дает рекомендации
    
    ⚠️ ОБРАЗОВАТЕЛЬНЫЙ МОДУЛЬ - НЕ ДЛЯ АВТОМАТИЧЕСКОЙ ТОРГОВЛИ!
    """
    
    def __init__(self, price_analyzer: PriceAnalyzer, item_filter: ItemFilter):
        self.price_analyzer = price_analyzer
        self.item_filter = item_filter
        
        # Настройки анализа
        self.good_deal_threshold = 0.8  # Цена ниже 80% от средней считается выгодной
        self.excellent_deal_threshold = 0.6  # Цена ниже 60% от средней - отличная сделка
        self.overpriced_threshold = 1.5  # Цена выше 150% от средней - переплата
        
        # История рекомендаций
        self.recommendation_history: List[PurchaseRecommendation] = []
    
    def analyze_purchase_opportunity(
        self, 
        item: SearchResult, 
        market_data: List[SearchResult]
    ) -> PurchaseRecommendation:
        """Анализ возможности покупки предмета"""
        
        reasons = []
        confidence = 0.5
        decision = PurchaseDecision.SKIP
        
        # Анализ цены
        price_analysis = self._analyze_price(item, market_data)
        reasons.extend(price_analysis["reasons"])
        confidence += price_analysis["confidence_modifier"]
        
        # Анализ качества предмета
        quality_analysis = self._analyze_item_quality(item)
        reasons.extend(quality_analysis["reasons"])
        confidence += quality_analysis["confidence_modifier"]
        
        # Анализ рыночных условий
        market_analysis = self._analyze_market_conditions(market_data)
        reasons.extend(market_analysis["reasons"])
        confidence += market_analysis["confidence_modifier"]
        
        # Проверка фильтров
        filter_analysis = self._check_filters(item)
        reasons.extend(filter_analysis["reasons"])
        confidence += filter_analysis["confidence_modifier"]
        
        # Нормализуем уверенность
        confidence = max(0.0, min(1.0, confidence))
        
        # Принимаем решение
        decision = self._make_decision(item, market_data, confidence, reasons)
        
        # Оценка справедливой цены
        fair_price = self.price_analyzer.calculate_fair_price(market_data, "trimmed_mean")
        
        recommendation = PurchaseRecommendation(
            item=item,
            decision=decision,
            confidence=confidence,
            reasons=reasons,
            estimated_fair_price=fair_price
        )
        
        self.recommendation_history.append(recommendation)
        
        # Ограничиваем историю
        if len(self.recommendation_history) > 1000:
            self.recommendation_history = self.recommendation_history[-1000:]
        
        return recommendation
    
    def _analyze_price(self, item: SearchResult, market_data: List[SearchResult]) -> Dict[str, Any]:
        """Анализ цены предмета"""
        reasons = []
        confidence_modifier = 0.0
        
        if not item.price_chaos:
            reasons.append("Цена не указана")
            return {"reasons": reasons, "confidence_modifier": -0.3}
        
        stats = self.price_analyzer.analyze_prices(market_data)
        
        if stats.count < 3:
            reasons.append("Недостаточно данных для анализа цены")
            confidence_modifier -= 0.2
        else:
            price_ratio = item.price_chaos / stats.mean_price if stats.mean_price > 0 else 1.0
            
            if price_ratio <= self.excellent_deal_threshold:
                reasons.append(f"Отличная цена! На {(1-price_ratio)*100:.1f}% ниже средней")
                confidence_modifier += 0.4
            elif price_ratio <= self.good_deal_threshold:
                reasons.append(f"Выгодная цена! На {(1-price_ratio)*100:.1f}% ниже средней")
                confidence_modifier += 0.2
            elif price_ratio >= self.overpriced_threshold:
                reasons.append(f"Завышенная цена! На {(price_ratio-1)*100:.1f}% выше средней")
                confidence_modifier -= 0.3
            else:
                reasons.append("Цена близка к рыночной")
        
        return {"reasons": reasons, "confidence_modifier": confidence_modifier}
    
    def _analyze_item_quality(self, item: SearchResult) -> Dict[str, Any]:
        """Анализ качества предмета"""
        reasons = []
        confidence_modifier = 0.0
        
        # Проверка уровня предмета
        if item.item.ilvl:
            if item.item.ilvl >= 85:
                reasons.append(f"Высокий уровень предмета: {item.item.ilvl}")
                confidence_modifier += 0.1
            elif item.item.ilvl < 70:
                reasons.append(f"Низкий уровень предмета: {item.item.ilvl}")
                confidence_modifier -= 0.1
        
        # Проверка редкости
        if item.item.frame_type == 3:  # Unique
            reasons.append("Уникальный предмет")
            confidence_modifier += 0.1
        elif item.item.frame_type == 2:  # Rare
            reasons.append("Редкий предмет")
            confidence_modifier += 0.05
        
        # Проверка коррупции
        if item.item.corrupted:
            reasons.append("Предмет коррумпирован (нельзя изменить)")
            confidence_modifier -= 0.05
        
        # Проверка связей сокетов
        if item.item.socket_links:
            if item.item.socket_links >= 6:
                reasons.append(f"Отличные связи сокетов: {item.item.socket_links}")
                confidence_modifier += 0.2
            elif item.item.socket_links >= 4:
                reasons.append(f"Хорошие связи сокетов: {item.item.socket_links}")
                confidence_modifier += 0.1
        
        return {"reasons": reasons, "confidence_modifier": confidence_modifier}
    
    def _analyze_market_conditions(self, market_data: List[SearchResult]) -> Dict[str, Any]:
        """Анализ рыночных условий"""
        reasons = []
        confidence_modifier = 0.0
        
        if len(market_data) < 5:
            reasons.append("Мало предложений на рынке - высокий риск")
            confidence_modifier -= 0.2
        elif len(market_data) > 50:
            reasons.append("Много предложений на рынке - стабильные цены")
            confidence_modifier += 0.1
        
        # Анализ распределения цен
        stats = self.price_analyzer.analyze_prices(market_data)
        
        if stats.std_dev > stats.mean_price * 0.5:
            reasons.append("Цены сильно варьируются - нестабильный рынок")
            confidence_modifier -= 0.1
        else:
            reasons.append("Стабильные цены на рынке")
            confidence_modifier += 0.05
        
        return {"reasons": reasons, "confidence_modifier": confidence_modifier}
    
    def _check_filters(self, item: SearchResult) -> Dict[str, Any]:
        """Проверка соответствия фильтрам"""
        reasons = []
        confidence_modifier = 0.0
        
        if self.item_filter.should_include(item):
            matching_rules = self.item_filter.get_matching_rules(item)
            
            # Проверяем приоритетные правила
            high_priority_rules = [r for r in matching_rules if r.priority >= 90]
            if high_priority_rules:
                reasons.append(f"Соответствует приоритетным фильтрам: {', '.join(r.name for r in high_priority_rules)}")
                confidence_modifier += 0.2
            
            # Проверяем белый список
            whitelist_matches = [r for r in matching_rules if r in self.item_filter.whitelist_rules]
            if whitelist_matches:
                reasons.append("Предмет в белом списке")
                confidence_modifier += 0.3
        else:
            reasons.append("Предмет не прошел фильтрацию")
            confidence_modifier -= 0.4
        
        return {"reasons": reasons, "confidence_modifier": confidence_modifier}
    
    def _make_decision(
        self, 
        item: SearchResult, 
        market_data: List[SearchResult], 
        confidence: float, 
        reasons: List[str]
    ) -> PurchaseDecision:
        """Принятие решения о покупке"""
        
        # Если предмет не прошел фильтры
        if not self.item_filter.should_include(item):
            return PurchaseDecision.SKIP
        
        # Если нет цены
        if not item.price_chaos:
            return PurchaseDecision.INVESTIGATE
        
        # Анализ цены
        stats = self.price_analyzer.analyze_prices(market_data)
        
        if stats.count > 0:
            price_ratio = item.price_chaos / stats.mean_price if stats.mean_price > 0 else 1.0
            
            # Отличная сделка с высокой уверенностью
            if price_ratio <= self.excellent_deal_threshold and confidence >= 0.7:
                return PurchaseDecision.BUY
            
            # Выгодная сделка с хорошей уверенностью
            elif price_ratio <= self.good_deal_threshold and confidence >= 0.6:
                return PurchaseDecision.BUY
            
            # Подозрительно дешево - нужно проверить
            elif price_ratio <= 0.3:
                return PurchaseDecision.INVESTIGATE
            
            # Слишком дорого
            elif price_ratio >= self.overpriced_threshold:
                return PurchaseDecision.SKIP
            
            # Средняя цена - ждем лучшего предложения
            else:
                return PurchaseDecision.WAIT
        
        # По умолчанию
        if confidence >= 0.7:
            return PurchaseDecision.BUY
        elif confidence >= 0.4:
            return PurchaseDecision.WAIT
        else:
            return PurchaseDecision.SKIP
    
    def get_purchase_recommendations(
        self, 
        items: List[SearchResult], 
        market_data: List[SearchResult]
    ) -> List[PurchaseRecommendation]:
        """Получить рекомендации по покупке для списка предметов"""
        
        recommendations = []
        
        for item in items:
            try:
                recommendation = self.analyze_purchase_opportunity(item, market_data)
                recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"Failed to analyze item {item.item.name}: {e}")
        
        # Сортируем по уверенности и решению
        recommendations.sort(
            key=lambda r: (
                r.decision == PurchaseDecision.BUY,
                r.confidence
            ),
            reverse=True
        )
        
        return recommendations
    
    def get_buy_recommendations(self, recommendations: List[PurchaseRecommendation]) -> List[PurchaseRecommendation]:
        """Получить только рекомендации к покупке"""
        return [r for r in recommendations if r.decision == PurchaseDecision.BUY]
    
    def generate_purchase_report(self, recommendations: List[PurchaseRecommendation]) -> Dict[str, Any]:
        """Сгенерировать отчет по рекомендациям"""
        
        by_decision = {}
        for decision in PurchaseDecision:
            by_decision[decision.value] = [r for r in recommendations if r.decision == decision]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(recommendations),
            "summary": {
                "buy": len(by_decision["buy"]),
                "wait": len(by_decision["wait"]),
                "skip": len(by_decision["skip"]),
                "investigate": len(by_decision["investigate"])
            },
            "top_recommendations": [
                {
                    "item_name": r.item.item.name,
                    "decision": r.decision.value,
                    "confidence": r.confidence,
                    "price": r.item.price_chaos,
                    "fair_price": r.estimated_fair_price,
                    "reasons": r.reasons[:3]  # Топ-3 причины
                }
                for r in recommendations[:10]  # Топ-10 рекомендаций
            ]
        }
        
        return report
    
    def update_settings(
        self,
        good_deal_threshold: Optional[float] = None,
        excellent_deal_threshold: Optional[float] = None,
        overpriced_threshold: Optional[float] = None
    ):
        """Обновить настройки анализа"""
        
        if good_deal_threshold is not None:
            self.good_deal_threshold = good_deal_threshold
        
        if excellent_deal_threshold is not None:
            self.excellent_deal_threshold = excellent_deal_threshold
        
        if overpriced_threshold is not None:
            self.overpriced_threshold = overpriced_threshold
        
        logger.info(f"Updated purchase advisor settings: "
                   f"good={self.good_deal_threshold}, "
                   f"excellent={self.excellent_deal_threshold}, "
                   f"overpriced={self.overpriced_threshold}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику рекомендаций"""
        
        if not self.recommendation_history:
            return {"total": 0}
        
        recent = [r for r in self.recommendation_history 
                 if r.timestamp > datetime.now() - timedelta(days=7)]
        
        stats = {
            "total": len(self.recommendation_history),
            "recent_7_days": len(recent),
            "decisions": {},
            "average_confidence": 0.0
        }
        
        for decision in PurchaseDecision:
            count = len([r for r in recent if r.decision == decision])
            stats["decisions"][decision.value] = count
        
        if recent:
            stats["average_confidence"] = sum(r.confidence for r in recent) / len(recent)
        
        return stats