from openai import AsyncOpenAI
from app.core.config import settings

class AIService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = settings.AI_MODEL

    async def summarize_text(self, text: str) -> str:
        """Генерирует краткую смысловую выжимку переданного текста."""
        prompt = (
                    "Ты — аналитический модуль системы DocSense.\n"
                    "Твоя задача — предоставить краткий аналитический отчет по документу, а НЕ копировать его содержимое целиком.\n\n"
                    "Формат ответа:\n"
                    "1. **Тип и тема документа**: (например, словарь английских слов, договор, отчет и т.д.)\n"
                    "2. **Краткая суть**: (о чем документ в 2-3 предложениях)\n"
                    "3. **Основные моменты / примеры**: (выдели 3-5 ключевых пунктов или характерных примеров, не перечисляя всё подряд)\n\n"
                    f"Содержимое документа:\n\"\"\"\n{text}\n\"\"\""
                )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Отвечай структурированно на русском языке."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

ai_service = AIService()