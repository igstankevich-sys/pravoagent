"""
Configuration Service — управление настройками KPI метрик для тенанта.
Configuration Agent (Phase 10 — отложенная часть).
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.models.base import KpiMetricConfig


DEFAULT_METRICS = [
    {
        "metric_key": "efficiency",
        "metric_label": "Эффективность",
        "metric_description": "Процент выигранных / закрытых дел",
        "target_value": 80.0,
        "comparison": "gte",
        "is_custom": False,
        "sort_order": 1,
    },
    {
        "metric_key": "users",
        "metric_label": "Количество юристов",
        "metric_description": "Общее число активных юристов в отделе",
        "target_value": None,
        "comparison": "gte",
        "is_custom": False,
        "sort_order": 2,
    },
    {
        "metric_key": "duration",
        "metric_label": "Средний срок дела",
        "metric_description": "Среднее время от открытия до закрытия дела",
        "target_value": 90.0,
        "comparison": "lte",
        "is_custom": False,
        "sort_order": 3,
    },
    {
        "metric_key": "documents",
        "metric_label": "Количество документов",
        "metric_description": "Общее число созданных заключений и документов",
        "target_value": None,
        "comparison": "gte",
        "is_custom": False,
        "sort_order": 4,
    },
    {
        "metric_key": "case-chart",
        "metric_label": "График по делам",
        "metric_description": "Визуализация статусов дел (открыто / в работе / закрыто)",
        "target_value": None,
        "comparison": "gte",
        "is_custom": False,
        "sort_order": 5,
    },
    {
        "metric_key": "team-table",
        "metric_label": "Таблица загрузки",
        "metric_description": "Детальная таблица загрузки каждого юриста",
        "target_value": None,
        "comparison": "gte",
        "is_custom": False,
        "sort_order": 6,
    },
]


class ConfigurationService:
    """Сервис управления конфигурацией KPI метрик для тенанта.

    Позволяет получать, обновлять, добавлять и удалять метрики,
    а также управлять их видимостью и целевыми значениями.
    """

    def get_kpi_config(self, db: Session, tenant_id: int) -> List[Dict]:
        """Получение всех метрик KPI для тенанта.

        Если конфигурация ещё не создана — создаёт дефолтный набор.

        Args:
            db: Сессия SQLAlchemy.
            tenant_id: ID тенанта.

        Returns:
            Список словарей с настройками метрик.
        """
        configs = (
            db.query(KpiMetricConfig)
            .filter(KpiMetricConfig.tenant_id == tenant_id)
            .order_by(KpiMetricConfig.sort_order)
            .all()
        )

        if not configs:
            configs = self.create_default_config(db, tenant_id)

        return [self._metric_to_dict(m) for m in configs]

    def update_kpi_config(
        self, db: Session, tenant_id: int, metrics: List[Dict]
    ) -> List[Dict]:
        """Полная замена конфигурации KPI метрик для тенанта.

        Args:
            db: Сессия SQLAlchemy.
            tenant_id: ID тенанта.
            metrics: Список словарей с полями метрик.

        Returns:
            Обновлённый список метрик.
        """
        existing = (
            db.query(KpiMetricConfig)
            .filter(KpiMetricConfig.tenant_id == tenant_id)
            .all()
        )
        for m in existing:
            db.delete(m)
        db.flush()

        result = []
        for idx, m in enumerate(metrics):
            config = KpiMetricConfig(
                tenant_id=tenant_id,
                metric_key=m.get("metric_key", f"custom_{idx}"),
                metric_label=m.get("metric_label", "Метрика"),
                metric_description=m.get("metric_description", ""),
                target_value=m.get("target_value"),
                comparison=m.get("comparison", "gte"),
                is_custom=m.get("is_custom", False),
                formula=m.get("formula"),
                is_enabled=m.get("is_enabled", True),
                sort_order=m.get("sort_order", idx),
            )
            db.add(config)
            result.append(config)
        db.commit()

        return [self._metric_to_dict(m) for m in result]

    def toggle_kpi_metric(
        self, db: Session, tenant_id: int, config_id: int, is_enabled: bool
    ) -> Optional[Dict]:
        """Включение/выключение метрики KPI.

        Args:
            db: Сессия SQLAlchemy.
            tenant_id: ID тенанта (для проверки принадлежности).
            config_id: ID конфигурации метрики.
            is_enabled: Новое состояние (включена/выключена).

        Returns:
            Словарь с обновлённой метрикой или None если не найдена.
        """
        config = (
            db.query(KpiMetricConfig)
            .filter(KpiMetricConfig.id == config_id)
            .filter(KpiMetricConfig.tenant_id == tenant_id)
            .first()
        )
        if not config:
            return None

        config.is_enabled = is_enabled
        db.commit()
        db.refresh(config)

        return self._metric_to_dict(config)

    def add_custom_metric(
        self, db: Session, tenant_id: int, data: Dict
    ) -> Dict:
        """Добавление кастомной метрики KPI.

        Args:
            db: Сессия SQLAlchemy.
            tenant_id: ID тенанта.
            data: Данные метрики (metric_label, metric_description,
                  target_value, comparison, formula).

        Returns:
            Словарь с созданной метрикой.
        """
        max_sort = (
            db.query(KpiMetricConfig.sort_order)
            .filter(KpiMetricConfig.tenant_id == tenant_id)
            .order_by(KpiMetricConfig.sort_order.desc())
            .first()
        )
        next_sort = (max_sort[0] + 1) if max_sort and max_sort[0] else 1

        config = KpiMetricConfig(
            tenant_id=tenant_id,
            metric_key=data.get("metric_key", f"custom_{next_sort}"),
            metric_label=data.get("metric_label", "Новая метрика"),
            metric_description=data.get("metric_description", ""),
            target_value=data.get("target_value"),
            comparison=data.get("comparison", "gte"),
            is_custom=True,
            formula=data.get("formula"),
            is_enabled=True,
            sort_order=next_sort,
        )
        db.add(config)
        db.commit()
        db.refresh(config)

        return self._metric_to_dict(config)

    def delete_kpi_metric(self, db: Session, tenant_id: int, config_id: int) -> bool:
        """Удаление кастомной метрики KPI.

        Args:
            db: Сессия SQLAlchemy.
            tenant_id: ID тенанта (для проверки принадлежности).
            config_id: ID конфигурации метрики.

        Returns:
            True если удалена, False если не найдена или не кастомная.
        """
        config = (
            db.query(KpiMetricConfig)
            .filter(KpiMetricConfig.id == config_id)
            .filter(KpiMetricConfig.tenant_id == tenant_id)
            .first()
        )
        if not config:
            return False

        if not config.is_custom:
            return False

        db.delete(config)
        db.commit()
        return True

    def create_default_config(
        self, db: Session, tenant_id: int
    ) -> List[KpiMetricConfig]:
        """Создание дефолтного набора метрик KPI для тенанта.

        Args:
            db: Сессия SQLAlchemy.
            tenant_id: ID тенанта.

        Returns:
            Список созданных объектов KpiMetricConfig.
        """
        configs = []
        for idx, m in enumerate(DEFAULT_METRICS):
            config = KpiMetricConfig(
                tenant_id=tenant_id,
                metric_key=m["metric_key"],
                metric_label=m["metric_label"],
                metric_description=m["metric_description"],
                target_value=m["target_value"],
                comparison=m["comparison"],
                is_custom=m["is_custom"],
                is_enabled=True,
                sort_order=m.get("sort_order", idx),
            )
            db.add(config)
            configs.append(config)
        db.commit()

        for c in configs:
            db.refresh(c)

        return configs

    def _metric_to_dict(self, metric: KpiMetricConfig) -> Dict:
        """Сериализация объекта KpiMetricConfig в словарь.

        Args:
            metric: Объект KpiMetricConfig.

        Returns:
            Словарь с данными метрики.
        """
        return {
            "id": metric.id,
            "tenant_id": metric.tenant_id,
            "metric_key": metric.metric_key,
            "metric_label": metric.metric_label,
            "metric_description": metric.metric_description,
            "target_value": metric.target_value,
            "comparison": metric.comparison,
            "is_custom": metric.is_custom,
            "formula": metric.formula,
            "is_enabled": metric.is_enabled,
            "sort_order": metric.sort_order,
        }
