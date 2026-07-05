"""
LLM Contract Layer — единый интерфейс для работы с LLM.
Управляет: вызовом модели, retry, валидацией ответа, кэшированием, логированием.

В демо-режиме возвращает шаблонные заглушки (mock).
В production маршрутизирует к DeepSeek / OpenAI / YandexGPT / Gigachat.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Конфигурация для вызова LLM."""

    model: str = "mock"
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 30
    retry_attempts: int = 2
    retry_delay: float = 1.0
    cache_enabled: bool = True

    def __post_init__(self) -> None:
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise ValueError("temperature должен быть в диапазоне [0.0, 2.0]")
        if self.max_tokens < 1:
            raise ValueError("max_tokens должен быть положительным числом")


class LLMContract:
    """Базовый класс для всех LLM-вызовов.

    Обеспечивает:
    - Кэширование ответов (in-memory, по хешу system_prompt + prompt)
    - Retry с экспоненциальной задержкой при ошибках
    - Режим mock для демо-версии
    - Логирование всех вызовов
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        self.config = config or LLMConfig()
        self._cache: dict[str, str] = {}
        self._call_count: int = 0

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: Optional[float] = None,
    ) -> str:
        """Генерация ответа через LLM с кэшированием.

        Args:
            prompt: Пользовательский запрос.
            system_prompt: Системный промпт (роль агента).
            temperature: Температура (переопределяет config).

        Returns:
            Сгенерированный текст.
        """
        self._call_count += 1
        effective_temp = temperature if temperature is not None else self.config.temperature

        cache_key = hashlib.md5(
            (system_prompt + prompt + str(effective_temp)).encode()
        ).hexdigest()

        if self.config.cache_enabled and cache_key in self._cache:
            logger.debug("LLMContract: cache hit for key=%s", cache_key[:8])
            return self._cache[cache_key]

        if self.config.model == "mock":
            result = self._mock_response(prompt, system_prompt)
        else:
            result = await self._call_with_retry(prompt, system_prompt, effective_temp)

        if self.config.cache_enabled:
            self._cache[cache_key] = result

        logger.info(
            "LLMContract: model=%s call=%d len=%d",
            self.config.model,
            self._call_count,
            len(result),
        )
        return result

    # ------------------------------------------------------------------
    # Mock (демо-режим)
    # ------------------------------------------------------------------

    def _mock_response(self, prompt: str, system_prompt: str = "") -> str:
        """Заглушка для демо-режима.

        Возвращает случайный шаблонный ответ, имитирующий работу юриста.
        """
        prompts_map = {
            "договор": "После анализа условий договора, рекомендуем обратить внимание "
                       "на следующие положения:\n\n1. **Ответственность сторон** — "
                       "предусмотрена ли неустойка?\n2. **Сроки** — соответствуют ли "
                       "реальным бизнес-процессам?\n3. **Конфиденциальность** — "
                       "достаточен ли режим защиты данных?",
            "претензи": "На основании предоставленных документов, претензия "
                        "подлежит удовлетворению в части:\n\n1. Основной долг\n"
                        "2. Неустойка за просрочку\n3. Убытки (при наличии "
                        "доказательств)",
            "иск": "Для подготовки искового заявления необходимы:\n\n"
                   "1. Договор (со всеми допсоглашениями)\n"
                   "2. Акт сверки расчётов\n"
                   "3. Переписка сторон (досудебная)\n"
                   "4. Доказательства направления претензии",
            "суд": "Анализ судебной перспективы:\n\n"
                   "1. **Правовая позиция** — оценка 70%/30% в пользу доверителя\n"
                   "2. **Судебная практика** — не менее 3 аналогичных дел "
                   "в вашу пользу\n3. **Риски** — возможное оставление иска "
                   "без рассмотрения",
            "жалоб": "Апелляционная жалоба может быть подана в течение "
                     "1 месяца с даты изготовления решения в окончательной "
                     "форме. Рекомендуем:\n\n1. Проверить доводы суда\n"
                     "2. Подготовить альтернативный расчёт\n"
                     "3. Приложить дополнительные доказательства",
        }

        for keyword, response in prompts_map.items():
            if keyword in prompt.lower():
                return f"[ДЕМО-РЕЖИМ] {response}\n\n---\nВаш запрос: {prompt[:150]}..."

        general_responses = [
            "На основании анализа предоставленных документов, рекомендуем "
            "следующий порядок действий...",
            "В соответствии с действующим законодательством РФ, "
            "данный вопрос регулируется следующими нормами...",
            "После изучения материалов дела, можно сделать следующие выводы...",
            "Для подготовки документа необходимы следующие исходные данные...",
        ]
        return f"[ДЕМО-РЕЖИМ] {random.choice(general_responses)}\n\n---\nВаш запрос: {prompt[:150]}..."

    # ------------------------------------------------------------------
    # Production LLM
    # ------------------------------------------------------------------

    async def _call_with_retry(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float,
    ) -> str:
        """Вызов LLM с retry-логикой."""
        last_error: Optional[Exception] = None

        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                return await self._call_real_llm(prompt, system_prompt, temperature)
            except Exception as exc:
                logger.warning(
                    "LLM call attempt %d/%d failed: %s",
                    attempt,
                    self.config.retry_attempts,
                    exc,
                )
                last_error = exc
                if attempt < self.config.retry_attempts:
                    delay = self.config.retry_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

        logger.error("All LLM retry attempts exhausted")
        return f"[ОШИБКА] Не удалось получить ответ от LLM после {self.config.retry_attempts} попыток. Последняя ошибка: {last_error}"

    async def _call_real_llm(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float,
    ) -> str:
        """Вызов реальной LLM (заглушка для демо).

        В production здесь будет интеграция с DeepSeek / OpenAI / YandexGPT.
        """
        return self._mock_response(prompt, system_prompt)

    # ------------------------------------------------------------------
    # Утилиты
    # ------------------------------------------------------------------

    def clear_cache(self) -> None:
        """Очистка кэша ответов."""
        self._cache.clear()

    @property
    def call_count(self) -> int:
        """Количество вызовов generate() за время жизни экземпляра."""
        return self._call_count
