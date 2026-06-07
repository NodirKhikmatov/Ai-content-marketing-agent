"""Canned AI responses for offline/development mode (AI_MOCK_MODE=true).

Lets the full analysis pipeline run end-to-end without consuming any real
provider quota. Every payload is shaped to validate against the matching
schema in services/ai/schemas.py.
"""

from typing import Any

from services.ai.models import AITask


def _website_analysis() -> dict[str, Any]:
    return {
        "business_type": "B2B SaaS — manufacturing ERP",
        "products_services": [
            "Cloud ERP platform",
            "Production planning module",
            "Inventory and warehouse management",
        ],
        "target_audience": "Operations and IT leaders at mid-size manufacturers",
        "unique_value_proposition": (
            "An affordable, modern ERP tailored to regional manufacturers with "
            "fast onboarding and local-language support."
        ),
        "brand_tone": "professional, pragmatic, confident",
        "key_messages": [
            "Cut production downtime",
            "Real-time shop-floor visibility",
            "Implement in weeks, not years",
        ],
        "industry": "Manufacturing software",
    }


def _competitor_research() -> dict[str, Any]:
    def comp(name: str, url: str) -> dict[str, Any]:
        return {
            "name": name,
            "url": url,
            "strengths": ["Established brand", "Broad feature set"],
            "weaknesses": ["Expensive", "Slow implementation"],
            "content_gaps": ["Localized how-to guides", "ROI calculators"],
            "positioning_summary": f"{name} targets large enterprises.",
            "social_presence": {"linkedin": "active", "youtube": "moderate"},
        }

    return {
        "competitors": [
            comp("SAP Business One", "https://www.sap.com"),
            comp("Odoo", "https://www.odoo.com"),
            comp("Katana MRP", "https://katanamrp.com"),
        ],
        "market_insights": (
            "Incumbents over-serve enterprises and underserve mid-market "
            "manufacturers seeking quick deployment and local support."
        ),
    }


def _audience_research() -> dict[str, Any]:
    return {
        "personas": [
            {
                "name": "Operations Director Olim",
                "role": "Director of Operations",
                "demographics": "45-60, manufacturing management, regional",
                "pain_points": ["Unplanned downtime", "Manual planning"],
                "goals": ["Increase throughput", "Reduce waste"],
                "content_preferences": ["Case studies", "Webinars"],
                "platforms": ["LinkedIn", "Industry forums"],
            },
            {
                "name": "Plant Manager Pavel",
                "role": "Plant Manager",
                "demographics": "35-50, shop-floor operations",
                "pain_points": ["No real-time visibility", "Inventory errors"],
                "goals": ["On-time delivery", "Lower carrying cost"],
                "content_preferences": ["How-to videos", "Checklists"],
                "platforms": ["YouTube", "LinkedIn"],
            },
            {
                "name": "IT Lead Iroda",
                "role": "IT Administrator",
                "demographics": "28-42, IT administration",
                "pain_points": ["Integration overhead", "Security"],
                "goals": ["Reliable uptime", "Easy integrations"],
                "content_preferences": ["Docs", "API tutorials"],
                "platforms": ["GitHub", "LinkedIn"],
            },
        ],
        "audience_summary": (
            "Decision-makers value fast time-to-value, local support, and "
            "measurable operational gains over breadth of features."
        ),
        "content_preferences": {
            "formats": ["case_study", "video", "guide"],
            "cadence": "3-4 posts per week",
        },
    }


def _seo_strategy() -> dict[str, Any]:
    def kw(keyword: str, intent: str, priority: str, cluster: str) -> dict[str, Any]:
        return {
            "keyword": keyword,
            "search_volume": 480,
            "difficulty": 32,
            "intent": intent,
            "cluster": cluster,
            "priority": priority,
            "content_suggestions": [f"Guide: {keyword}"],
        }

    return {
        "keywords": [
            kw("manufacturing erp software", "commercial", "high", "ERP buying"),
            kw("what is mrp", "informational", "medium", "Education"),
            kw("best erp for small manufacturers", "commercial", "high", "ERP buying"),
            kw("erp implementation checklist", "informational", "medium", "Education"),
            kw("odoo vs sap business one", "commercial", "medium", "Comparisons"),
            kw("buy manufacturing erp", "transactional", "high", "Conversion"),
        ],
        "clusters": ["ERP buying", "Education", "Comparisons", "Conversion"],
        "strategy_summary": (
            "Target high-intent commercial terms while building topical "
            "authority with educational content around MRP/ERP basics."
        ),
    }


def _content_planning() -> dict[str, Any]:
    channels = [
        ("linkedin", "post"),
        ("youtube", "video"),
        ("instagram", "reel"),
        ("blog", "article"),
        ("linkedin", "carousel"),
    ]
    items = []
    for i, (channel, fmt) in enumerate(channels, start=1):
        items.append(
            {
                "day": i,
                "title": f"Content idea #{i}: cut downtime with real-time ERP",
                "description": "Educational piece tied to a core buyer pain point.",
                "channel": channel,
                "format": fmt,
                "pillar": "Operational efficiency",
                "keyword_targets": ["manufacturing erp software"],
                "hook_idea": "What if you could see every machine in real time?",
            }
        )
    return {
        "plan_name": "30-Day Content Plan (mock)",
        "pillars": [
            "Operational efficiency",
            "Cost reduction",
            "Digital transformation",
        ],
        "channel_mix": {"linkedin": 2, "youtube": 1, "instagram": 1, "blog": 1},
        "content_items": items,
    }


def _caption_writing() -> dict[str, Any]:
    return {
        "caption": (
            "Downtime is the silent profit killer on every shop floor. "
            "Here's how real-time ERP visibility changes the game."
        ),
        "hashtags": ["#manufacturing", "#ERP", "#operations"],
        "hook": "What if you could see every machine in real time?",
        "cta": "See how it works — link in comments.",
        "character_count": 142,
    }


def _script_writing() -> dict[str, Any]:
    return {
        "script": (
            "INTRO: Meet the plant manager fighting daily downtime...\n"
            "BODY: Show real-time dashboards, alerts, and planning.\n"
            "CTA: Book a 15-minute walkthrough."
        ),
        "blog_outline": {
            "h1": "Cut downtime with real-time ERP",
            "sections": ["The cost of downtime", "What visibility unlocks", "Next steps"],
        },
        "image_prompt": (
            "Modern factory floor with a tablet showing a real-time ERP "
            "dashboard, clean lighting, professional photography."
        ),
        "b_roll_suggestions": ["Machine close-ups", "Dashboard screen recording"],
    }


_MOCKS = {
    AITask.WEBSITE_ANALYSIS: _website_analysis,
    AITask.COMPETITOR_RESEARCH: _competitor_research,
    AITask.AUDIENCE_RESEARCH: _audience_research,
    AITask.SEO_STRATEGY: _seo_strategy,
    AITask.CONTENT_PLANNING: _content_planning,
    AITask.CAPTION_WRITING: _caption_writing,
    AITask.SCRIPT_WRITING: _script_writing,
}


def get_mock_response(task: AITask) -> dict[str, Any]:
    """Return a deep-ish copy of canned data for the given task."""
    factory = _MOCKS.get(task)
    if factory is None:
        return {}
    return factory()


def get_mock_text(task: AITask) -> str:
    """Plain-text mock for complete_text callers."""
    data = get_mock_response(task)
    return data.get("script") or data.get("caption") or "Mock AI response."
