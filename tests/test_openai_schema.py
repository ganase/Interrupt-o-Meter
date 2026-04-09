from app.schemas import OpenAIVisionResult


def test_openai_schema_validation() -> None:
    valid = OpenAIVisionResult.model_validate(
        {
            "visual_busy_score": 55,
            "confidence": 0.7,
            "reasons": ["モニター注視", "入力中"],
            "caution": "過信しないでください",
        }
    )
    assert valid.visual_busy_score == 55
