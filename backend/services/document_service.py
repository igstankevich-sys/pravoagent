"""
Document Engine - движок для работы с документами.
Шаблоны, генерация, граф связей.
"""
from sqlalchemy.orm import Session
from backend.models.base import Document


class DocumentTemplate:
    """Шаблон документа (Jinja2-подобный)."""

    def __init__(self, name: str, template_text: str):
        self.name = name
        self.template_text = template_text

    def render(self, context: dict) -> str:
        """Заполнение шаблона данными."""
        result = self.template_text
        for key, value in context.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result


# Встроенные шаблоны
TEMPLATES = {
    "claim": DocumentTemplate(
        "Претензия",
        "ПРЕТЕНЗИЯ\n\n"
        "От: {{{sender}}}\n"
        "Кому: {{{recipient}}}\n"
        "Дата: {{{date}}}\n\n"
        "Уважаемый {{{recipient_name}}}!\n\n"
        "Настоящей претензией уведомляю Вас о необходимости...\n\n"
        "Сумма требования: {{{amount}}} руб.\n\n"
        "Срок ответа: 30 дней.\n\n"
        "С уважением,\n{{{sender_name}}}",
    ),
    "lawsuit": DocumentTemplate(
        "Исковое заявление",
        "В {{{court_name}}}\n\n"
        "Истец: {{{plaintiff}}}\n"
        "Ответчик: {{{defendant}}}\n\n"
        "ИСКОВОЕ ЗАЯВЛЕНИЕ\n"
        "о взыскании {{{amount}}} руб.\n\n"
        "Цена иска: {{{amount}}} руб.\n\n"
        "1. Обстоятельства дела\n...",
    ),
    "contract": DocumentTemplate(
        "Договор",
        "ДОГОВОР №{{{contract_number}}}\n"
        "г. {{{city}}}  \"___\" _________ 2026 г.\n\n"
        "{{{party1}}}, именуемое \"Сторона 1\", и {{{party2}}}, "
        "именуемое \"Сторона 2\", заключили настоящий договор...\n",
    ),
    "legal_opinion": DocumentTemplate(
        "Юридическое заключение",
        "ЮРИДИЧЕСКОЕ ЗАКЛЮЧЕНИЕ\n\n"
        "Вопрос: {{{question}}}\n\n"
        "Заключение: ...\n\n"
        "Нормы права: ...\n",
    ),
    "opinion_standard": DocumentTemplate(
        "Стандартное юридическое заключение",
        "ЮРИДИЧЕСКОЕ ЗАКЛЮЧЕНИЕ\n\n"
        "1. Заголовок\n"
        "{{{title}}}\n\n"
        "2. Вопрос\n"
        "{{{question}}}\n\n"
        "3. Исходные данные\n"
        "{{{initial_data}}}\n\n"
        "4. Анализ\n"
        "{{{analysis}}}\n\n"
        "5. Вывод\n"
        "{{{conclusion}}}\n\n"
        "6. Риски\n"
        "{{{risks}}}\n\n"
        "Дата: {{{date}}}\n"
        "Юрист: {{{lawyer}}}",
    ),
    "opinion_purchases": DocumentTemplate(
        "Юридическое заключение по закупкам",
        "ЮРИДИЧЕСКОЕ ЗАКЛЮЧЕНИЕ ПО ЗАКУПКАМ\n\n"
        "1. Заголовок\n"
        "{{{title}}}\n\n"
        "2. Вопрос\n"
        "{{{question}}}\n\n"
        "3. Исходные данные\n"
        "Закупочная документация: {{{docs_info}}}\n"
        "Нормативная база: Федеральный закон от 05.04.2013 № 44-ФЗ, "
        "Федеральный закон от 18.07.2011 № 223-ФЗ\n\n"
        "4. Анализ\n"
        "{{{analysis}}}\n\n"
        "5. Вывод\n"
        "{{{conclusion}}}\n\n"
        "6. Риски\n"
        "{{{risks}}}\n\n"
        "Дата: {{{date}}}\n"
        "Юрист: {{{lawyer}}}",
    ),
    "opinion_taxes": DocumentTemplate(
        "Юридическое заключение по налогам",
        "ЮРИДИЧЕСКОЕ ЗАКЛЮЧЕНИЕ ПО НАЛОГАМ\n\n"
        "1. Заголовок\n"
        "{{{title}}}\n\n"
        "2. Вопрос\n"
        "{{{question}}}\n\n"
        "3. Исходные данные\n"
        "{{{initial_data}}}\n\n"
        "4. Анализ\n"
        "{{{analysis}}}\n\n"
        "5. Вывод\n"
        "{{{conclusion}}}\n\n"
        "6. Налоговые риски\n"
        "{{{risks}}}\n\n"
        "Дата: {{{date}}}\n"
        "Юрист: {{{lawyer}}}",
    ),
    "opinion_labor": DocumentTemplate(
        "Юридическое заключение по трудовому праву",
        "ЮРИДИЧЕСКОЕ ЗАКЛЮЧЕНИЕ ПО ТРУДОВОМУ ПРАВУ\n\n"
        "1. Заголовок\n"
        "{{{title}}}\n\n"
        "2. Вопрос\n"
        "{{{question}}}\n\n"
        "3. Исходные данные\n"
        "{{{initial_data}}}\n\n"
        "4. Анализ\n"
        "{{{analysis}}}\n\n"
        "5. Вывод\n"
        "{{{conclusion}}}\n\n"
        "6. Риски для работодателя/работника\n"
        "{{{risks}}}\n\n"
        "Дата: {{{date}}}\n"
        "Юрист: {{{lawyer}}}",
    ),
    "opinion_corporate": DocumentTemplate(
        "Юридическое заключение по корпоративному праву",
        "ЮРИДИЧЕСКОЕ ЗАКЛЮЧЕНИЕ ПО КОРПОРАТИВНОМУ ПРАВУ\n\n"
        "1. Заголовок\n"
        "{{{title}}}\n\n"
        "2. Вопрос\n"
        "{{{question}}}\n\n"
        "3. Исходные данные\n"
        "{{{initial_data}}}\n\n"
        "4. Анализ\n"
        "{{{analysis}}}\n\n"
        "5. Вывод\n"
        "{{{conclusion}}}\n\n"
        "6. Корпоративные риски\n"
        "{{{risks}}}\n\n"
        "Дата: {{{date}}}\n"
        "Юрист: {{{lawyer}}}",
    ),
}


class DocumentService:
    """Сервис для работы с документами."""

    def create_from_template(
        self,
        db: Session,
        template_name: str,
        context: dict,
        case_id: int,
        author_id: int,
        tenant_id: int,
    ) -> Document:
        """Создание документа из шаблона."""
        template = TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Шаблон '{template_name}' не найден")

        content = template.render(context)
        doc = Document(
            title=template.name,
            content=content,
            doc_type=template_name,
            status="draft",
            case_id=case_id,
            author_id=author_id,
            tenant_id=tenant_id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def get_document_graph(self, db: Session, case_id: int) -> dict:
        """Граф связей документов дела."""
        documents = (
            db.query(Document).filter(Document.case_id == case_id).all()
        )
        return {
            "case_id": case_id,
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "type": d.doc_type,
                    "status": d.status,
                }
                for d in documents
            ],
            "links": self._build_links(documents),
        }

    def _build_links(self, documents: list) -> list:
        return [
            {"source": 0, "target": i, "type": "related"}
            for i in range(1, len(documents))
        ]
