from app.llm.base import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    def generate(self, prompt: str) -> str:
        return (
            "Mock LLM summary: f-uji scores higher overall, with stronger "
            "findability and accessibility performance than fair-checker."
        )