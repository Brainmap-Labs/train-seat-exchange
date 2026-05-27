"""Unified AI provider service (OpenAI + Google Gemini) with automatic fallback."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

ProviderName = str  # "openai" | "gemini"


class AIServiceError(Exception):
    pass


class AIService:
    """Call OpenAI or Gemini for JSON-formatted chat completions."""

    GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self) -> None:
        self.provider_preference = (settings.AI_PROVIDER or "auto").strip().lower()
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL
        self._openai_client = None

    def is_available(self) -> bool:
        return bool(self.openai_api_key or self.gemini_api_key)

    def available_providers(self) -> List[ProviderName]:
        providers: List[ProviderName] = []
        if self.gemini_api_key:
            providers.append("gemini")
        if self.openai_api_key:
            providers.append("openai")
        return providers

    def _provider_order(self) -> List[ProviderName]:
        available = self.available_providers()
        if not available:
            return []

        if self.provider_preference == "openai":
            order = ["openai", "gemini"]
        elif self.provider_preference == "gemini":
            order = ["gemini", "openai"]
        else:
            # auto: prefer Gemini when both are configured (often cheaper / separate quota)
            order = ["gemini", "openai"]

        return [p for p in order if p in available]

    @staticmethod
    def _parse_json_response(text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return json.loads(cleaned)

    def _get_openai_client(self):
        if self._openai_client is not None:
            return self._openai_client
        if not self.openai_api_key:
            raise AIServiceError("OpenAI API key not configured")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AIServiceError("openai package not installed") from exc
        self._openai_client = OpenAI(api_key=self.openai_api_key)
        return self._openai_client

    def _chat_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> Dict[str, Any]:
        client = self._get_openai_client()
        response = client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or ""
        return self._parse_json_response(content)

    def _chat_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> Dict[str, Any]:
        if not self.gemini_api_key:
            raise AIServiceError("Gemini API key not configured")

        url = (
            f"{self.GEMINI_API_BASE}/models/{self.gemini_model}:generateContent"
            f"?key={self.gemini_api_key}"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload)
            if response.status_code >= 400:
                detail = response.text[:500]
                raise AIServiceError(f"Gemini API error {response.status_code}: {detail}")

            data = response.json()
            candidates = data.get("candidates") or []
            if not candidates:
                raise AIServiceError("Gemini returned no candidates")

            parts = candidates[0].get("content", {}).get("parts") or []
            text = "".join(part.get("text", "") for part in parts).strip()
            if not text:
                raise AIServiceError("Gemini returned empty content")
            return self._parse_json_response(text)

    def chat_json_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> Tuple[Dict[str, Any], ProviderName]:
        errors: List[str] = []
        for provider in self._provider_order():
            try:
                if provider == "openai":
                    result = self._chat_openai(system_prompt, user_prompt, temperature)
                else:
                    result = self._chat_gemini(system_prompt, user_prompt, temperature)
                logger.info("AI request succeeded via %s", provider)
                return result, provider
            except Exception as exc:
                msg = f"{provider}: {exc}"
                logger.warning("AI provider failed — %s", msg)
                errors.append(msg)

        raise AIServiceError(
            "All AI providers failed. "
            + ("; ".join(errors) if errors else "No API keys configured.")
        )

    async def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> Tuple[Dict[str, Any], ProviderName]:
        return await asyncio.to_thread(
            self.chat_json_sync,
            system_prompt,
            user_prompt,
            temperature,
        )
