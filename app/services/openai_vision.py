from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import settings
from app.schemas import OpenAIVisionResult


SYSTEM_PROMPT = (
    "あなたはジョークアプリ用の軽い画像判定器です。"
    "人物の心理状態や属性を断定せず、見た目上の忙しさのみ控えめに推定してください。"
    "JSONのみ返してください。"
)


FALLBACK_RESULT = OpenAIVisionResult(
    visual_busy_score=50,
    confidence=0.2,
    reasons=["判定に失敗したため中立値を採用"],
    caution="画像判定に失敗しました",
)


def _extract_text_json(payload: dict[str, Any]) -> str | None:
    try:
        for output in payload.get("output", []):
            for content in output.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    text = content.get("text")
                    if text:
                        return str(text)
    except Exception:
        return None
    return None


async def analyze_visual_busy(image_base64: str) -> OpenAIVisionResult:
    if not settings.openai_api_key:
        return FALLBACK_RESULT

    request_body = {
        "model": settings.openai_model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "この画像の見た目上の忙しさを判定し、"
                            "{visual_busy_score, confidence, reasons, caution} をJSONで返してください。"
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "visual_busy",
                "schema": {
                    "type": "object",
                    "properties": {
                        "visual_busy_score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "reasons": {"type": "array", "items": {"type": "string"}},
                        "caution": {"type": "string"},
                    },
                    "required": ["visual_busy_score", "confidence", "reasons", "caution"],
                    "additionalProperties": False,
                },
            }
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    for _ in range(2):
        try:
            async with httpx.AsyncClient(timeout=settings.openai_timeout_sec) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=request_body,
                )
                response.raise_for_status()
            payload = response.json()
            text_json = _extract_text_json(payload)
            if not text_json:
                continue
            parsed = json.loads(text_json)
            return OpenAIVisionResult.model_validate(parsed)
        except (httpx.HTTPError, json.JSONDecodeError, ValidationError, KeyError, TypeError):
            continue

    return FALLBACK_RESULT
