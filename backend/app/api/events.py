from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Event, BudgetCategory, Expense, Task
from app.schemas import (
    EventCreate, EventUpdate, EventResponse,
    BudgetCategoryCreate, BudgetCategoryUpdate, BudgetCategoryResponse,
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, BudgetSummary,
    BudgetSimulationRequest, TaskCreate, TaskUpdate, TaskResponse,
)
from app.services.budget_service import calculate_budget_allocations, compute_budget_summary, generate_timeline_tasks
from app.services.ai_service import generate_event_plan
from datetime import datetime, timezone

router = APIRouter(prefix="/events", tags=["Events"])


def _check_event_owner(event: Event, user: User):
    if event.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this event")


# ─── Events CRUD ─────────────────────────────────────────────────────────────

@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event = Event(**data.model_dump(), owner_id=current_user.id)
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return EventResponse.model_validate(event)


@router.get("", response_model=List[EventResponse])
async def list_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event).where(Event.owner_id == current_user.id).order_by(Event.created_at.desc())
    )
    return [EventResponse.model_validate(e) for e in result.scalars().all()]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)
    return EventResponse.model_validate(event)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(event, field, value)

    await db.flush()
    await db.refresh(event)
    return EventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)
    await db.delete(event)


# ─── AI Plan Generation ───────────────────────────────────────────────────────

@router.post("/{event_id}/generate-plan", response_model=EventResponse)
async def generate_plan(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    event_dict = EventResponse.model_validate(event).model_dump(mode="json")
    ai_plan = await generate_event_plan(event_dict)
    event.ai_plan = ai_plan

    # Auto-generate budget categories if none exist
    cat_result = await db.execute(
        select(BudgetCategory).where(BudgetCategory.event_id == event_id)
    )
    existing_cats = cat_result.scalars().all()
    if not existing_cats and event.total_budget > 0:
        allocations = calculate_budget_allocations(event.total_budget, event.event_type.value)
        for alloc in allocations:
            cat = BudgetCategory(
                event_id=event_id,
                name=alloc["name"],
                allocated_amount=alloc["allocated_amount"],
                color=alloc["color"],
            )
            db.add(cat)

    # Auto-generate tasks if none exist
    task_result = await db.execute(select(Task).where(Task.event_id == event_id))
    existing_tasks = task_result.scalars().all()
    if not existing_tasks and event.event_date:
        now = datetime.now(timezone.utc)
        event_dt = event.event_date.replace(tzinfo=timezone.utc) if event.event_date.tzinfo is None else event.event_date
        days_until = max(1, (event_dt - now).days)
        timeline_tasks = generate_timeline_tasks(event_dt, event.event_type.value, days_until)
        for t in timeline_tasks:
            from app.models import TaskPriority, TaskStatus
            task = Task(
                event_id=event_id,
                title=t["title"],
                priority=TaskPriority(t["priority"]),
                due_date=datetime.fromisoformat(t["due_date"]),
                status=TaskStatus(t["status"]),
            )
            db.add(task)

    await db.flush()
    await db.refresh(event)
    return EventResponse.model_validate(event)


# ─── Budget ───────────────────────────────────────────────────────────────────

@router.get("/{event_id}/budget", response_model=BudgetSummary)
async def get_budget_summary(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    cat_result = await db.execute(
        select(BudgetCategory)
        .where(BudgetCategory.event_id == event_id)
        .options(selectinload(BudgetCategory.expenses))
    )
    categories = cat_result.scalars().all()
    cat_dicts = [BudgetCategoryResponse.model_validate(c).model_dump(mode="json") for c in categories]

    summary = compute_budget_summary(event.total_budget, cat_dicts)
    summary["categories"] = [BudgetCategoryResponse.model_validate(c) for c in categories]
    return BudgetSummary(**summary)


@router.post("/{event_id}/budget/categories", response_model=BudgetCategoryResponse, status_code=201)
async def create_budget_category(
    event_id: int,
    data: BudgetCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    cat = BudgetCategory(event_id=event_id, **data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return BudgetCategoryResponse.model_validate(cat)


@router.put("/{event_id}/budget/categories/{cat_id}", response_model=BudgetCategoryResponse)
async def update_budget_category(
    event_id: int,
    cat_id: int,
    data: BudgetCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    cat_result = await db.execute(
        select(BudgetCategory).where(BudgetCategory.id == cat_id, BudgetCategory.event_id == event_id)
    )
    cat = cat_result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(cat, field, value)
    await db.flush()
    await db.refresh(cat)
    return BudgetCategoryResponse.model_validate(cat)


@router.post("/{event_id}/budget/categories/{cat_id}/expenses", response_model=ExpenseResponse, status_code=201)
async def add_expense(
    event_id: int,
    cat_id: int,
    data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    expense = Expense(category_id=cat_id, **data.model_dump())
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return ExpenseResponse.model_validate(expense)


@router.put("/{event_id}/budget/categories/{cat_id}/expenses/{exp_id}", response_model=ExpenseResponse)
async def update_expense(
    event_id: int,
    cat_id: int,
    exp_id: int,
    data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    exp_result = await db.execute(select(Expense).where(Expense.id == exp_id, Expense.category_id == cat_id))
    expense = exp_result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(expense, field, value)
    await db.flush()
    await db.refresh(expense)
    return ExpenseResponse.model_validate(expense)


# ─── Tasks ────────────────────────────────────────────────────────────────────

@router.get("/{event_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    task_result = await db.execute(
        select(Task).where(Task.event_id == event_id).order_by(Task.due_date)
    )
    return [TaskResponse.model_validate(t) for t in task_result.scalars().all()]


@router.post("/{event_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    event_id: int,
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    task = Task(event_id=event_id, **data.model_dump())
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return TaskResponse.model_validate(task)


@router.put("/{event_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    event_id: int,
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    task_result = await db.execute(
        select(Task).where(Task.id == task_id, Task.event_id == event_id)
    )
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = data.model_dump(exclude_none=True)
    if update_data.get("status") == "completed" and task.status != "completed":
        from datetime import datetime, timezone
        update_data["completed_at"] = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(task, field, value)
    await db.flush()
    await db.refresh(task)
    return TaskResponse.model_validate(task)


@router.delete("/{event_id}/tasks/{task_id}", status_code=204)
async def delete_task(
    event_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, current_user)

    task_result = await db.execute(
        select(Task).where(Task.id == task_id, Task.event_id == event_id)
    )
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
