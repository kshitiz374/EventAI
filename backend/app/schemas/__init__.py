from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from app.models import EventType, EventStatus, TaskPriority, TaskStatus, GuestStatus, VendorCategory, VendorStatus, MessageRole


# ─── Event Schemas ────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    name: str
    event_type: EventType = EventType.OTHER
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    guest_count: int = 0
    total_budget: float = 0.0
    currency: str = "INR"
    theme: Optional[str] = None
    atmosphere: Optional[str] = None
    dietary_requirements: Optional[str] = None
    special_requirements: Optional[str] = None


class EventUpdate(BaseModel):
    name: Optional[str] = None
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    guest_count: Optional[int] = None
    total_budget: Optional[float] = None
    currency: Optional[str] = None
    theme: Optional[str] = None
    atmosphere: Optional[str] = None
    dietary_requirements: Optional[str] = None
    special_requirements: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    event_type: EventType
    status: EventStatus
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    guest_count: int
    total_budget: float
    currency: str
    theme: Optional[str] = None
    atmosphere: Optional[str] = None
    dietary_requirements: Optional[str] = None
    special_requirements: Optional[str] = None
    ai_plan: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Budget Schemas ───────────────────────────────────────────────────────────

class BudgetCategoryCreate(BaseModel):
    name: str
    allocated_amount: float = 0.0
    color: Optional[str] = None


class BudgetCategoryUpdate(BaseModel):
    name: Optional[str] = None
    allocated_amount: Optional[float] = None
    color: Optional[str] = None


class ExpenseCreate(BaseModel):
    description: str
    estimated_amount: float = 0.0
    actual_amount: Optional[float] = None
    is_paid: bool = False
    vendor_name: Optional[str] = None
    notes: Optional[str] = None


class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    estimated_amount: Optional[float] = None
    actual_amount: Optional[float] = None
    is_paid: Optional[bool] = None
    vendor_name: Optional[str] = None
    notes: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    category_id: int
    description: str
    estimated_amount: float
    actual_amount: Optional[float] = None
    is_paid: bool
    vendor_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BudgetCategoryResponse(BaseModel):
    id: int
    event_id: int
    name: str
    allocated_amount: float
    color: Optional[str] = None
    expenses: List[ExpenseResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class BudgetSummary(BaseModel):
    total_budget: float
    total_allocated: float
    total_estimated: float
    total_actual: float
    remaining_budget: float
    emergency_reserve: float
    utilization_percentage: float
    is_over_budget: bool
    categories: List[BudgetCategoryResponse]


class BudgetSimulationRequest(BaseModel):
    new_budget: Optional[float] = None
    new_guest_count: Optional[int] = None
    priority_categories: Optional[List[str]] = None
    notes: Optional[str] = None


# ─── Task Schemas ─────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    depends_on: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    depends_on: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    event_id: int
    title: str
    description: Optional[str] = None
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    depends_on: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Guest Schemas ────────────────────────────────────────────────────────────

class GuestCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    category: Optional[str] = None
    dietary_preference: Optional[str] = None
    notes: Optional[str] = None


class GuestUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    category: Optional[str] = None
    rsvp_status: Optional[GuestStatus] = None
    dietary_preference: Optional[str] = None
    invitation_sent: Optional[bool] = None
    notes: Optional[str] = None


class GuestResponse(BaseModel):
    id: int
    event_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    category: Optional[str] = None
    rsvp_status: GuestStatus
    dietary_preference: Optional[str] = None
    invitation_sent: bool
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Vendor Schemas ───────────────────────────────────────────────────────────

class VendorCreate(BaseModel):
    name: str
    category: VendorCategory = VendorCategory.OTHER
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[VendorCategory] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class VendorResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    category: VendorCategory
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EventVendorCreate(BaseModel):
    vendor_id: int
    quoted_price: Optional[float] = None
    notes: Optional[str] = None


class EventVendorUpdate(BaseModel):
    status: Optional[VendorStatus] = None
    quoted_price: Optional[float] = None
    final_price: Optional[float] = None
    notes: Optional[str] = None


class EventVendorResponse(BaseModel):
    id: int
    event_id: int
    vendor_id: int
    status: VendorStatus
    quoted_price: Optional[float] = None
    final_price: Optional[float] = None
    notes: Optional[str] = None
    vendor: VendorResponse
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── AI / Chat Schemas ────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    role: MessageRole = MessageRole.ASSISTANT
    tool_calls: Optional[List[Dict]] = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    event_id: Optional[int] = None
    title: Optional[str] = None
    messages: List[MessageResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class EventPlanRequest(BaseModel):
    natural_language_prompt: Optional[str] = None
    event_data: Optional[EventCreate] = None


class WhatIfSimulationRequest(BaseModel):
    scenario_type: str  # budget_change, guest_change, date_change, venue_change
    parameters: Dict[str, Any]


class WhatIfSimulationResponse(BaseModel):
    scenario_description: str
    financial_impact: float
    affected_tasks: List[str]
    budget_changes: Dict[str, float]
    recommendations: List[str]
    trade_offs: List[str]


class ChangeProposalResponse(BaseModel):
    id: int
    event_id: int
    title: str
    description: str
    proposed_changes: Dict
    financial_impact: Optional[float] = None
    is_applied: bool
    created_at: datetime

    model_config = {"from_attributes": True}
