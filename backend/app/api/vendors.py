from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Event, Vendor, EventVendor
from app.schemas import (
    VendorCreate, VendorUpdate, VendorResponse,
    EventVendorCreate, EventVendorUpdate, EventVendorResponse,
)

router = APIRouter(tags=["Vendors"])

vendors_router = APIRouter(prefix="/vendors")
event_vendors_router = APIRouter(prefix="/events/{event_id}/vendors")


# ─── Global Vendor CRUD ───────────────────────────────────────────────────────

@vendors_router.get("", response_model=List[VendorResponse])
async def list_vendors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vendor).where(Vendor.owner_id == current_user.id).order_by(Vendor.name)
    )
    return [VendorResponse.model_validate(v) for v in result.scalars().all()]


@vendors_router.post("", response_model=VendorResponse, status_code=201)
async def create_vendor(
    data: VendorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    vendor = Vendor(owner_id=current_user.id, **data.model_dump())
    db.add(vendor)
    await db.flush()
    await db.refresh(vendor)
    return VendorResponse.model_validate(vendor)


@vendors_router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: int,
    data: VendorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id, Vendor.owner_id == current_user.id)
    )
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(vendor, field, value)
    await db.flush()
    await db.refresh(vendor)
    return VendorResponse.model_validate(vendor)


@vendors_router.delete("/{vendor_id}", status_code=204)
async def delete_vendor(
    vendor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id, Vendor.owner_id == current_user.id)
    )
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    await db.delete(vendor)


# ─── Event Vendor Assignments ─────────────────────────────────────────────────

@event_vendors_router.get("", response_model=List[EventVendorResponse])
async def list_event_vendors(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    event = event_result.scalar_one_or_none()
    if not event or event.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")

    result = await db.execute(
        select(EventVendor)
        .where(EventVendor.event_id == event_id)
        .options(selectinload(EventVendor.vendor))
    )
    return [EventVendorResponse.model_validate(ev) for ev in result.scalars().all()]


@event_vendors_router.post("", response_model=EventVendorResponse, status_code=201)
async def add_vendor_to_event(
    event_id: int,
    data: EventVendorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    event = event_result.scalar_one_or_none()
    if not event or event.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")

    # Verify vendor belongs to user
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.id == data.vendor_id, Vendor.owner_id == current_user.id)
    )
    if not vendor_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vendor not found")

    ev = EventVendor(event_id=event_id, **data.model_dump())
    db.add(ev)
    await db.flush()

    ev_result = await db.execute(
        select(EventVendor).where(EventVendor.id == ev.id).options(selectinload(EventVendor.vendor))
    )
    return EventVendorResponse.model_validate(ev_result.scalar_one())


@event_vendors_router.put("/{ev_id}", response_model=EventVendorResponse)
async def update_event_vendor(
    event_id: int,
    ev_id: int,
    data: EventVendorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    event = event_result.scalar_one_or_none()
    if not event or event.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")

    result = await db.execute(
        select(EventVendor)
        .where(EventVendor.id == ev_id, EventVendor.event_id == event_id)
        .options(selectinload(EventVendor.vendor))
    )
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Event vendor not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(ev, field, value)
    await db.flush()
    await db.refresh(ev)

    result2 = await db.execute(
        select(EventVendor).where(EventVendor.id == ev.id).options(selectinload(EventVendor.vendor))
    )
    return EventVendorResponse.model_validate(result2.scalar_one())
