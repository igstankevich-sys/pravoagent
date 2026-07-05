"""
LangGraph Orchestrator — управление агентами, маршрутизация запросов, HITL.

Базовый граф для маршрутизации запросов к агентам с поддержкой:
- Keyword-based routing (RouterNode)
- Human-in-the-loop (AuditLog + approve/reject)
- Вызов LLM через LLMContract
- LangGraph StateGraph для построения графа состояний
- Выбор модели через ModelRouter
"""
from __future__ import annotations

import datetime
import logging
from typing import Any, Callable, Optional, TypedDict

from langgraph.graph import END, StateGraph

from backend.agents.llm_contract import LLMContract, LLMConfig
from backend.agents.model_router import ModelRouter
from backend.agents.litigation.claim_agent import ClaimAgent
from backend.agents.litigation.lawsuit_agent import LawsuitAgent
from backend.agents.litigation.court_calendar import CourtCalendar
from backend.agents.contracts.contract_draft import ContractDraftAgent
from backend.agents.contracts.contract_review import ContractReviewAgent
from backend.agents.general_dept.legal_opinion_agent import LegalOpinionAgent

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Состояние графа
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    """Состояние, передаваемое между узлами графа."""

    request: str
    agent_type: str
    case_id: Optional[int]
    user_id: Optional[int]
    tenant_id: Optional[int]
    response: str
    requires_human_approval: bool
    approved: Optional[bool]
    model_used: str
    tokens_used: int
    model_tier: str
    error: Optional[str]


# ---------------------------------------------------------------------------
# Узлы графа
# ---------------------------------------------------------------------------


class AgentNode:
    """Базовый класс узла графа.

    Все узлы наследуются от него и реализуют async process().
    """

    async def process(self, state: AgentState) -> AgentState:
        raise NotImplementedError("Подклассы должны реализовать process()")


class RouterNode(AgentNode):
    """Узел маршрутизации запроса к агенту по ключевым словам.

    Определяет:
    - agent_type: litigation / contracts / general_dept
    - requires_human_approval: нужна ли верификация человеком
    """

    def __init__(self) -> None:
        self.routes: dict[str, str] = {
            # Русские ключевые слова -> litigation
            "иск": "litigation",
            "претензи": "litigation",
            "жалоб": "litigation",
            "суд": "litigation",
            "кассаци": "litigation",
            "апелляци": "litigation",
            "взыскан": "litigation",
            "задолженност": "litigation",
            "неустойк": "litigation",
            # Английские ключевые слова -> litigation
            "claim": "litigation",
            "lawsuit": "litigation",
            "court": "litigation",
            "appeal": "litigation",
            # Русские ключевые слова -> contracts
            "договор": "contracts",
            "контракт": "contracts",
            "оферт": "contracts",
            "поставк": "contracts",
            "подряд": "contracts",
            "аренд": "contracts",
            # Английские ключевые слова -> contracts
            "contract": "contracts",
            "agreement": "contracts",
            # Русские ключевые слова -> general_dept
            "доверенност": "general_dept",
            "нотари": "general_dept",
            "заключен": "general_dept",
            "корпоратив": "general_dept",
            "регистраци": "general_dept",
            # Английские ключевые слова -> general_dept
            "opinion": "general_dept",
            "power_of_attorney": "general_dept",
            "notarial": "general_dept",
        }

        # Ключевые слова, требующие утверждения человеком
        self.hitl_keywords: list[str] = [
            "иск", "претензия", "жалоба", "суд", "договор",
            "contract", "claim", "lawsuit", "complaint",
        ]

    async def process(self, state: AgentState) -> AgentState:
        """Маршрутизация запроса.

        Если agent_type уже задан (например, передан явно в API) — пропускаем.
        """
        if state["agent_type"]:
            logger.debug("RouterNode: agent_type уже задан = %s", state["agent_type"])
            return state

        request_lower = state["request"].lower()

        for keyword, agent_type in self.routes.items():
            if keyword in request_lower:
                state["agent_type"] = agent_type
                logger.debug("RouterNode: маршрутизация -> %s (keyword=%s)", agent_type, keyword)
                break

        if not state["agent_type"]:
            state["agent_type"] = "general_dept"
            logger.debug("RouterNode: маршрутизация по-умолчанию -> general_dept")

        state["requires_human_approval"] = any(
            kw in request_lower for kw in self.hitl_keywords
        )
        return state


class HumanInTheLoop:
    """Human-in-the-loop: запрос утверждения у пользователя.

    Вместо блокирования выполнения запись идёт в AuditLog.
    flag requires_human_approval = True означает, что ответ должен быть
    проверен человеком перед отправкой контрагенту.
    """

    async def request_approval(self, state: AgentState, db_session: Any) -> AgentState:
        """Запрос утверждения — вставка записи в AuditLog.

        Args:
            state: Текущее состояние графа.
            db_session: Сессия SQLAlchemy.

        Returns:
            Состояние без изменений (неблокирующий HITL).
        """
        if not state["requires_human_approval"]:
            return state

        try:
            from backend.models.base import AuditLog

            log = AuditLog(
                user_id=state.get("user_id"),
                tenant_id=state.get("tenant_id"),
                action="agent_approval_request",
                entity_type="agent",
                entity_id=str(state.get("case_id")) if state.get("case_id") else None,
                details=(
                    f"Agent: {state['agent_type']}, "
                    f"Request: {state['request'][:200]}..."
                ),
                timestamp=datetime.datetime.utcnow(),
            )
            db_session.add(log)
            db_session.commit()
            logger.info(
                "HITL: запрос утверждения для agent_type=%s (user=%s)",
                state["agent_type"],
                state.get("user_id"),
            )
        except Exception as exc:
            logger.warning("HITL: ошибка записи AuditLog: %s", exc)

        return state

    async def confirm_approval(self, state: AgentState, approved: bool) -> AgentState:
        """Подтверждение или отклонение.

        Args:
            state: Текущее состояние.
            approved: True — одобрено, False — отклонено.

        Returns:
            Обновлённое состояние.
        """
        state["approved"] = approved
        logger.info("HITL: решение = %s для agent_type=%s", approved, state["agent_type"])
        return state


# ---------------------------------------------------------------------------
# LangGraph Nodes (как callable для StateGraph)
# ---------------------------------------------------------------------------


async def route_node(state: AgentState, config: dict[str, Any] | None = None) -> AgentState:
    """Узел маршрутизации запроса к агенту по ключевым словам."""
    if state.get("agent_type"):
        return state

    router = RouterNode()
    return await router.process(state)


async def model_select_node(state: AgentState, config: dict[str, Any] | None = None) -> AgentState:
    """Узел выбора модели."""
    model_router = ModelRouter()
    tier = model_router.select_tier(state["request"])
    state["model_tier"] = tier
    state["model_used"] = model_router.select_model(tier)
    return state


async def hitl_node(state: AgentState, config: dict[str, Any] | None = None) -> AgentState:
    """Узел Human-in-the-loop (неблокирующая запись в AuditLog)."""
    if not state.get("requires_human_approval"):
        return state

    hitl = HumanInTheLoop()
    db_session = config.get("db_session") if config else None
    return await hitl.request_approval(state, db_session)


async def llm_generate_node(state: AgentState, config: dict[str, Any] | None = None) -> AgentState:
    """Узел генерации ответа LLM."""
    system_prompts = {
        "litigation": "Ты — судебный юрист ПравоАгент...",
        "contracts": "Ты — договорник ПравоАгент...",
        "general_dept": "Ты — юрист общего отдела ПравоАгент...",
    }

    agent_type = state["agent_type"]
    is_mock = state.get("model_used", "mock") == "mock"

    if is_mock:
        try:
            case_data: dict[str, Any] = {
                "title": state["request"],
                "case_id": state.get("case_id"),
                "user_id": state.get("user_id"),
                "tenant_id": state.get("tenant_id"),
            }
            if agent_type == "litigation":
                claim_agent = ClaimAgent()
                response = await claim_agent.draft_claim(case_data)
            elif agent_type == "contracts":
                contract_agent = ContractDraftAgent()
                response = await contract_agent.draft_contract("supply", {"description": state["request"]})
            elif agent_type == "general_dept":
                opinion_agent = LegalOpinionAgent()
                response = await opinion_agent.generate_opinion(state["request"])
            else:
                llm = LLMContract(LLMConfig(model="mock"))
                response = await llm.generate(
                    state["request"],
                    system_prompts.get(agent_type, "Ты — юридический ассистент ПравоАгент."),
                )
            state["response"] = response
            state["tokens_used"] = len(state["request"]) + len(response)
        except Exception as exc:
            logging.getLogger(__name__).exception("LLM generate error")
            state["error"] = str(exc)
            state["response"] = f"[ОШИБКА] При обработке запроса произошла ошибка: {exc}."
        return state

    llm = LLMContract(LLMConfig(model=state.get("model_used", "mock")))
    system_prompt = system_prompts.get(agent_type, "Ты — юридический ассистент ПравоАгент.")

    context = ""
    if state.get("case_id"):
        context = f"\nКонтекст: ID дела = {state['case_id']}"
    if state.get("tenant_id"):
        context += f"\nТенант ID = {state['tenant_id']}"

    full_prompt = f"{state['request']}{context}" if context else state["request"]

    try:
        state["response"] = await llm.generate(full_prompt, system_prompt)
        state["tokens_used"] = len(full_prompt) + len(state["response"])
    except Exception as exc:
        logging.getLogger(__name__).exception("LLM generate error")
        state["error"] = str(exc)
        state["response"] = f"[ОШИБКА] При обработке запроса произошла ошибка: {exc}."

    return state


def should_route_to_hitl(state: AgentState) -> str:
    """Conditional edge: если требуется HITL — идём в hitl_node, иначе в llm_generate."""
    if state.get("requires_human_approval"):
        return "hitl"
    return "llm_generate"


# ---------------------------------------------------------------------------
# LangGraph Builder
# ---------------------------------------------------------------------------


def build_orchestrator_graph() -> StateGraph:
    """Построение графа оркестратора с помощью LangGraph StateGraph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("route", route_node)
    workflow.add_node("select_model", model_select_node)
    workflow.add_node("hitl", hitl_node)
    workflow.add_node("llm_generate", llm_generate_node)

    workflow.set_entry_point("route")

    workflow.add_edge("route", "select_model")
    workflow.add_conditional_edges(
        "select_model",
        should_route_to_hitl,
        {"hitl": "hitl", "llm_generate": "llm_generate"},
    )
    workflow.add_edge("hitl", "llm_generate")
    workflow.add_edge("llm_generate", END)

    return workflow.compile()


# ---------------------------------------------------------------------------
# Оркестратор (обёртка над LangGraph графом)
# ---------------------------------------------------------------------------


class Orchestrator:
    """Главный оркестратор. Использует LangGraph StateGraph для управления агентами."""

    def __init__(self) -> None:
        self.graph = build_orchestrator_graph()

    async def process_request(
        self,
        request: str,
        user_id: int,
        tenant_id: int,
        case_id: Optional[int] = None,
        agent_type: Optional[str] = None,
        db_session: Any = None,
        estimated_complexity: Optional[str] = None,
    ) -> dict[str, Any]:
        """Полный цикл обработки запроса через LangGraph."""
        initial_state: AgentState = {
            "request": request,
            "agent_type": agent_type or "",
            "case_id": case_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "response": "",
            "requires_human_approval": False,
            "approved": None,
            "model_used": "mock",
            "tokens_used": 0,
            "model_tier": "flash",
            "error": None,
        }

        try:
            result_state = await self.graph.ainvoke(
                initial_state,
                config={"configurable": {"db_session": db_session}},
            )

            estimated_cost = ModelRouter().get_cost_estimate(
                result_state.get("model_tier", "flash"),
                result_state.get("tokens_used", 0),
            )

            logging.getLogger(__name__).info(
                "Orchestrator: agent=%s tier=%s model=%s tokens=%d cost=%.6f",
                result_state.get("agent_type"),
                result_state.get("model_tier"),
                result_state.get("model_used"),
                result_state.get("tokens_used", 0),
                estimated_cost,
            )

        except Exception as exc:
            logging.getLogger(__name__).exception("Orchestrator error")
            result_state = {
                **initial_state,
                "error": str(exc),
                "response": f"[ОШИБКА] {exc}",
            }

        return {
            "agent_type": result_state.get("agent_type", ""),
            "response": result_state.get("response", ""),
            "requires_human_approval": result_state.get("requires_human_approval", False),
            "approved": result_state.get("approved"),
            "model_used": result_state.get("model_used", "mock"),
            "model_tier": result_state.get("model_tier", "flash"),
            "tokens_used": result_state.get("tokens_used", 0),
            "error": result_state.get("error"),
        }


    def _get_system_prompt(self, agent_type: str) -> str:
        prompts = {
            "litigation": "Ты — судебный юрист ПравоАгент...",
            "contracts": "Ты — договорник ПравоАгент...",
            "general_dept": "Ты — юрист общего отдела ПравоАгент...",
        }
        return prompts.get(agent_type, "Ты — юридический ассистент ПравоАгент.")
