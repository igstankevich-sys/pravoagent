"""
Russian Post Mock — заглушка API Почты России.
Часть Part 12.10 плана.
"""


class RussianPostMock:
    """Заглушка Почты России для демо-режима."""

    def create_shipment(self, recipient: str, address: str, documents: list[str]) -> dict:
        """Создание отправления.

        Args:
            recipient: ФИО или наименование получателя.
            address: Адрес доставки.
            documents: Список документов для отправки.

        Returns:
            dict: Информация о созданном отправлении с tracking_number.
        """
        return {
            "status": "demo",
            "tracking_number": "DEMO-1234567890",
            "recipient": recipient,
            "address": address,
            "documents": documents,
            "estimated_delivery": "5-7 рабочих дней",
            "message": "[ДЕМО] В production — интеграция с API Почты России",
        }

    def get_status(self, tracking_number: str) -> dict:
        """Получение статуса отправления.

        Args:
            tracking_number: Трек-номер отправления.

        Returns:
            dict: Текущий статус, местоположение и время.
        """
        return {
            "tracking_number": tracking_number,
            "status": "in_transit",
            "location": "Москва",
            "timestamp": "2026-06-25T10:00:00Z",
            "mode": "demo",
        }
