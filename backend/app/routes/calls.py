import uuid
import os
import json

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.lead import Lead, LeadStatus
from app.models.campaign import Campaign, CampaignStatus
from app.models.call_log import CallLog
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.utils.auth import decode_token
from app.services.voice_service import VoiceService
from app.services.conversation_service import ConversationService
from app.services.tts_service import TextToSpeechService
from app.config import settings
from app.ws_manager import manager

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/calls", tags=["Calls"])
conversation_service = ConversationService()

# In-memory conversation state (use Redis in production)
active_calls: dict[str, list[dict]] = {}
call_lead_map: dict[str, uuid.UUID] = {}
ai_audio_store: dict[str, bytes] = {}


@router.websocket("/ws")
async def call_ws(websocket: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        await websocket.close(code=4001)
        return
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/initiate")
async def initiate_call(
    lead_id: uuid.UUID,
    campaign_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    call_log = CallLog(
        lead_id=lead_id,
        campaign_id=campaign_id,
        status="initiated",
    )
    db.add(call_log)
    await db.commit()
    await db.refresh(call_log)

    webhook_url = f"{settings.SIGNALWIRE_WEBHOOK_BASE_URL}/api/calls/outbound-twiml/{call_log.id}"

    try:
        call_sid = await VoiceService.make_call(lead.phone, webhook_url)
        call_lead_map[call_sid] = lead_id
        return {"call_sid": call_sid, "call_log_id": str(call_log.id)}
    except Exception as e:
        call_log.status = "failed"
        call_log.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outbound-twiml/{call_log_id}")
async def outbound_twiml(call_log_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CallLog).where(CallLog.id == call_log_id))
    call_log = result.scalar_one_or_none()

    greeting = "Assalam-o-Alaikum!"
    if call_log and call_log.campaign_id:
        camp_result = await db.execute(select(Campaign).where(Campaign.id == call_log.campaign_id))
        campaign = camp_result.scalar_one_or_none()
        if campaign and campaign.greeting_message:
            greeting = campaign.greeting_message

    twiml = VoiceService.generate_twiml_greeting(greeting)
    return Response(content=twiml, media_type="application/xml")


@router.post("/process-speech")
async def process_speech(request: Request):
    form_data = await request.form()
    speech_result = form_data.get("SpeechResult", "")
    call_sid = form_data.get("CallSid", "")
    call_log_id_str = request.query_params.get("call_log_id", "")

    if call_sid not in active_calls:
        active_calls[call_sid] = []

    transcript = active_calls[call_sid]
    transcript.append({"role": "user", "content": speech_result})

    # Check for exit keywords
    exit_keywords = ["allah hafiz", "bye", "goodbye", "ni chahye", "nahi", "not interested"]
    if any(kw in speech_result.lower() for kw in exit_keywords):
        closing = "Shukriya aap se baat karne ka! Allah Hafiz."
        twiml = VoiceService.generate_twiml_hangup(closing)
        return Response(content=twiml, media_type="application/xml")

    try:
        result = await conversation_service.process_text_input(
            customer_input=speech_result,
            transcript=transcript,
        )
        ai_text = result["ai_response"]
        ai_audio = result["audio_bytes"]
        transcript.append({"role": "assistant", "content": ai_text})
        ai_audio_store[call_sid] = ai_audio

        await manager.broadcast("transcript", {
            "call_sid": call_sid,
            "entry": {"role": "user", "content": speech_result},
        })
        await manager.broadcast("transcript", {
            "call_sid": call_sid,
            "entry": {"role": "assistant", "content": ai_text},
        })

        audio_url = f"{settings.SIGNALWIRE_WEBHOOK_BASE_URL}/api/calls/audio-response/{call_sid}"
        twiml = VoiceService.generate_twiml_response(audio_url)
        return Response(content=twiml, media_type="application/xml")
    except Exception as e:
        logger.error("process_speech_error", error=str(e))
        fallback = "Mujhe maaf karein, koi technical issue aa gaya hai. Koi insan aap se dobara contact kare ga."
        twiml = VoiceService.generate_twiml_hangup(fallback)
        return Response(content=twiml, media_type="application/xml")


@router.get("/audio-response/{call_sid}")
async def serve_audio(call_sid: str):
    audio = ai_audio_store.get(call_sid)
    if not audio:
        return Response(status_code=404, content="Audio not found")
    return StreamingResponse(
        iter([audio]),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline"},
    )


@router.post("/status")
async def call_status(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    call_status_val = form_data.get("CallStatus", "")
    call_duration = form_data.get("CallDuration", "0")

    await manager.broadcast("call_status", {
        "call_sid": call_sid,
        "status": call_status_val,
        "duration": call_duration,
    })

    lead_id = call_lead_map.pop(call_sid, None)
    transcript = active_calls.pop(call_sid, None)

    if lead_id and transcript:
        background_tasks.add_task(
            _finalize_call, lead_id, transcript, call_sid, call_status_val, call_duration
        )

    return {"status": "ok"}


async def _finalize_call(
    lead_id_str: str,
    transcript: list[dict],
    call_sid: str,
    call_status: str,
    call_duration: str,
):
    from app.database import async_session

    async with async_session() as db:
        result = await db.execute(select(Lead).where(Lead.id == uuid.UUID(lead_id_str)))
        lead = result.scalar_one_or_none()
        if not lead:
            return

        result = await db.execute(
            select(CallLog).where(CallLog.lead_id == lead.id).order_by(CallLog.created_at.desc())
        )
        call_log = result.scalar_one_or_none()

        if transcript:
            result_data = await conversation_service.finalize_conversation(transcript)

            lead.status = LeadStatus(result_data["lead_status"])

            if call_log:
                call_log.status = call_status or "completed"
                call_log.duration_seconds = int(call_duration) if call_duration.isdigit() else None
                call_log.transcript = transcript
                call_log.summary = result_data["summary"]
                call_log.sentiment_score = result_data["sentiment_score"]
                call_log.lead_status = result_data["lead_status"]
                call_log.extra_data = {"call_sid": call_sid}

        await db.commit()


@router.post("/test-local/{lead_id}")
async def test_local_call(
    lead_id: uuid.UUID,
    campaign_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    call_log = CallLog(
        lead_id=lead_id,
        campaign_id=campaign_id,
        status="in-progress",
    )
    db.add(call_log)
    await db.commit()
    await db.refresh(call_log)

    from app.services.conversation_service import ConversationService
    cs = ConversationService()
    transcript = []
    greeting = "Hello! I'm calling from NCAI Insurance about our health insurance plans."

    tts = TextToSpeechService()
    audio = await tts.synthesize(greeting)
    ai_audio_store[str(call_log.id)] = audio
    transcript.append({"role": "assistant", "content": greeting})

    return {
        "call_log_id": str(call_log.id),
        "greeting": greeting,
        "audio_url": f"{settings.SIGNALWIRE_WEBHOOK_BASE_URL}/api/calls/audio-response/{call_log.id}",
        "message": "Test call initiated. Use text input to continue the conversation.",
        "next_action": "POST /api/calls/test-process-speech with {call_log_id, text}",
    }


@router.post("/test-process-speech")
async def test_process_speech(
    call_log_id: uuid.UUID,
    text: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    transcript_key = f"test_{call_log_id}"
    if transcript_key not in active_calls:
        active_calls[transcript_key] = []

    transcript = active_calls[transcript_key]
    transcript.append({"role": "user", "content": text})

    exit_keywords = ["goodbye", "bye", "not interested", "no thanks", "bye bye", "take care"]
    if any(kw in text.lower() for kw in exit_keywords):
        from app.services.tts_service import TextToSpeechService
        tts = TextToSpeechService()
        closing = "Thank you for your time! Have a great day."
        audio = await tts.synthesize(closing)
        ai_audio_store[str(call_log_id)] = audio
        transcript.append({"role": "assistant", "content": closing})

        result = await db.execute(select(CallLog).where(CallLog.id == call_log_id))
        call_log = result.scalar_one_or_none()
        if call_log:
            call_log.status = "completed"
            call_log.transcript = transcript
            call_log.duration_seconds = len(transcript) * 10
            await db.commit()

        await manager.broadcast("call_status", {
            "call_sid": str(call_log_id),
            "status": "completed",
        })

        return {
            "ai_response": closing,
            "audio_url": f"{settings.SIGNALWIRE_WEBHOOK_BASE_URL}/api/calls/audio-response/{call_log_id}",
            "completed": True,
        }

    result = await conversation_service.process_text_input(
        customer_input=text,
        transcript=transcript,
    )
    ai_text = result["ai_response"]

    from app.services.tts_service import TextToSpeechService
    tts = TextToSpeechService()
    ai_audio = await tts.synthesize(ai_text)
    ai_audio_store[str(call_log_id)] = ai_audio

    await manager.broadcast("transcript", {
        "call_sid": str(call_log_id),
        "entry": {"role": "user", "content": text},
    })
    await manager.broadcast("transcript", {
        "call_sid": str(call_log_id),
        "entry": {"role": "assistant", "content": ai_text},
    })

    return {
        "ai_response": ai_text,
        "audio_url": f"{settings.SIGNALWIRE_WEBHOOK_BASE_URL}/api/calls/audio-response/{call_log_id}",
        "completed": False,
    }


def _get_db_session():
    from app.database import async_session
    return async_session


@router.get("/history")
async def call_history(
    lead_id: str | None = None,
    campaign_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    from sqlalchemy import select, func
    from app.schemas.call_log import CallLogListResponse, CallLogResponse

    query = select(CallLog)

    if lead_id:
        query = query.where(CallLog.lead_id == uuid.UUID(lead_id))
    if campaign_id:
        query = query.where(CallLog.campaign_id == uuid.UUID(campaign_id))
    if status:
        query = query.where(CallLog.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.order_by(CallLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    call_logs = result.scalars().all()

    return CallLogListResponse(total=total, call_logs=call_logs)
