from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from app.config import settings
from app.repositories.event_repo import list_events
from app.repositories.result_repo import insert_result
from app.schemas import AnalyzeFrameRequest, AnalyzeFrameResponse, ScoreRequest, ScoreResponse
from app.services.comment_builder import build_comment
from app.services.openai_vision import analyze_visual_busy, score_interruptability
from app.services.scoring import blend_busy_scores, calculate_schedule_busy_score

router = APIRouter(tags=["camera"])


@router.post("/api/score", response_model=ScoreResponse)
async def score_image(req: ScoreRequest) -> ScoreResponse:
    result = await score_interruptability(req.image_data_url, req.source_label)
    return ScoreResponse(
        **result.model_dump(by_alias=True),
        model=settings.openai_model,
        sourceLabel=req.source_label,
        generatedAt=datetime.now(timezone.utc),
    )


@router.post("/api/analyze/frame", response_model=AnalyzeFrameResponse)
async def analyze_frame(req: AnalyzeFrameRequest) -> AnalyzeFrameResponse:
    lookback_start = req.captured_at - timedelta(days=1)
    lookahead_end = req.captured_at + timedelta(days=1)

    events = list_events(req.source_user, lookback_start, lookahead_end)
    schedule_score = calculate_schedule_busy_score(events, req.captured_at)

    visual = await analyze_visual_busy(req.image_base64)
    blended, talk_ok = blend_busy_scores(
        schedule_busy_score=schedule_score,
        visual_busy_score=visual.visual_busy_score,
        sw=settings.schedule_weight,
        vw=settings.visual_weight,
    )
    comment = build_comment(talk_ok)

    insert_result(
        source_user=req.source_user,
        captured_at=req.captured_at,
        schedule_busy_score=schedule_score,
        visual_busy_score=visual.visual_busy_score,
        blended_busy_score=blended,
        talk_ok_score=talk_ok,
        confidence=visual.confidence,
        reasons=visual.reasons,
        comment_text=comment,
        image_saved_flag=False,
    )

    return AnalyzeFrameResponse(
        source_user=req.source_user,
        captured_at=req.captured_at,
        schedule_busy_score=schedule_score,
        visual_busy_score=visual.visual_busy_score,
        blended_busy_score=blended,
        talk_ok_score=talk_ok,
        confidence=visual.confidence,
        reasons=visual.reasons,
        comment=comment,
        disclaimer="これはジョーク判定です。真に受けないでください。",
    )
