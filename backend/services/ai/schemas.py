"""Pydantic schemas for structured AI agent outputs."""

from pydantic import BaseModel, Field, field_validator, model_validator


def _coerce_to_str(value: object) -> object:
    """LLMs sometimes return a list or dict where a string is expected."""
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item is not None)
    if isinstance(value, dict):
        parts: list[str] = []
        for key, item in value.items():
            if isinstance(item, list):
                parts.append(f"{key}: {', '.join(str(x) for x in item)}")
            elif isinstance(item, dict):
                parts.append(f"{key}: {_coerce_to_str(item)}")
            else:
                parts.append(f"{key}: {item}")
        return "; ".join(parts)
    return value


def _coerce_to_list(value: object) -> list[str]:
    """LLMs sometimes return a string where a list is expected."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _coerce_to_int(value: object, default: int = 0) -> int:
    if value is None or value == "":
        return default
    if isinstance(value, int):
        return value
    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return default


_VALID_KEYWORD_INTENTS = frozenset(
    {"informational", "commercial", "transactional", "navigational"}
)
_VALID_KEYWORD_PRIORITIES = frozenset({"low", "medium", "high"})
_VALID_CHANNELS = frozenset(
    {"blog", "linkedin", "instagram", "tiktok", "youtube", "twitter", "facebook"}
)
_VALID_FORMATS = frozenset(
    {"post", "article", "video", "reel", "story", "carousel", "thread"}
)


def _normalize_keyword_intent(value: object) -> str:
    text = str(_coerce_to_str(value) or "informational").strip().lower()
    if text in _VALID_KEYWORD_INTENTS:
        return text
    aliases = {
        "info": "informational",
        "information": "informational",
        "commercial intent": "commercial",
        "buy": "transactional",
        "purchase": "transactional",
        "transaction": "transactional",
        "nav": "navigational",
        "navigation": "navigational",
        "brand": "navigational",
    }
    if text in aliases:
        return aliases[text]
    for valid in _VALID_KEYWORD_INTENTS:
        if valid in text:
            return valid
    return "informational"


def _normalize_keyword_priority(value: object) -> str:
    text = str(_coerce_to_str(value) or "medium").strip().lower()
    if text in _VALID_KEYWORD_PRIORITIES:
        return text
    if "high" in text:
        return "high"
    if "low" in text:
        return "low"
    return "medium"


def _normalize_channel(value: object) -> str:
    text = str(_coerce_to_str(value) or "blog").strip().lower()
    text = text.replace("-", " ").replace("_", " ")
    if text in _VALID_CHANNELS:
        return text
    aliases = {
        "linked in": "linkedin",
        "x": "twitter",
        "x twitter": "twitter",
        "twitter/x": "twitter",
        "fb": "facebook",
        "ig": "instagram",
        "yt": "youtube",
        "website": "blog",
        "web": "blog",
    }
    if text in aliases:
        return aliases[text]
    compact = text.replace(" ", "")
    for valid in _VALID_CHANNELS:
        if valid in compact or valid in text:
            return valid
    return "blog"


def _normalize_format(value: object) -> str:
    text = str(_coerce_to_str(value) or "post").strip().lower()
    text = text.replace("-", " ").replace("_", " ")
    if text in _VALID_FORMATS:
        return text
    aliases = {
        "thought leadership article": "article",
        "long form article": "article",
        "longform article": "article",
        "blog post": "post",
        "social post": "post",
        "short video": "reel",
        "shorts": "reel",
        "short form video": "reel",
        "carousel post": "carousel",
    }
    if text in aliases:
        return aliases[text]
    for valid in _VALID_FORMATS:
        if valid in text:
            return valid
    return "post"


class WebsiteAnalysisSchema(BaseModel):
    business_type: str
    products_services: list[str] = Field(default_factory=list)
    target_audience: str
    unique_value_proposition: str
    brand_tone: str
    key_messages: list[str] = Field(default_factory=list)
    industry: str = ""

    @field_validator(
        "business_type",
        "target_audience",
        "unique_value_proposition",
        "brand_tone",
        "industry",
        mode="before",
    )
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("products_services", "key_messages", mode="before")
    @classmethod
    def coerce_string_lists(cls, value: object) -> object:
        return _coerce_to_list(value)


class CompetitorSchema(BaseModel):
    name: str
    url: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    content_gaps: list[str] = Field(default_factory=list)
    positioning_summary: str = ""
    social_presence: dict[str, str] = Field(default_factory=dict)

    @field_validator("name", "url", "positioning_summary", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("strengths", "weaknesses", "content_gaps", mode="before")
    @classmethod
    def coerce_list_fields(cls, value: object) -> object:
        return _coerce_to_list(value)

    @field_validator("social_presence", mode="before")
    @classmethod
    def coerce_social_presence(cls, value: object) -> object:
        if isinstance(value, dict):
            return {str(k): str(v) for k, v in value.items()}
        return {}


class CompetitorResearchSchema(BaseModel):
    competitors: list[CompetitorSchema]
    market_insights: str = ""

    @field_validator("market_insights", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)


class PersonaSchema(BaseModel):
    name: str
    role: str
    demographics: str = ""
    pain_points: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    content_preferences: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_persona(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        if not data.get("name"):
            data["name"] = (
                data.get("id")
                or data.get("title")
                or data.get("persona_name")
                or data.get("role")
                or "Audience persona"
            )
        if not data.get("role"):
            data["role"] = str(data.get("title") or data.get("job_title") or "Decision maker")
        return data

    @field_validator("name", "role", "demographics", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator(
        "pain_points", "goals", "content_preferences", "platforms", mode="before"
    )
    @classmethod
    def coerce_list_fields(cls, value: object) -> object:
        return _coerce_to_list(value)


class AudienceResearchSchema(BaseModel):
    personas: list[PersonaSchema]
    audience_summary: str = ""
    content_preferences: dict[str, object] = Field(default_factory=dict)

    @field_validator("audience_summary", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("content_preferences", mode="before")
    @classmethod
    def coerce_content_preferences(cls, value: object) -> object:
        return value if isinstance(value, dict) else {}


class KeywordSchema(BaseModel):
    keyword: str
    search_volume: int = 0
    difficulty: int = 0
    intent: str = "informational"
    cluster: str = ""
    priority: str = "medium"
    content_suggestions: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_keyword(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        if not data.get("keyword"):
            data["keyword"] = (
                data.get("term")
                or data.get("phrase")
                or data.get("key")
                or data.get("name")
                or "keyword"
            )
        return data

    @field_validator("keyword", "cluster", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("intent", mode="before")
    @classmethod
    def normalize_intent(cls, value: object) -> str:
        return _normalize_keyword_intent(value)

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, value: object) -> str:
        return _normalize_keyword_priority(value)

    @field_validator("search_volume", "difficulty", mode="before")
    @classmethod
    def coerce_int_fields(cls, value: object) -> object:
        coerced = _coerce_to_int(value)
        if coerced < 0:
            return 0
        return coerced

    @field_validator("difficulty", mode="after")
    @classmethod
    def clamp_difficulty(cls, value: int) -> int:
        return max(0, min(100, value))

    @field_validator("content_suggestions", mode="before")
    @classmethod
    def coerce_list_fields(cls, value: object) -> object:
        return _coerce_to_list(value)


class SEOStrategySchema(BaseModel):
    keywords: list[KeywordSchema]
    clusters: list[str] = Field(default_factory=list)
    strategy_summary: str = ""

    @model_validator(mode="before")
    @classmethod
    def normalize_strategy(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        if "keywords" not in data:
            for alt in ("keyword_list", "keyword_strategy", "target_keywords"):
                if alt in data:
                    data["keywords"] = data[alt]
                    break
        if isinstance(data.get("clusters"), dict):
            data["clusters"] = list(data["clusters"].keys())
        return data

    @field_validator("strategy_summary", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("clusters", mode="before")
    @classmethod
    def coerce_list_fields(cls, value: object) -> object:
        return _coerce_to_list(value)


class ContentItemPlanSchema(BaseModel):
    day: int
    title: str
    description: str = ""
    channel: str
    format: str
    pillar: str = ""
    keyword_targets: list[str] = Field(default_factory=list)
    hook_idea: str = ""

    @field_validator("title", "description", "pillar", "hook_idea", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("channel", mode="before")
    @classmethod
    def normalize_channel(cls, value: object) -> str:
        return _normalize_channel(value)

    @field_validator("format", mode="before")
    @classmethod
    def normalize_format(cls, value: object) -> str:
        return _normalize_format(value)

    @field_validator("day", mode="before")
    @classmethod
    def coerce_day(cls, value: object) -> object:
        return _coerce_to_int(value, default=1)

    @field_validator("keyword_targets", mode="before")
    @classmethod
    def coerce_list_fields(cls, value: object) -> object:
        return _coerce_to_list(value)


class ContentPlanSchema(BaseModel):
    plan_name: str = "30-Day Content Plan"
    pillars: list[str] = Field(default_factory=list)
    channel_mix: dict[str, int] = Field(default_factory=dict)
    content_items: list[ContentItemPlanSchema]

    @field_validator("plan_name", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("pillars", mode="before")
    @classmethod
    def coerce_list_fields(cls, value: object) -> object:
        return _coerce_to_list(value)

    @field_validator("channel_mix", mode="before")
    @classmethod
    def coerce_channel_mix(cls, value: object) -> object:
        if not isinstance(value, dict):
            return {}
        return {_normalize_channel(k): _coerce_to_int(v) for k, v in value.items()}


class CaptionSchema(BaseModel):
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    hook: str = ""
    cta: str = ""
    character_count: int = 0

    @field_validator("caption", "hook", "cta", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("hashtags", mode="before")
    @classmethod
    def coerce_list_fields(cls, value: object) -> object:
        return _coerce_to_list(value)

    @field_validator("character_count", mode="before")
    @classmethod
    def coerce_character_count(cls, value: object) -> object:
        return _coerce_to_int(value)


class ScriptSchema(BaseModel):
    script: str = ""
    blog_outline: dict[str, object] = Field(default_factory=dict)
    image_prompt: str = ""
    b_roll_suggestions: list[str] = Field(default_factory=list)

    @field_validator("script", "image_prompt", mode="before")
    @classmethod
    def coerce_text_fields(cls, value: object) -> object:
        return _coerce_to_str(value)

    @field_validator("b_roll_suggestions", mode="before")
    @classmethod
    def coerce_list_fields(cls, value: object) -> object:
        return _coerce_to_list(value)

    @field_validator("blog_outline", mode="before")
    @classmethod
    def coerce_blog_outline(cls, value: object) -> object:
        return value if isinstance(value, dict) else {}
