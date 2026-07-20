import json
import urllib.error
import urllib.request

from app.core.config import settings


class LLMUnavailableError(Exception):
    """Raised when the LLM backend (Ollama) can't be reached — surfaced as a clean 503."""


class OllamaProvider:
    """
    Local Ollama chat provider. Kept behind a small interface (`.chat(messages)`) so a hosted
    provider (Claude/OpenAI) can be swapped in later without touching the mentor service.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    def chat(self, messages: list[dict], *, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise LLMUnavailableError(str(exc)) from exc
        return (data.get("message") or {}).get("content", "").strip()


def get_provider() -> OllamaProvider:
    return OllamaProvider()
