"""
Генератор тестовых данных для ПравоАгент.
Создаёт: 3 организации, 6 пользователей, 8 дел, 24+ документа,
10 юрзаключений, 15 заявок, KPI за 3 месяца, 500+ audit логов.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import init_db, SessionLocal
from backend.models.base import (
    Tenant, User, Case, Document, AuditLog,
    LegalRequest, KpiEntry, LegalOpinion, KpiMetricConfig,
)
from datetime import datetime, timedelta
import random


def generate_all():
    init_db()
    db = SessionLocal()
    now = datetime.utcnow()

    # ============ Базовые данные (если нет) ============
    tenants = db.query(Tenant).all()
    if not tenants:
        print("Генерация базовых данных...")
        t1 = Tenant(name="ООО «Ромашка»", monthly_token_limit=5_000_000, tokens_used_this_month=123456)
        t2 = Tenant(name="АО «ТехноИнвест»", monthly_token_limit=10_000_000, tokens_used_this_month=789012)
        t3 = Tenant(name="ООО «Юридический Центр»", monthly_token_limit=3_000_000, tokens_used_this_month=34567)
        db.add_all([t1, t2, t3])
        db.commit()
        tenants = [t1, t2, t3]
    else:
        print(f"Тенанты уже есть ({len(tenants)} шт).")

    # --- Users (только если нет) ---
    users = db.query(User).all()
    if not users:
        users_data = [
            {"email": "ivanov@romashka.ru", "username": "Иванов И.И.", "role": "litigation", "tenant_id": tenants[0].id},
            {"email": "petrov@romashka.ru", "username": "Петров П.П.", "role": "contracts", "tenant_id": tenants[0].id},
            {"email": "sidorova@tehno.ru", "username": "Сидорова А.С.", "role": "general", "tenant_id": tenants[1].id},
            {"email": "smirnov@tehno.ru", "username": "Смирнов Д.В.", "role": "head_legal", "tenant_id": tenants[1].id},
            {"email": "kuznetsov@lawcenter.ru", "username": "Кузнецов М.А.", "role": "litigation", "tenant_id": tenants[2].id},
            {"email": "admin@pravoagent.ru", "username": "Администратор", "role": "admin", "tenant_id": None},
        ]
        for u in users_data:
            user = User(
                email=u["email"], username=u["username"],
                hashed_password="demo_hash", role=u["role"],
                tenant_id=u["tenant_id"], is_active=True,
            )
            db.add(user)
            users.append(user)
        db.commit()
    else:
        print(f"Пользователи уже есть ({len(users)} шт).")

    # --- Cases (только если нет) ---
    cases = db.query(Case).all()
    if not cases:
        cases_data = [
            {"title": "Спор с ООО «Поставщик» о неисполнении договора", "status": "in_progress", "case_type": "litigation",
             "court": "АС г. Москвы", "plaintiff": "ООО «Ромашка»", "defendant": "ООО «Поставщик»",
             "case_number": "А40-12345/2026", "priority": "high", "user_id": users[0].id, "tenant_id": tenants[0].id},
            {"title": "Взыскание дебиторской задолженности", "status": "open", "case_type": "litigation",
             "court": "АС г. Москвы", "plaintiff": "ООО «Ромашка»", "defendant": "ООО «Должник»",
             "case_number": "А40-23456/2026", "priority": "urgent", "user_id": users[0].id, "tenant_id": tenants[0].id},
            {"title": "Претензия по договору поставки №45/23", "status": "open", "case_type": "contracts",
             "plaintiff": "ООО «Ромашка»", "defendant": "ООО «Поставщик»", "priority": "normal",
             "user_id": users[1].id, "tenant_id": tenants[0].id},
            {"title": "Регистрация прав на товарный знак", "status": "in_progress", "case_type": "general",
             "plaintiff": "АО «ТехноИнвест»", "priority": "normal",
             "case_number": "РТ-2026-001", "user_id": users[2].id, "tenant_id": tenants[1].id},
            {"title": "Согласование лицензионного договора", "status": "open", "case_type": "contracts",
             "plaintiff": "АО «ТехноИнвест»", "defendant": "ООО «Партнёр»", "priority": "high",
             "user_id": users[3].id, "tenant_id": tenants[1].id},
            {"title": "Оспаривание кадастровой стоимости", "status": "closed", "case_type": "litigation",
             "court": "АС г. Санкт-Петербурга", "plaintiff": "ООО «Юридический Центр»", "defendant": "Росреестр",
             "case_number": "А56-34567/2026", "priority": "normal", "user_id": users[4].id, "tenant_id": tenants[2].id},
            {"title": "Проверка контрагента ООО «Новый партнёр»", "status": "in_progress", "case_type": "contracts",
             "plaintiff": "ООО «Юридический Центр»", "priority": "high",
             "user_id": users[4].id, "tenant_id": tenants[2].id},
            {"title": "Подготовка юридического заключения по 223-ФЗ", "status": "open", "case_type": "general",
             "plaintiff": "АО «ТехноИнвест»", "priority": "normal",
             "user_id": users[2].id, "tenant_id": tenants[1].id},
        ]
        for c in cases_data:
            case = Case(
                **c,
                description=f"Описание дела «{c['title']}». Создано для демонстрации прототипа ПравоАгент.",
                created_at=now - timedelta(days=random.randint(1, 60)),
                updated_at=now - timedelta(hours=random.randint(1, 48)),
            )
            db.add(case)
            cases.append(case)
        db.commit()
    else:
        print(f"Дела уже есть ({len(cases)} шт).")

    # --- Documents (только если нет) ---
    existing_docs = db.query(Document).count()
    if existing_docs == 0:
        doc_titles = [
            "Исковое заявление", "Претензия", "Отзыв на иск",
            "Ходатайство", "Договор поставки", "Дополнительное соглашение",
            "Юридическое заключение", "Справка", "Акт сверки",
            "Уведомление", "Запрос", "Решение",
        ]
        doc_types = ["claim", "contract", "opinion", "other"]
        for case in cases:
            num_docs = random.randint(1, 4)
            for j in range(num_docs):
                title = random.choice(doc_titles)
                doc_type = random.choice(doc_types)
                content = f"Документ «{title}» по делу «{case.title}».\n\n"
                content += "Создан для демонстрации прототипа ПравоАгент.\n"
                content += "Статус: черновик. Требует утверждения юристом.\n"

                doc = Document(
                    title=title, content=content, doc_type=doc_type,
                    status=random.choice(["draft", "draft", "review", "approved"]),
                    case_id=case.id, author_id=case.user_id, tenant_id=case.tenant_id,
                    created_at=case.created_at + timedelta(hours=random.randint(1, 72)),
                    updated_at=now - timedelta(hours=random.randint(1, 24)),
                )
                db.add(doc)
        db.commit()

    # ============ 1. Юрзаключения (LegalOpinion) — 10 шт ============
    existing_opinions = db.query(LegalOpinion).count()
    if existing_opinions == 0:
        print("Генерация юридических заключений...")
        opinions_data = [
            {
                "title": "Правовой анализ возможности взыскания убытков с контрагента",
                "question": "Может ли ООО «Ромашка» взыскать убытки с ООО «Поставщик» за срыв срока поставки?",
                "short_answer": "Да, взыскание убытков возможно на основании ст. 15, 393 ГК РФ при доказанности факта нарушения и размера убытков.",
                "opinion_type": "litigation",
                "tenant_idx": 0,
            },
            {
                "title": "Заключение по налоговым рискам договора лицензирования",
                "question": "Какие налоговые риски возникают при заключении лицензионного договора с иностранной компанией?",
                "short_answer": "Риск доначисления налога у источника (роялти) и НДС при отсутствии фактического права на льготу по СИДН.",
                "opinion_type": "tax",
                "tenant_idx": 1,
            },
            {
                "title": "Анализ условий договора поставки на предмет кабальности",
                "question": "Являются ли условия договора поставки №45/23 кабальными для ООО «Ромашка»?",
                "short_answer": "Отдельные условия (п. 7.3, 9.2) могут быть признаны кабальными в силу ст. 179 ГК РФ.",
                "opinion_type": "contract",
                "tenant_idx": 0,
            },
            {
                "title": "Заключение о порядке оспаривания кадастровой стоимости",
                "question": "Каков порядок оспаривания кадастровой стоимости земельного участка в 2026 году?",
                "short_answer": "Внесудебный порядок через ГБУ (6 мес.) или судебный через КАС РФ (3 мес. с момента отказа).",
                "opinion_type": "litigation",
                "tenant_idx": 2,
            },
            {
                "title": "Правовая позиция по корпоративному спору между участниками",
                "question": "Каковы перспективы исключения участника из ООО за систематическое нарушение?",
                "short_answer": "Исключение возможно при грубом нарушении обязанностей, делающем невозможной деятельность общества.",
                "opinion_type": "corporate",
                "tenant_idx": 1,
            },
            {
                "title": "Анализ регуляторных требований к рекламе финансовых услуг",
                "question": "Соответствует ли реклама кредитных продуктов требованиям ФЗ «О рекламе» и ФЗ «О потребительском кредите»?",
                "short_answer": "Требуется указание всех условий, влияющих на полную стоимость кредита. Риск предписания ФАС.",
                "opinion_type": "regulatory",
                "tenant_idx": 1,
            },
            {
                "title": "Заключение о возможности снижения неустойки по ст. 333 ГК РФ",
                "question": "Есть ли основания для снижения договорной неустойки с 0.5% до 0.1% за каждый день просрочки?",
                "short_answer": "Да, 0.5% явно несоразмерно последствиям нарушения (обычная практика — 0.1-0.2%).",
                "opinion_type": "litigation",
                "tenant_idx": 0,
            },
            {
                "title": "Правовой анализ договора аренды оборудования",
                "question": "Какие риски содержатся в проекте договора аренды оборудования?",
                "short_answer": "Риск одностороннего повышения арендной платы и отсутствие гарантий возврата обеспечительного платежа.",
                "opinion_type": "contract",
                "tenant_idx": 2,
            },
            {
                "title": "Заключение по вопросу регистрации товарного знака",
                "question": "Каковы шансы регистрации товарного знака «ТехноИнвест» по классам МКТУ 9, 35, 42?",
                "short_answer": "Высокие шансы при отсутствии тождественных/сходных обозначений. Рекомендуется предварительный поиск.",
                "opinion_type": "corporate",
                "tenant_idx": 1,
            },
            {
                "title": "Анализ изменений законодательства о персональных данных",
                "question": "Как новые требования 152-ФЗ (ред. 2025) влияют на обработку данных сотрудников?",
                "short_answer": "Требуется усиление мер защиты: DPA, уведомления, оценка рисков. Сроки хранения сокращены.",
                "opinion_type": "regulatory",
                "tenant_idx": 0,
            },
        ]
        for o in opinions_data:
            t = tenants[o["tenant_idx"]]
            user_list = [u for u in users if u.tenant_id == t.id]
            author = random.choice(user_list) if user_list else users[0]
            local_case = random.choice([c for c in cases if c.tenant_id == t.id] or cases)
            opinion = LegalOpinion(
                title=o["title"],
                question=o["question"],
                short_answer=o["short_answer"],
                full_answer=o["short_answer"] + "\n\nПолный текст заключения содержит подробный анализ нормативной базы, "
                "судебной практики и рекомендации по действиям. Подготовлено на основе "
                "актуального законодательства РФ по состоянию на " + now.strftime("%d.%m.%Y") + ".",
                opinion_type=o["opinion_type"],
                status=random.choice(["approved", "approved", "draft", "review"]),
                tags=o["opinion_type"] + ", zakluchenie",
                author_id=author.id,
                case_id=local_case.id,
                tenant_id=t.id,
                created_at=now - timedelta(days=random.randint(1, 90)),
                updated_at=now - timedelta(hours=random.randint(1, 72)),
            )
            db.add(opinion)
        db.commit()

    # ============ 2. Заявки (LegalRequest) — 15 шт ============
    existing_requests = db.query(LegalRequest).count()
    if existing_requests == 0:
        print("Генерация заявок...")
        request_templates = [
            ("Подготовить исковое заявление", "document", "high", "Срочно подготовить иск о взыскании задолженности по договору поставки."),
            ("Проверить контрагента ООО «Новый партнёр»", "advice", "normal", "Проверить добросовестность и платёжеспособность контрагента."),
            ("Согласовать договор аренды помещения", "approval", "high", "Требуется юридическое согласование проекта договора аренды."),
            ("Зарегистрировать товарный знак", "registration", "normal", "Подать заявку на регистрацию товарного знака в Роспатент."),
            ("Подготовить претензию контрагенту", "document", "urgent", "Претензия о неисполнении обязательств по договору №87/24."),
            ("Проверить изменения в 223-ФЗ", "advice", "low", "Анализ влияния новых поправок на закупочную деятельность."),
            ("Согласовать дополнительное соглашение", "approval", "normal", "Допсоглашение об изменении цены договора поставки."),
            ("Подготовить отзыв на исковое заявление", "document", "urgent", "Отзыв на иск в АС г. Москвы по делу №А40-12345/2026."),
            ("Зарегистрировать ККТ в ФНС", "registration", "normal", "Постановка контрольно-кассовой техники на учёт."),
            ("Проверить договор с самозанятым", "advice", "low", "Проверить соответствие договора требованиям законодательства."),
            ("Согласовать политику обработки ПДн", "approval", "high", "Внутренняя политика обработки персональных данных."),
            ("Подготовить ходатайство об отложении", "document", "normal", "Ходатайство об отложении судебного заседания."),
            ("Проверить контрагента ООО «СтройИнвест»", "advice", "normal", "Проверка на предмет банкротства и судебных споров."),
            ("Согласовать договор подряда", "approval", "high", "Строительный подряд. Риски: сроки, смета, гарантии."),
            ("Зарегистрировать изменения в ЕГРЮЛ", "registration", "normal", "Смена генерального директора — подача формы Р13014."),
        ]
        request_statuses = ["open", "open", "in_progress", "completed", "completed"]
        for title, rtype, priority, desc in request_templates:
            tenant = random.choice(tenants)
            user_list = [u for u in users if u.tenant_id == tenant.id]
            user = random.choice(user_list) if user_list else users[0]
            req = LegalRequest(
                title=title,
                description=desc,
                status=random.choice(request_statuses),
                request_type=rtype,
                priority=priority,
                user_id=user.id,
                tenant_id=tenant.id,
                created_at=now - timedelta(days=random.randint(1, 45)),
                updated_at=now - timedelta(hours=random.randint(1, 48)),
            )
            db.add(req)
        db.commit()

    # ============ 3. KPI история — 3 месяца ============
    existing_kpi = db.query(KpiEntry).count()
    if existing_kpi == 0:
        print("Генерация KPI истории...")
        kpi_metrics = [
            ("cases_open", "Количество открытых дел"),
            ("cases_closed", "Количество закрытых дел"),
            ("docs_generated", "Сгенерировано документов"),
            ("tokens_used", "Потрачено токенов (K)"),
            ("avg_response_time", "Среднее время ответа (ч)"),
        ]
        for tenant in tenants:
            base_values = {
                "cases_open": random.randint(5, 20),
                "cases_closed": random.randint(3, 12),
                "docs_generated": random.randint(10, 50),
                "tokens_used": random.randint(100, 500),
                "avg_response_time": random.randint(2, 8),
            }
            for week_offset in range(12):  # ~3 months
                week_date = now - timedelta(weeks=11 - week_offset)
                for metric_name, _ in kpi_metrics:
                    value = base_values[metric_name] + random.randint(-3, 5)
                    value = max(value, 1)
                    entry = KpiEntry(
                        tenant_id=tenant.id,
                        date=week_date,
                        metric_name=metric_name,
                        metric_value=float(value),
                    )
                    db.add(entry)
        db.commit()

    # ============ 3a. KPI Metric Configs — дефолтные настройки ============
    existing_configs = db.query(KpiMetricConfig).count()
    if existing_configs == 0:
        print("Генерация KPI конфигураций...")
        from backend.services.configuration_service import ConfigurationService
        cfg_service = ConfigurationService()
        for tenant in tenants:
            cfg_service.create_default_config(db, tenant.id)
        print(f"  KPI конфигураций: {db.query(KpiMetricConfig).count()}")

    # ============ 4. Audit логи — 500+ записей ============
    existing_audit = db.query(AuditLog).count()
    if existing_audit == 0:
        print("Генерация audit логов...")
        audit_actions = [
            ("user.login", "user", "Вход в систему"),
            ("user.logout", "user", "Выход из системы"),
            ("case.create", "case", "Создание дела"),
            ("case.update", "case", "Изменение дела"),
            ("case.delete", "case", "Удаление дела"),
            ("document.create", "document", "Создание документа"),
            ("document.update", "document", "Изменение документа"),
            ("document.download", "document", "Скачивание документа"),
            ("document.share", "document", "Отправка на согласование"),
            ("opinion.create", "legal_opinion", "Создание заключения"),
            ("opinion.approve", "legal_opinion", "Утверждение заключения"),
            ("agent.chat", "agent", "Обращение к AI-агенту"),
            ("agent.document_generate", "agent", "Генерация документа агентом"),
            ("kb.search", "knowledge_base", "Поиск по базе знаний"),
            ("kb.document_add", "knowledge_base", "Добавление в базу знаний"),
            ("settings.update", "settings", "Изменение настроек"),
            ("workspace.change", "workspace", "Смена рабочего пространства"),
            ("integration.connect", "integration", "Подключение интеграции"),
        ]
        sample_ips = ["192.168.1.10", "10.0.0.5", "172.16.0.20", "85.234.1.100", "95.25.180.55"]
        for i in range(550):
            action, entity_type, _ = random.choice(audit_actions)
            user = random.choice(users)
            log_entry = AuditLog(
                user_id=user.id,
                user_name=user.username,
                tenant_id=user.tenant_id,
                role=user.role,
                action=action,
                entity_type=entity_type,
                entity_id=str(random.randint(1, 50)),
                details=f"{action.replace('.', ' ').title()} — тестовая запись #{i + 1}",
                ip_address=random.choice(sample_ips),
                session_id=f"sess_{random.randint(10000, 99999)}",
                timestamp=now - timedelta(
                    days=random.randint(0, 60),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                ),
            )
            db.add(log_entry)
        db.commit()

    # ============ Итоговая статистика ============
    print("Генерация seed data завершена:")
    print(f"  Тенантов: {db.query(Tenant).count()}")
    print(f"  Пользователей: {db.query(User).count()}")
    print(f"  Дел: {db.query(Case).count()}")
    print(f"  Документов: {db.query(Document).count()}")
    print(f"  Юрзаключений: {db.query(LegalOpinion).count()}")
    print(f"  Заявок: {db.query(LegalRequest).count()}")
    print(f"  KPI записей: {db.query(KpiEntry).count()}")
    print(f"  Audit логов: {db.query(AuditLog).count()}")
    db.close()


if __name__ == "__main__":
    generate_all()
