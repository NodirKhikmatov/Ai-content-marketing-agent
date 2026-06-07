"""Tests for startup analysis defaults."""

from workflows.analysis_defaults import STARTUP_ANALYSIS_OPTIONS, merge_analysis_options


def test_merge_analysis_options_applies_startup_defaults():
    opts = merge_analysis_options(None)
    assert opts["calendar_days"] == 7
    assert opts["sample_asset_count"] == 3
    assert opts["keyword_count"] == 10


def test_merge_analysis_options_request_overrides():
    opts = merge_analysis_options({"calendar_days": 30, "sample_asset_count": 0})
    assert opts["calendar_days"] == 30
    assert opts["sample_asset_count"] == 0
    assert opts["competitor_count"] == STARTUP_ANALYSIS_OPTIONS["competitor_count"]
