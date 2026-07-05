"""
Сервис конфигурации ролевых workspace для ПравоАгент.
Определяет, какие панели, layout и AI-агенты доступны для каждой роли.
"""

WORKSPACE_CONFIG = {
    "litigation": {
        "title": "Судебный юрист",
        "icon": "\uD83D\uDCB0",
        "panels": {
            "sidebar": {
                "title": "Дела",
                "tabs": ["Дела", "Избранное", "КАД"],
                "default_width": 280,
            },
            "main": {
                "title": "Редактор",
                "tabs": ["Дело", "Документы", "Чат", "КАД"],
            },
            "right": {
                "title": "AI-агент",
                "default_width": 320,
            },
        },
        "activity_bar": [
            {"id": "cases", "icon": "\uD83D\uDCCB", "title": "Дела"},
            {"id": "documents", "icon": "\uD83D\uDCC4", "title": "Документы"},
            {"id": "chat", "icon": "\uD83D\uDCAC", "title": "Чат"},
            {"id": "kad", "icon": "\uD83D\uDD0D", "title": "КАД"},
        ],
        "agents": ["litigation"],
        "actions": [
            {"id": "new-claim", "label": "Создать иск", "icon": "\uD83D\uDCDD"},
            {"id": "new-complaint", "label": "Претензия", "icon": "\uD83D\uDCE9"},
            {"id": "new-appeal", "label": "Жалоба", "icon": "\uD83D\uDCE2"},
            {"id": "case-review", "label": "Ознакомление с делом", "icon": "\uD83D\uDCC3"},
        ],
    },
    "contracts": {
        "title": "Договорник",
        "icon": "\uD83D\uDCDD",
        "panels": {
            "sidebar": {
                "title": "Договоры",
                "tabs": ["Договоры", "Шаблоны", "Контрагенты"],
                "default_width": 280,
            },
            "main": {
                "title": "Редактор договора",
                "tabs": ["Договор", "Риски", "Версии"],
            },
            "right": {
                "title": "AI-агент + Approval",
                "default_width": 320,
            },
        },
        "activity_bar": [
            {"id": "contracts", "icon": "\uD83D\uDCDD", "title": "Договоры"},
            {"id": "templates", "icon": "\uD83D\uDCCB", "title": "Шаблоны"},
            {"id": "approval", "icon": "\u2705", "title": "Согласование"},
            {"id": "counterparties", "icon": "\uD83C\uDFE2", "title": "Контрагенты"},
        ],
        "agents": ["contracts"],
        "actions": [
            {"id": "new-contract", "label": "Создать договор", "icon": "\uD83D\uDCDD"},
            {"id": "approve", "label": "Согласовать", "icon": "\u2705"},
            {"id": "send-counterparty", "label": "Отправить контрагенту", "icon": "\uD83D\uDCE8"},
        ],
    },
    "general": {
        "title": "Общий отдел",
        "icon": "\uD83C\uDFE2",
        "panels": {
            "sidebar": {
                "title": "Документы",
                "tabs": ["Доверенности", "Нотариат", "НПА", "Реестры"],
                "default_width": 280,
            },
            "main": {
                "title": "Просмотр",
                "tabs": ["Документ", "История"],
            },
            "right": {
                "title": "AI-агент",
                "default_width": 320,
            },
        },
        "activity_bar": [
            {"id": "proxies", "icon": "\uD83D\uDCC3", "title": "Доверенности"},
            {"id": "notary", "icon": "\uD83D\uDCD0", "title": "Нотариат"},
            {"id": "npa", "icon": "\uD83D\uDCD6", "title": "НПА"},
            {"id": "registries", "icon": "\uD83D\uDCCA", "title": "Реестры"},
        ],
        "agents": ["general"],
        "actions": [
            {"id": "new-proxy", "label": "Создать доверенность", "icon": "\uD83D\uDCC3"},
            {"id": "new-notary", "label": "Заказ нотариуса", "icon": "\uD83D\uDCD0"},
            {"id": "new-npa", "label": "Проект НПА", "icon": "\uD83D\uDCD6"},
        ],
    },
    "head_legal": {
        "title": "Head of Legal",
        "icon": "\uD83D\uDCCA",
        "panels": {
            "sidebar": {
                "title": "Команда",
                "tabs": ["Команда", "Отделы", "Загрузка"],
                "default_width": 280,
            },
            "main": {
                "title": "Дашборд",
                "tabs": ["Дашборд", "Аналитика", "Отчёты"],
            },
            "right": {
                "title": "KPI",
                "default_width": 320,
            },
        },
        "activity_bar": [
            {"id": "dashboard", "icon": "\uD83D\uDCCA", "title": "Дашборд"},
            {"id": "team", "icon": "\uD83D\uDC65", "title": "Команда"},
            {"id": "analytics", "icon": "\uD83D\uDCC8", "title": "Аналитика"},
            {"id": "kpi-settings", "icon": "\u2699\uFE0F", "title": "Настройки KPI"},
        ],
        "agents": ["head_legal"],
        "actions": [
            {"id": "new-report", "label": "Создать отчёт", "icon": "\uD83D\uDCCA"},
            {"id": "team-plan", "label": "План загрузки", "icon": "\uD83D\uDCCB"},
        ],
    },
    "admin": {
        "title": "Администратор",
        "icon": "\uD83D\uDD27",
        "panels": {
            "sidebar": {
                "title": "Администрирование",
                "tabs": ["Пользователи", "Тенанты", "LLM", "Система"],
                "default_width": 280,
            },
            "main": {
                "title": "Панель управления",
                "tabs": ["Главная", "Логи", "Health"],
            },
            "right": {
                "title": "Детали",
                "default_width": 320,
            },
        },
        "activity_bar": [
            {"id": "users", "icon": "\uD83D\uDC64", "title": "Пользователи"},
            {"id": "tenants", "icon": "\uD83C\uDFE2", "title": "Тенанты"},
            {"id": "llm", "icon": "\uD83E\uDD16", "title": "LLM"},
            {"id": "health", "icon": "\uD83D\uDC9A", "title": "Health"},
            {"id": "logs", "icon": "\uD83D\uDCCB", "title": "Логи"},
            {"id": "system", "icon": "\u2699\uFE0F", "title": "Система"},
        ],
        "agents": [],
        "actions": [
            {"id": "new-user", "label": "Создать пользователя", "icon": "\uD83D\uDC64"},
            {"id": "new-tenant", "label": "Создать тенанта", "icon": "\uD83C\uDFE2"},
            {"id": "system-update", "label": "Обновление системы", "icon": "\uD83D\uDD04"},
        ],
    },
    "legal_opinions": {
        "title": "Юридические заключения",
        "icon": "\uD83D\uDCDD",
        "panels": {
            "sidebar": {
                "title": "Заявки",
                "tabs": ["Заявки", "В работе", "Архив"],
                "default_width": 280,
            },
            "main": {
                "title": "Заключение",
                "tabs": ["Заключение", "Материалы", "История"],
            },
            "right": {
                "title": "AI-агент",
                "default_width": 320,
            },
        },
        "activity_bar": [
            {"id": "requests", "icon": "\uD83D\uDCE9", "title": "Заявки"},
            {"id": "opinions", "icon": "\uD83D\uDCDD", "title": "Заключения"},
            {"id": "templates", "icon": "\uD83D\uDCCB", "title": "Шаблоны"},
            {"id": "stats", "icon": "\uD83D\uDCCA", "title": "Статистика"},
        ],
        "agents": ["legal_opinion"],
        "actions": [
            {"id": "new-opinion", "label": "Новое заключение", "icon": "\uD83D\uDCDD"},
        ],
    },
}

# Маппинг ролей в workspace_id
ROLE_TO_WORKSPACE = {
    "litigation": "litigation",
    "contracts": "contracts",
    "general": "general",
    "head_legal": "head_legal",
    "admin": "admin",
    "legal_opinions": "legal_opinions",
}


def get_workspace_config(role: str) -> dict:
    """Получить конфигурацию workspace для роли."""
    workspace_id = ROLE_TO_WORKSPACE.get(role)
    if workspace_id:
        return WORKSPACE_CONFIG.get(workspace_id, {})
    return WORKSPACE_CONFIG.get("general", {})


def get_default_workspace(role: str) -> str:
    """Получить ID workspace по умолчанию для роли."""
    return ROLE_TO_WORKSPACE.get(role, "general")
