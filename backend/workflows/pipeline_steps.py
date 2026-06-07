"""Analysis pipeline constants and helpers."""

PIPELINE_STEPS = [
    "website_analysis",
    "competitor_research",
    "audience_research",
    "seo_strategy",
    "content_planning",
    "asset_generation",
]

STEP_PROGRESS: dict[str, int] = {
    "website_analysis": 5,
    "competitor_research": 20,
    "audience_research": 40,
    "seo_strategy": 55,
    "content_planning": 70,
    "asset_generation": 85,
}

NEXT_STEP: dict[str, str | None] = {
    "website_analysis": "competitor_research",
    "competitor_research": "audience_research",
    "audience_research": "seo_strategy",
    "seo_strategy": "content_planning",
    "content_planning": "asset_generation",
    "asset_generation": None,
}

STEP_LABELS: dict[str, str] = {
    "website_analysis": "Analyzing website",
    "competitor_research": "Researching competitors",
    "audience_research": "Building audience personas",
    "seo_strategy": "Creating SEO strategy",
    "content_planning": "Planning content calendar",
    "asset_generation": "Generating content assets",
}
