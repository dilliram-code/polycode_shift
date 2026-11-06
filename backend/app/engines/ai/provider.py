"""
PolyShift - AI Provider Adapter
Provides optional LLM-assisted translation, explanation, and automated repair.
Seamlessly falls back to deterministic engines when no API key is configured.
"""
import os
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

class AIProvider:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")

    def is_available(self) -> bool:
        return bool(self.gemini_key or self.openai_key)

    def get_status(self) -> Dict[str, Any]:
        return {
            "available": self.is_available(),
            "gemini_configured": bool(self.gemini_key),
            "openai_configured": bool(self.openai_key),
            "active_provider": "gemini" if self.gemini_key else ("openai" if self.openai_key else "none")
        }

    async def assist_translation(
        self,
        source_code: str,
        source_lang: str,
        target_lang: str,
        notes: str = ""
    ) -> Optional[str]:
        """
        Uses configured LLM to assist translation when deterministic conversion has edge-cases.
        Returns None if no LLM is configured or request fails.
        """
        if not self.is_available():
            return None

        prompt = (
            f"You are PolyShift AI Compiler. Translate the following {source_lang} code into idiomatic {target_lang}.\n"
            f"Preserve logic, control structures, types, and algorithmic correctness.\n"
            f"Output ONLY the translated {target_lang} code without markdown backticks or commentary.\n\n"
            f"{source_code}"
        )

        try:
            if self.gemini_key:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL_GEMINI}:generateContent?key={self.gemini_key}"
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json={
                        "contents": [{"parts": [{"text": prompt}]}]
                    })
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        # Clean markdown quotes if returned
                        if text.startswith("```"):
                            lines = text.splitlines()
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].strip() == "```":
                                lines = lines[:-1]
                            text = "\n".join(lines)
                        return text.strip()

            elif self.openai_key:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.openai_key}"}
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, headers=headers, json={
                        "model": settings.AI_MODEL_OPENAI,
                        "messages": [
                            {"role": "system", "content": f"You are a strict code transpiler from {source_lang} to {target_lang}."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1
                    })
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"]
                        if text.startswith("```"):
                            lines = text.splitlines()
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].strip() == "```":
                                lines = lines[:-1]
                            text = "\n".join(lines)
                        return text.strip()
        except Exception:
            return None

        return None

ai_provider = AIProvider()
