"""Default analysis options — tuned for startup cost/speed (override per request)."""

from typing import Any

# ~6–8 Claude calls per run vs ~65 for full 30-day + all assets.
STARTUP_ANALYSIS_OPTIONS: dict[str, Any] = {
    "calendar_days": 7,
    "competitor_count": 4,
    "keyword_count": 10,
    "generate_assets": True,
    "sample_asset_count": 3,
}

FULL_ANALYSIS_OPTIONS: dict[str, Any] = {
    "calendar_days": 30,
    "competitor_count": 8,
    "keyword_count": 25,
    "generate_assets": True,
    "sample_asset_count": 0,  # 0 = generate assets for every calendar item
}


def merge_analysis_options(options: dict[str, Any] | None) -> dict[str, Any]:
    """Apply startup defaults; explicit request options win."""
    merged = dict(STARTUP_ANALYSIS_OPTIONS)
    if options:
        merged.update({k: v for k, v in options.items() if v is not None})
    return merged
