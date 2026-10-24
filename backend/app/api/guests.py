from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Event, Guest
from app.schemas import GuestCreate, GuestUpdate, GuestResponse

router = APIRouter(prefix="/events/{event_id}/guests", tags=["Guests"])


def _check_event_owner(event: Event, user: User):
    if event.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")


async def _get_event(event_id: int, user: User, db: AsyncSession) -> Event:
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _check_event_owner(event, user)
    return event


@router.get("", response_model=List[GuestResponse])
async def list_guests(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_event(event_id, current_user, db)
    result = await db.execute(
        select(Guest).where(Guest.event_id == event_id).order_by(Guest.name)
    )
    return [GuestResponse.model_validate(g) for g in result.scalars().all()]


@router.post("", response_model=GuestResponse, status_code=201)
async def add_guest(
    event_id: int,
    data: GuestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_event(event_id, current_user, db)
    guest = Guest(event_id=event_id, **data.model_dump())
    db.add(guest)
    await db.flush()
    await db.refresh(guest)
    return GuestResponse.model_validate(guest)


@router.put("/{guest_id}", response_model=GuestResponse)
async def update_guest(
    event_id: int,
    guest_id: int,
    data: GuestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_event(event_id, current_user, db)
    result = await db.execute(
        select(Guest).where(Guest.id == guest_id, Guest.event_id == event_id)
    )
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(guest, field, value)
    await db.flush()
    await db.refresh(guest)
    return GuestResponse.model_validate(guest)


@router.delete("/{guest_id}", status_code=204)
async def delete_guest(
    event_id: int,
    guest_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_event(event_id, current_user, db)
    result = await db.execute(
        select(Guest).where(Guest.id == guest_id, Guest.event_id == event_id)
    )
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    await db.delete(guest)
