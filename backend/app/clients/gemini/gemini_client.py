import google.generativeai as genai
from app.config.settings import settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Send a prompt to Gemini and return the text response."""
        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def generate_structured(self, prompt: str) -> str:
        """Generate with lower temperature for structured/factual outputs."""
        return await self.generate(prompt, temperature=0.2)
