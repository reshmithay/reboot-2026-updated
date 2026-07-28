import requests
import logging
from typing import Optional
import urllib3

from app.config.settings import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class CortexClient:
    """Client for Lloyds Cortex API - Gemini integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        timeout: Optional[int] = None,
    ):
        self.api_key = api_key or settings.CORTEX_API_KEY
        self.base_url = base_url or settings.CORTEX_BASE_URL
        self.model = model or settings.CORTEX_MODEL
        self.temperature = temperature or settings.CORTEX_TEMPERATURE
        self.timeout = timeout or settings.CORTEX_TIMEOUT

    def chat(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Send a chat completion request to Cortex API.

        Args:
            prompt: User prompt
            system_message: Optional system message
            model: Override default model
            temperature: Override default temperature

        Returns:
            Generated text response
        """
        url = f"{self.base_url}/v1/chat/completions"

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.model,
            "temperature": temperature or self.temperature,
            "messages": messages,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            logger.info(f"Sending request to Cortex API: {url}")
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                verify=False,  # Note: SSL verification disabled for internal API
            )

            response.raise_for_status()
            result = response.json()

            content = result["choices"][0]["message"]["content"]
            logger.info(f"Received response from Cortex API ({len(content)} chars)")
            return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Cortex API request failed: {e}")
            raise Exception(f"Failed to generate narrative: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response format from Cortex API: {e}")
            raise Exception(f"Invalid response from Cortex API: {str(e)}")
