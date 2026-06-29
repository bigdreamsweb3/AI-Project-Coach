from collections.abc import Sequence

from .config import configuration_help
from .types import CoachConfig


class AiConfigurationError(RuntimeError):
    pass


class AnthropicProvider:
    name = "claude"

    def __init__(self, api_key: str, model: str) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise AiConfigurationError(
                "The Anthropic SDK is not installed. Install it with: pip install anthropic"
            ) from exc

        self.model = model
        self.client = Anthropic(api_key=api_key)

    def generate(self, prompt: str, max_tokens: int) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(getattr(block, "text", "") for block in response.content)
        return text.strip()


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise AiConfigurationError(
                "The Google GenAI SDK is not installed. Install it with: pip install google-genai"
            ) from exc

        self.model = model
        self.types = types
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str, max_tokens: int) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.types.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        return (response.text or "").strip()


class AiRouter:
    def __init__(
        self,
        providers: Sequence[AnthropicProvider | GeminiProvider],
        provider_order: Sequence[str],
    ) -> None:
        self.providers = list(providers)
        self.provider_order = tuple(provider_order)
        if not self.providers:
            raise AiConfigurationError(configuration_help())

    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        errors: list[str] = []
        providers = sorted(
            self.providers,
            key=lambda provider: self.provider_order.index(provider.name)
            if provider.name in self.provider_order
            else len(self.provider_order),
        )

        for provider in providers:
            try:
                text = provider.generate(prompt, max_tokens)
                if text:
                    return text
                errors.append(f"{provider.name}: empty response")
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")

        joined_errors = "\n".join(f"  - {error}" for error in errors)
        raise RuntimeError(f"All configured AI providers failed:\n{joined_errors}")


def build_ai_router(config: CoachConfig) -> AiRouter:
    providers: list[AnthropicProvider | GeminiProvider] = []
    setup_errors: list[str] = []

    if config.anthropic_api_key:
        try:
            providers.append(AnthropicProvider(config.anthropic_api_key, config.anthropic_model))
        except AiConfigurationError as exc:
            setup_errors.append(f"Claude: {exc}")

    if config.gemini_api_key:
        try:
            providers.append(GeminiProvider(config.gemini_api_key, config.gemini_model))
        except AiConfigurationError as exc:
            setup_errors.append(f"Gemini: {exc}")

    if providers:
        return AiRouter(providers, config.provider_order)

    details = "\n".join(setup_errors)
    if details:
        raise AiConfigurationError(f"{details}\n\n{configuration_help()}")
    raise AiConfigurationError(configuration_help())
