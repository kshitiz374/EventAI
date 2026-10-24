from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Event, Conversation, Message, Task, BudgetCategory
from app.schemas import (
    ChatRequest, ChatResponse, ConversationResponse, MessageResponse,
    WhatIfSimulationRequest, WhatIfSimulationResponse,
    ChangeProposalResponse,
)
from app.services.ai_service import chat_with_copilot, generate_whatif_simulation, generate_theme_recommendations
from app.models import MessageRole

router = APIRouter(prefix="/ai", tags=["AI"])


async def _get_event_context(event_id: int, user: User, db: AsyncSession) -> Optional[dict]:
    """Load full event context including budget utilization and task count."""
    result = await db.execute(
        select(Event)
        .where(Event.id == event_id, Event.owner_id == user.id)
        .options(selectinload(Event.budget_categories), selectinload(Event.tasks))
    )
    event = result.scalar_one_or_none()
    if not event:
        return None

    total_estimated = 0
    for cat in event.budget_categories:
        cat_result = await db.execute(
            select(BudgetCategory).where(BudgetCategory.id == cat.id)
            .options(selectinload(BudgetCategory.expenses))
        )
        full_cat = cat_result.scalar_one_or_none()
        if full_cat:
            total_estimated += sum(e.estimated_amount for e in full_cat.expenses)

    pending_tasks = sum(1 for t in event.tasks if t.status in ("pending", "in_progress"))
    utilization = (total_estimated / event.total_budget * 100) if event.total_budget else 0

    return {
        "name": event.name,
        "event_type": event.event_type.value,
        "event_date": event.event_date.isoformat() if event.event_date else None,
        "location": event.location,
        "guest_count": event.guest_count,
        "total_budget": event.total_budget,
        "currency": event.currency,
        "theme": event.theme,
        "utilization_pct": utilization,
        "pending_tasks": pending_tasks,
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    event_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get or create conversation
    conversation = None
    if request.conversation_id:
        conv_result = await db.execute(
            select(Conversation)
            .where(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id)
            .options(selectinload(Conversation.messages))
        )
        conversation = conv_result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(
            user_id=current_user.id,
            event_id=event_id,
            title=request.message[:80],
        )
        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)
        conversation.messages = []

    # Load message history
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    history = [{"role": m.role.value, "content": m.content} for m in msg_result.scalars().all()]

    # Get event context
    ctx_event_id = event_id or conversation.event_id
    event_context = None
    if ctx_event_id:
        event_context = await _get_event_context(ctx_event_id, current_user, db)

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_msg)

    # Generate AI response
    ai_reply = await chat_with_copilot(request.message, history, event_context)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=ai_reply,
    )
    db.add(assistant_msg)
    await db.flush()

    return ChatResponse(
        conversation_id=conversation.id,
        message=ai_reply,
        role=MessageRole.ASSISTANT,
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .options(selectinload(Conversation.messages))
        .order_by(Conversation.updated_at.desc())
    )
    return [ConversationResponse.model_validate(c) for c in result.scalars().all()]


@router.get("/conversations/{conv_id}", response_model=ConversationResponse)
async def get_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conv_id, Conversation.user_id == current_user.id)
        .options(selectinload(Conversation.messages))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationResponse.model_validate(conv)


@router.post("/simulate", response_model=WhatIfSimulationResponse)
async def simulate_whatif(
    request: WhatIfSimulationRequest,
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event).where(Event.id == event_id, Event.owner_id == current_user.id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    from app.schemas import EventResponse
    event_dict = EventResponse.model_validate(event).model_dump(mode="json")
    simulation = await generate_whatif_simulation(event_dict, request.scenario_type, request.parameters)
    return WhatIfSimulationResponse(**simulation)


@router.get("/themes/{event_id}")
async def get_theme_recommendations(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event).where(Event.id == event_id, Event.owner_id == current_user.id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    from app.schemas import EventResponse
    event_dict = EventResponse.model_validate(event).model_dump(mode="json")
    return await generate_theme_recommendations(event_dict)


@router.get("/dashboard-stats")
async def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Aggregate real stats from DB for the dashboard."""
    from sqlalchemy import func
    from app.models import Task, Guest, Expense
    from datetime import datetime, timezone

    # Events
    events_result = await db.execute(
        select(Event).where(Event.owner_id == current_user.id)
        .options(selectinload(Event.tasks), selectinload(Event.guests))
    )
    events = events_result.scalars().all()

    total_budget = sum(e.total_budget for e in events)
    upcoming = [e for e in events if e.event_date and e.event_date.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)]
    upcoming_sorted = sorted(upcoming, key=lambda e: e.event_date)[:5]

    # Tasks across all events
    all_task_ids = [e.id for e in events]
    pending_tasks = 0
    overdue_tasks = 0
    now = datetime.now(timezone.utc)

    for event in events:
        for task in event.tasks:
            if task.status in ("pending", "in_progress"):
                pending_tasks += 1
                if task.due_date and task.due_date.replace(tzinfo=timezone.utc) < now:
                    overdue_tasks += 1

    # Guest confirmations
    total_guests = sum(len(e.guests) for e in events)
    confirmed_guests = sum(
        sum(1 for g in e.guests if g.rsvp_status.value == "confirmed")
        for e in events
    )

    return {
        "total_events": len(events),
        "upcoming_events": len(upcoming),
        "total_budget": total_budget,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "total_guests": total_guests,
        "confirmed_guests": confirmed_guests,
        "upcoming_events_list": [
            {
                "id": e.id,
                "name": e.name,
                "event_type": e.event_type.value,
                "event_date": e.event_date.isoformat() if e.event_date else None,
                "location": e.location,
                "status": e.status.value,
                "total_budget": e.total_budget,
                "currency": e.currency,
                "guest_count": e.guest_count,
            }
            for e in upcoming_sorted
        ],
    }
