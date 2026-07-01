import os

from groq import Groq

from app.llm.base import BaseLLMClient

from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)

class GroqLLMClient(BaseLLMClient):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "llama-3.3-70b-versatile",
    ) -> None:
        resolved_api_key = api_key or os.getenv("GROQ_API_KEY")
        if not resolved_api_key:
            raise ValueError("GROQ_API_KEY is not set")

        self.client = Groq(api_key=resolved_api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You summarize FAIR comparison results faithfully. "
                        "Use only the provided structured facts."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Groq returned empty content")

        return content.strip()