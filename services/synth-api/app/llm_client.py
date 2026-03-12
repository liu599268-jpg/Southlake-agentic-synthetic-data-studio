from __future__ import annotations

from typing import Iterable

from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL


class NarrativeClient:
    def __init__(self) -> None:
        self.enabled = bool(OPENAI_API_KEY)
        self.client = OpenAI(api_key=OPENAI_API_KEY) if self.enabled else None

    def polish_bullets(
        self,
        title: str,
        context_lines: Iterable[str],
        fallback: list[str],
    ) -> list[str]:
        if not self.enabled or self.client is None:
            return fallback

        prompt = "\n".join(context_lines)

        try:
            response = self.client.responses.create(
                model=OPENAI_MODEL,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Rewrite the provided context into exactly three concise, "
                            "pitch-ready bullet points for a healthcare planning and "
                            "innovation demo. Keep the language suitable for a "
                            "non-clinical prototype. "
                            "Do not use markdown bullets or numbering."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"{title}\n\n{prompt}",
                    },
                ],
                temperature=0.4,
            )
            text = response.output_text.strip()
            bullets = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
            return bullets[:3] if bullets else fallback
        except Exception:
            return fallback
