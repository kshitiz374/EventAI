import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas import EventCreate, BudgetSummary


CATEGORIES_WITH_COLORS = [
    {"name": "Venue", "color": "#6366f1", "pct": 0.30},
    {"name": "Catering", "color": "#f59e0b", "pct": 0.25},
    {"name": "Decoration", "color": "#10b981", "pct": 0.15},
    {"name": "Photography", "color": "#3b82f6", "pct": 0.10},
    {"name": "Entertainment", "color": "#8b5cf6", "pct": 0.08},
    {"name": "Invitations", "color": "#ec4899", "pct": 0.04},
    {"name": "Miscellaneous", "color": "#6b7280", "pct": 0.05},
    {"name": "Emergency Reserve", "color": "#ef4444", "pct": 0.03},
]

EVENT_TYPE_WEIGHTS = {
    "wedding": {"Venue": 0.35, "Catering": 0.25, "Decoration": 0.15, "Photography": 0.10, "Entertainment": 0.05, "Invitations": 0.03, "Miscellaneous": 0.04, "Emergency Reserve": 0.03},
    "birthday": {"Venue": 0.25, "Catering": 0.30, "Decoration": 0.20, "Photography": 0.08, "Entertainment": 0.07, "Invitations": 0.03, "Miscellaneous": 0.04, "Emergency Reserve": 0.03},
    "hackathon": {"Venue": 0.40, "Catering": 0.30, "Decoration": 0.05, "Photography": 0.05, "Entertainment": 0.10, "Invitations": 0.02, "Miscellaneous": 0.05, "Emergency Reserve": 0.03},
    "corporate": {"Venue": 0.35, "Catering": 0.25, "Decoration": 0.10, "Photography": 0.08, "Entertainment": 0.10, "Invitations": 0.05, "Miscellaneous": 0.04, "Emergency Reserve": 0.03},
    "festival": {"Venue": 0.30, "Catering": 0.20, "Decoration": 0.20, "Photography": 0.08, "Entertainment": 0.12, "Invitations": 0.03, "Miscellaneous": 0.04, "Emergency Reserve": 0.03},
}


def calculate_budget_allocations(total_budget: float, event_type: str) -> List[Dict]:
    weights = EVENT_TYPE_WEIGHTS.get(event_type, {
        "Venue": 0.30, "Catering": 0.25, "Decoration": 0.15, "Photography": 0.10,
        "Entertainment": 0.08, "Invitations": 0.04, "Miscellaneous": 0.05, "Emergency Reserve": 0.03
    })
    colors = {c["name"]: c["color"] for c in CATEGORIES_WITH_COLORS}
    result = []
    for name, pct in weights.items():
        result.append({
            "name": name,
            "allocated_amount": round(total_budget * pct, 2),
            "color": colors.get(name, "#6b7280"),
        })
    return result


def compute_budget_summary(total_budget: float, categories: List[Dict]) -> Dict:
    total_allocated = sum(c.get("allocated_amount", 0) for c in categories)
    all_expenses = [e for c in categories for e in c.get("expenses", [])]
    total_estimated = sum(e.get("estimated_amount", 0) for e in all_expenses)
    total_actual = sum(e.get("actual_amount", 0) or e.get("estimated_amount", 0) for e in all_expenses)
    emergency_reserve = next(
        (c.get("allocated_amount", 0) for c in categories if "emergency" in c.get("name", "").lower()),
        round(total_budget * 0.03, 2)
    )
    remaining = total_budget - total_estimated
    utilization = (total_estimated / total_budget * 100) if total_budget > 0 else 0
    return {
        "total_budget": total_budget,
        "total_allocated": total_allocated,
        "total_estimated": total_estimated,
        "total_actual": total_actual,
        "remaining_budget": remaining,
        "emergency_reserve": emergency_reserve,
        "utilization_percentage": round(utilization, 1),
        "is_over_budget": total_estimated > total_budget,
    }


def generate_timeline_tasks(event_date: datetime, event_type: str, days_until: int) -> List[Dict]:
    now = datetime.now(timezone.utc)
    tasks = []

    milestones = {
        "wedding": [
            (0.9, "Book the venue", "critical"),
            (0.85, "Hire caterer", "critical"),
            (0.80, "Send invitations", "high"),
            (0.70, "Book photographer", "high"),
            (0.65, "Finalize decoration theme", "medium"),
            (0.50, "Confirm guest list & RSVPs", "high"),
            (0.40, "Order wedding cake", "medium"),
            (0.30, "Final menu tasting", "medium"),
            (0.20, "Confirm all vendor bookings", "high"),
            (0.10, "Prepare day-of checklist", "high"),
            (0.05, "Final guest count to caterer", "critical"),
            (0.01, "Set up venue", "critical"),
        ],
        "birthday": [
            (0.85, "Book venue or confirm location", "high"),
            (0.75, "Send invitations", "high"),
            (0.65, "Order birthday cake", "medium"),
            (0.50, "Plan catering/food menu", "medium"),
            (0.40, "Finalize decoration theme", "medium"),
            (0.30, "Confirm guest RSVPs", "high"),
            (0.20, "Purchase decorations", "medium"),
            (0.10, "Prepare entertainment plan", "medium"),
            (0.05, "Set up venue", "high"),
            (0.01, "Final checklist review", "critical"),
        ],
        "hackathon": [
            (0.90, "Secure venue / online platform", "critical"),
            (0.80, "Launch event registration", "critical"),
            (0.70, "Confirm sponsors and prizes", "high"),
            (0.60, "Set up communication channels", "high"),
            (0.50, "Arrange catering for participants", "medium"),
            (0.40, "Prepare judging criteria", "high"),
            (0.30, "Confirm judges and mentors", "high"),
            (0.20, "Send pre-event briefing", "medium"),
            (0.10, "Set up technical infrastructure", "high"),
            (0.01, "Final logistics check", "critical"),
        ],
        "corporate": [
            (0.90, "Confirm venue and AV setup", "critical"),
            (0.80, "Send official invitations", "high"),
            (0.70, "Arrange catering", "high"),
            (0.60, "Prepare agenda and presentations", "high"),
            (0.50, "Confirm speakers/panelists", "high"),
            (0.40, "Arrange accommodation if needed", "medium"),
            (0.30, "Prepare name badges and materials", "medium"),
            (0.15, "Rehearsal / dry run", "high"),
            (0.05, "Final headcount to caterer", "critical"),
            (0.01, "Set up registration desk", "high"),
        ],
    }

    template = milestones.get(event_type, milestones["birthday"])
    event_dt = event_date.replace(tzinfo=timezone.utc) if event_date.tzinfo is None else event_date

    for fraction, title, priority in template:
        days_before = max(1, int(days_until * fraction))
        due = event_dt - __import__("datetime").timedelta(days=days_before)
        tasks.append({
            "title": title,
            "priority": priority,
            "due_date": due.isoformat(),
            "status": "completed" if due < now else "pending",
        })

    return tasks
