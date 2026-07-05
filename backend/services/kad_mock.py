"""
KAD Mock — заглушка API КАД Арбитраж.
Часть Part 6.1 и Part 12.10 плана.
"""


class KADMock:
    """Заглушка КАД Арбитраж для демо-режима."""

    CASES = [
        {
            "number": "А40-12345/2026",
            "plaintiff": "ООО «Истец»",
            "defendant": "ООО «Ответчик»",
            "status": "pending",
            "court": "АС г. Москвы",
            "judge": "Иванова М.И.",
            "amount": 5000000,
            "next_hearing": "2026-07-15",
        },
        {
            "number": "А40-23456/2026",
            "plaintiff": "АО «Банк»",
            "defendant": "ИП Петров",
            "status": "in_progress",
            "court": "АС г. Москвы",
            "judge": "Петров А.С.",
            "amount": 12000000,
            "next_hearing": "2026-07-20",
        },
    ]

    def get_case(self, case_number: str) -> dict:
        """Получение карточки дела.

        Args:
            case_number: Номер дела в формате А40-XXXXX/YYYY.

        Returns:
            dict: Данные дела с полями number, plaintiff, defendant, status, mode.
        """
        for case in self.CASES:
            if case["number"] == case_number:
                return {**case, "mode": "demo", "message": "[ДЕМО] В production — через КАД API"}
        return {"error": "Дело не найдено", "mode": "demo"}

    def search_cases(self, query: str) -> list[dict]:
        """Поиск дел.

        Args:
            query: Строка поиска (номер дела или наименование истца).

        Returns:
            list[dict]: Список найденных дел.
        """
        return [
            {**c, "mode": "demo"}
            for c in self.CASES
            if query.lower() in c["number"].lower() or query.lower() in c["plaintiff"].lower()
        ]

    def submit_document(self, case_number: str, document_text: str) -> dict:
        """Подача документа в суд (заглушка).

        Args:
            case_number: Номер дела.
            document_text: Текст подаваемого документа.

        Returns:
            dict: Статус подачи с mode=demo.
        """
        return {
            "status": "submitted",
            "case_number": case_number,
            "document_preview": document_text[:100],
            "mode": "demo",
            "message": "[ДЕМО] В production — через Мой Арбитр (УКЭП)",
        }
