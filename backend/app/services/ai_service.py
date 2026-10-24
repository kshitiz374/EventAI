"""
AI Service Layer — all LLM interactions are centralized here.
Deterministic calculations NEVER delegate to the LLM.
"""
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from app.core.config import settings


def _get_client():
    """Lazily create the OpenAI client only when an API key is available."""
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            pass
    return None


def _extract_json(text: str) -> Optional[Dict]:
    """Extract the first JSON object from text, handling markdown code fences."""
    # Strip markdown fences
    text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "")
    # Try to find JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


SYSTEM_PROMPT = """You are Eventra AI, an expert event planning assistant.
You help users plan, organize, and manage events of all types.
You provide structured, actionable advice tailored to the user's budget, guest count, location, and preferences.
Always be specific, practical, and encouraging. Format lists clearly.
When a user describes their event, generate comprehensive but realistic plans.
Never fabricate vendor names, phone numbers, prices, or availability.
Clearly label all prices as "Estimates" not confirmed quotes.
"""


async def generate_event_plan(event_data: Dict) -> Dict:
    """Generate a structured event plan using the LLM."""
    client = _get_client()

    prompt = f"""
Create a comprehensive event plan for the following event:

Event: {event_data.get('name', 'Event')}
Type: {event_data.get('event_type', 'other')}
Date: {event_data.get('event_date', 'TBD')}
Location: {event_data.get('location', 'TBD')}
Guests: {event_data.get('guest_count', 0)}
Budget: {event_data.get('currency', 'INR')} {event_data.get('total_budget', 0)}
Theme: {event_data.get('theme', 'Not specified')}
Atmosphere: {event_data.get('atmosphere', 'Not specified')}
Dietary Requirements: {event_data.get('dietary_requirements', 'None')}
Special Requirements: {event_data.get('special_requirements', 'None')}

Return a JSON object with these keys:
- "summary": Brief 2-3 sentence overview
- "theme_recommendations": List of 3 theme ideas with descriptions
- "decoration_ideas": List of 5 decoration suggestions
- "catering_suggestions": List of menu suggestions appropriate for dietary requirements
- "key_considerations": List of 5 important things to plan first
- "risk_factors": List of potential risks and mitigation strategies
- "estimated_timeline_notes": Notes about when to do major tasks given the event date
- "ai_tips": 3 personalized AI tips for this specific event
"""

    if client:
        try:
            response = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return _fallback_event_plan(event_data, str(e))
    else:
        return _fallback_event_plan(event_data, "No AI API key configured")


def _fallback_event_plan(event_data: Dict, reason: str = "") -> Dict:
    """Return a high-quality template plan when AI is unavailable."""
    event_type = event_data.get("event_type", "other")
    budget = event_data.get("total_budget", 0)
    guests = event_data.get("guest_count", 0)
    theme = event_data.get("theme", "classic")
    currency = event_data.get("currency", "INR")

    themes_by_type = {
        "wedding": [
            {"name": "Royal Indian Wedding", "description": "Grand mandap, marigold flowers, royal blue and gold colors, classical music."},
            {"name": "Garden Elegance", "description": "Outdoor garden setting, white roses, fairy lights, romantic ambiance."},
            {"name": "Fusion Modern", "description": "Contemporary décor with traditional elements, minimal palette, chic setup."},
        ],
        "birthday": [
            {"name": "Cyberpunk Neon", "description": "Neon lights, dark backdrop, holographic elements, futuristic props."},
            {"name": "Retro Bollywood", "description": "Vintage film posters, golden hues, classic Bollywood music, photo booth."},
            {"name": "Tropical Fiesta", "description": "Bright colors, tropical plants, summer vibes, beach-style setup."},
        ],
        "hackathon": [
            {"name": "Silicon Valley Style", "description": "Minimalist white space, tech logos, standing desks, energetic playlist."},
            {"name": "Dark Mode Dev", "description": "Dark theme décor, glowing screens aesthetic, coding-inspired graphics."},
            {"name": "Innovation Hub", "description": "Open collaborative space, modular seating, whiteboards everywhere."},
        ],
        "corporate": [
            {"name": "Executive Elegance", "description": "Navy and silver palette, formal seating, professional AV setup."},
            {"name": "Innovation Summit", "description": "Modern tech feel, interactive displays, networking zones."},
            {"name": "Sustainability Focus", "description": "Eco-friendly materials, green décor, sustainable catering."},
        ],
    }

    return {
        "summary": f"A well-planned {event_type} for {guests} guests with a budget of {currency} {budget:,.0f}. "
                   f"Focus on securing the venue and catering first, as these typically consume 55-60% of the budget. "
                   f"With {'adequate' if budget / max(guests, 1) > 500 else 'tight'} per-person budget, "
                   f"prioritize quality in the most visible elements.",
        "theme_recommendations": themes_by_type.get(event_type, themes_by_type["birthday"]),
        "decoration_ideas": [
            "Floral centrepieces matching the chosen color palette",
            "Ambient LED lighting to set the atmosphere",
            "Photo backdrop / selfie wall with event name",
            "Welcome signage and directional banners",
            "Table runners and chair sashes in theme colors",
        ],
        "catering_suggestions": [
            "Welcome drinks station on arrival",
            "3-course seated meal (starter, main, dessert)",
            "Live food counters for interactive experience",
            "Dedicated vegetarian and special dietary sections",
            "Dessert table / cake cutting ceremony",
        ],
        "key_considerations": [
            "Book venue at least 60 days in advance for popular dates",
            "Confirm caterer capacity for your guest count",
            "Send invitations 3-4 weeks before the event",
            "Have a weather contingency plan for outdoor elements",
            "Appoint a day-of coordinator to manage logistics",
        ],
        "risk_factors": [
            {"risk": "Vendor cancellation", "mitigation": "Get signed contracts with penalty clauses; keep backup vendor list"},
            {"risk": "Guest count change", "mitigation": "Confirm final numbers 5 days before; negotiate flexible caterer terms"},
            {"risk": "Budget overrun", "mitigation": "Track spending weekly; maintain 3% emergency reserve"},
            {"risk": "Weather disruption", "mitigation": "Book a backup indoor space for outdoor elements"},
        ],
        "estimated_timeline_notes": "Begin planning immediately — secure high-demand vendors first. "
                                     "Send invitations 3 weeks before. Confirm all bookings 1 week before. "
                                     "Finalize details 2 days before the event.",
        "ai_tips": [
            f"For {guests} guests at {currency} {budget:,.0f}, allocate roughly {currency} {budget * 0.55 / max(guests, 1):,.0f} per person for food and venue combined.",
            f"A {theme or event_type} theme works best with a consistent color palette — choose 2-3 colors and stick to them throughout décor, invitations, and attire.",
            "Build a shared checklist in a spreadsheet or app and assign each task to a responsible person — distributed ownership prevents last-minute chaos.",
        ],
        "_ai_status": f"AI fallback mode: {reason}" if reason else "AI fallback mode",
    }


async def chat_with_copilot(
    message: str,
    history: List[Dict],
    event_context: Optional[Dict] = None,
) -> str:
    """Chat with the AI event copilot, passing event context."""
    client = _get_client()

    context_block = ""
    if event_context:
        context_block = f"""
CURRENT EVENT CONTEXT:
- Name: {event_context.get('name')}
- Type: {event_context.get('event_type')}
- Date: {event_context.get('event_date')}
- Location: {event_context.get('location')}
- Guests: {event_context.get('guest_count')}
- Budget: {event_context.get('currency')} {event_context.get('total_budget')}
- Theme: {event_context.get('theme')}
- Budget Utilization: {event_context.get('utilization_pct', 0):.1f}%
- Pending Tasks: {event_context.get('pending_tasks', 0)}
"""

    system = SYSTEM_PROMPT + context_block

    messages = [{"role": "system", "content": system}]
    for h in history[-10:]:  # last 10 messages for context
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    if client:
        try:
            response = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                temperature=0.8,
                max_tokens=1500,
            )
            return response.choices[0].message.content
        except Exception as e:
            return _fallback_chat(message, event_context, str(e))
    else:
        return _fallback_chat(message, event_context)


def _fallback_chat(message: str, event_context: Optional[Dict] = None, error: str = "") -> str:
    """Return helpful responses when AI is unavailable."""
    msg_lower = message.lower()

    prefix = ""
    if error:
        prefix = "*(AI service not configured — showing template response)*\n\n"

    if event_context:
        name = event_context.get("name", "your event")
        budget = event_context.get("total_budget", 0)
        currency = event_context.get("currency", "INR")
        guests = event_context.get("guest_count", 0)
    else:
        name, budget, currency, guests = "your event", 0, "INR", 0

    if any(w in msg_lower for w in ["budget", "cost", "money", "spend", "price"]):
        return prefix + f"""💰 **Budget Guidance for {name}**

With a budget of {currency} {budget:,.0f} for {guests} guests, here's a suggested allocation:

| Category | % | Estimate |
|---|---|---|
| Venue | 30% | {currency} {budget * 0.30:,.0f} |
| Catering | 25% | {currency} {budget * 0.25:,.0f} |
| Decoration | 15% | {currency} {budget * 0.15:,.0f} |
| Photography | 10% | {currency} {budget * 0.10:,.0f} |
| Entertainment | 8% | {currency} {budget * 0.08:,.0f} |
| Emergency Reserve | 3% | {currency} {budget * 0.03:,.0f} |

> These are **estimates** — actual market prices vary by location and season.

**Cost-saving tips:**
- Book vendors in off-peak times for 15-20% discounts
- Opt for a Sunday event instead of Saturday
- Use digital invitations to save on printing costs"""

    if any(w in msg_lower for w in ["task", "checklist", "todo", "schedule", "plan"]):
        return prefix + f"""📋 **Task Priorities for {name}**

**This Week (Urgent):**
1. ✅ Finalize and confirm venue booking
2. ✅ Shortlist and contact caterers
3. ✅ Send out invitations

**Next Week:**
4. 🔲 Confirm photographer / videographer
5. 🔲 Finalize decoration theme
6. 🔲 Follow up on guest RSVPs

**2 Weeks Before:**
7. 🔲 Final guest count to caterer
8. 🔲 Confirm all vendor contracts
9. 🔲 Prepare day-of schedule

**Day Before:**
10. 🔲 Final venue walkthrough
11. 🔲 Prepare payment envelopes for vendors
12. 🔲 Brief the team on their roles"""

    if any(w in msg_lower for w in ["theme", "decoration", "decor", "color"]):
        return prefix + f"""🎨 **Theme Ideas for {name}**

**Option 1: Royal Elegance**
Deep purple, gold, and ivory. Grand floral centrepieces, candlelit ambiance, vintage furniture.

**Option 2: Minimalist Modern**
White, beige, and sage green. Clean lines, simple florals, geometric shapes, premium materials.

**Option 3: Vibrant Festive**
Bright orange, pink, and yellow. Marigold strings, colorful drapes, folk art elements, joyful energy.

**Color Palette Tips:**
- Choose 2 primary + 1 accent color
- Keep table linens neutral; add color through florals and lighting
- Warm amber lighting flatters all themes"""

    if any(w in msg_lower for w in ["guest", "invite", "invitation", "rsvp"]):
        return prefix + f"""👥 **Guest Management for {guests} Guests**

**Invitation Timing:**
- Send 4-6 weeks before (formal events)
- Send 2-3 weeks before (casual events)
- RSVP deadline: 1 week before

**Invitation Message Template (WhatsApp):**
> 🎉 You're invited to *{name}*!
> 📅 Date: [Event Date]
> 📍 Venue: [Location]
> Please RSVP by [Date] to confirm your attendance.
> We can't wait to celebrate with you! 🙏

**Categories to track:** Family | Close Friends | Work Colleagues | VIP Guests"""

    # Default response
    return prefix + f"""I'm here to help you plan *{name}* perfectly! 🎉

Here's what I can help with:
- 💰 **Budget optimization** — "How should I allocate my budget?"
- 📋 **Task planning** — "What tasks should I do this week?"
- 🎨 **Theme ideas** — "Suggest 3 themes for my event"
- 👥 **Guest management** — "Draft an invitation message"
- 🏢 **Vendor tips** — "What should I ask a caterer?"
- ⚠️ **Risk planning** — "What could go wrong and how to prevent it?"

To unlock full AI capabilities, add your OpenAI API key to the backend `.env` file."""


async def generate_whatif_simulation(
    event_data: Dict,
    scenario_type: str,
    parameters: Dict,
) -> Dict:
    """Simulate what-if scenarios with deterministic impact calculations."""
    from app.services.budget_service import calculate_budget_allocations

    result = {
        "scenario_description": "",
        "financial_impact": 0.0,
        "affected_tasks": [],
        "budget_changes": {},
        "recommendations": [],
        "trade_offs": [],
    }

    current_budget = event_data.get("total_budget", 0)
    current_guests = event_data.get("guest_count", 0)
    event_type = event_data.get("event_type", "other")
    currency = event_data.get("currency", "INR")

    if scenario_type == "budget_change":
        new_budget = parameters.get("new_budget", current_budget)
        delta = new_budget - current_budget
        delta_pct = (delta / current_budget * 100) if current_budget else 0

        old_allocs = calculate_budget_allocations(current_budget, event_type)
        new_allocs = calculate_budget_allocations(new_budget, event_type)

        budget_changes = {}
        for old, new in zip(old_allocs, new_allocs):
            budget_changes[old["name"]] = round(new["allocated_amount"] - old["allocated_amount"], 2)

        result["scenario_description"] = f"Budget {'increased' if delta > 0 else 'decreased'} by {currency} {abs(delta):,.0f} ({abs(delta_pct):.1f}%)"
        result["financial_impact"] = delta
        result["budget_changes"] = budget_changes
        result["affected_tasks"] = ["Update vendor quotes", "Revise catering headcount", "Adjust decoration scope"]
        result["recommendations"] = [
            f"{'You can now upgrade' if delta > 0 else 'Consider scaling back'} venue and catering as priority",
            f"New per-person budget: {currency} {new_budget / max(current_guests, 1):,.0f}",
            "Re-negotiate quotes with vendors before finalizing contracts",
        ]
        result["trade_offs"] = [
            f"Venue allocation changes by {currency} {abs(budget_changes.get('Venue', 0)):,.0f}",
            f"Catering allocation changes by {currency} {abs(budget_changes.get('Catering', 0)):,.0f}",
        ]

    elif scenario_type == "guest_change":
        new_guests = parameters.get("new_guest_count", current_guests)
        delta_guests = new_guests - current_guests
        per_person_cost = current_budget / max(current_guests, 1)
        additional_cost = delta_guests * per_person_cost * 0.7  # catering + logistics, not full budget

        result["scenario_description"] = f"Guest count {'increased' if delta_guests > 0 else 'decreased'} by {abs(delta_guests)} people (total: {new_guests})"
        result["financial_impact"] = additional_cost
        result["affected_tasks"] = ["Update caterer headcount", "Revise seating arrangement", "Order additional place settings", "Update invitation list"]
        result["recommendations"] = [
            f"Expected additional cost: {currency} {abs(additional_cost):,.0f} (catering + logistics)",
            f"New catering estimate: {currency} {current_budget * 0.25 * (new_guests / max(current_guests, 1)):,.0f}",
            "Contact caterer immediately to confirm capacity",
        ]
        result["budget_changes"] = {
            "Catering": round(current_budget * 0.25 * (delta_guests / max(current_guests, 1)), 2),
            "Venue (seating)": round(current_budget * 0.05 * (delta_guests / max(current_guests, 1)), 2),
        }
        result["trade_offs"] = [
            f"Per-person budget changes from {currency} {per_person_cost:,.0f} to {currency} {current_budget / max(new_guests, 1):,.0f} (if budget stays same)",
            "Venue capacity must be verified for the new headcount",
        ]

    elif scenario_type == "date_change":
        new_date_str = parameters.get("new_date", "")
        season_impact = parameters.get("season", "peak")
        seasonal_multiplier = 1.15 if season_impact == "peak" else 0.90
        financial_impact = current_budget * (seasonal_multiplier - 1)

        result["scenario_description"] = f"Event date changed to {new_date_str} ({'peak' if season_impact == 'peak' else 'off-peak'} season)"
        result["financial_impact"] = financial_impact
        result["affected_tasks"] = ["Re-confirm venue availability", "Update vendor bookings", "Resend invitations", "Update task deadlines"]
        result["recommendations"] = [
            f"{'Peak season may add' if season_impact == 'peak' else 'Off-peak season can save'} ~{currency} {abs(financial_impact):,.0f} to total cost",
            "Contact all vendors immediately to check new date availability",
            "Send guests a date-change notice at least 3 weeks before new date",
        ]
        result["trade_offs"] = [
            "All timeline tasks need to be rescheduled relative to new date",
            "Some booked vendors may not be available on new date",
        ]

    return result


async def generate_theme_recommendations(event_data: Dict) -> Dict:
    """Generate creative theme and decoration recommendations."""
    client = _get_client()

    if client:
        prompt = f"""For a {event_data.get('event_type')} event called "{event_data.get('name')}" 
with theme "{event_data.get('theme', 'not specified')}" for {event_data.get('guest_count')} guests,
provide creative recommendations as JSON with keys:
- themes: list of 4 theme objects with name, description, color_palette (list), mood, key_elements (list)
- lighting_ideas: list of 5 suggestions
- dress_code: suggestion and description
- shopping_list: list of 10 decoration items to purchase
- venue_concepts: list of 3 venue setup concepts
- moodboard_prompt: a detailed DALL-E prompt for generating a moodboard image"""

        try:
            response = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.9,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            pass

    # Fallback
    return {
        "themes": [
            {"name": "Royal Elegance", "description": "Majestic gold and deep purple palette with grand floral arches", "color_palette": ["#7B2D8B", "#FFD700", "#FFFAF0"], "mood": "Opulent & Grand", "key_elements": ["Crystal chandeliers", "Draped fabric ceilings", "Centerpiece floral columns", "Gold-rimmed tableware"]},
            {"name": "Garden Romance", "description": "Lush greenery, soft pastels, and natural wood accents", "color_palette": ["#7EC8A4", "#F8C8D4", "#FAF7F0"], "mood": "Serene & Romantic", "key_elements": ["Floral archways", "Lanterns", "Wooden signage", "Wildflower centrepieces"]},
            {"name": "Minimalist Luxe", "description": "Clean white and beige with premium metallic accents", "color_palette": ["#FFFFFF", "#F5F0E8", "#C4A882"], "mood": "Sophisticated & Modern", "key_elements": ["Geometric terrariums", "Marble table tops", "Pampas grass", "Gold bar carts"]},
            {"name": "Vibrant Festival", "description": "Bold colors, layered fabrics, and joyful ethnic patterns", "color_palette": ["#FF6B35", "#F7C59F", "#EFEFD0"], "mood": "Energetic & Celebratory", "key_elements": ["Colorful drapes", "Rangoli", "Marigold strings", "Dhol and folk music"]},
        ],
        "lighting_ideas": [
            "Warm amber fairy lights for magical glow",
            "Uplighting in theme colors on walls and columns",
            "Candlelit table centerpieces for intimate warmth",
            "Neon sign with event name or couple's initials",
            "Spotlights on focal points like the stage or cake table",
        ],
        "dress_code": {"suggestion": "Smart Ethnic / Fusion Formals", "description": "Encourage guests to wear coordinated ethnic or semi-formal attire that complements the theme palette."},
        "shopping_list": [
            "Fairy lights (500 count string lights)",
            "Table centerpiece vases (one per table)",
            "Silk or satin table runners",
            "Chair sashes in theme color",
            "Balloon arch kit",
            "Themed backdrop banner",
            "Candles and tea light holders",
            "Fresh flowers for centrepieces",
            "Photo booth props set",
            "Welcome sign / chalkboard easel",
        ],
        "venue_concepts": [
            {"name": "Grand Entrance", "description": "Floral tunnel entrance, red carpet, name board, welcome staff"},
            {"name": "Intimate Garden Setup", "description": "Round tables under fairy light canopy, lush greenery walls, lantern pathways"},
            {"name": "Stage and Dining", "description": "Elevated stage for ceremonies, banquet seating, DJ corner"},
        ],
        "moodboard_prompt": f"Event moodboard for a {event_data.get('event_type', 'celebration')} with {event_data.get('theme', 'elegant')} theme. Elegant decor, coordinated color palette, floral arrangements, beautifully set tables, warm lighting, professional photography aesthetic.",
    }
