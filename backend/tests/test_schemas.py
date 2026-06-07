"""Schema coercion tests for AI output normalization."""

from services.ai.schemas import ContentItemPlanSchema, ContentPlanSchema


def test_content_item_normalizes_channel_and_format():
    item = ContentItemPlanSchema.model_validate(
        {
            "day": 1,
            "title": "Why factories are moving beyond spreadsheets",
            "description": "",
            "channel": "LinkedIn",
            "format": "Thought Leadership Article",
        }
    )
    assert item.channel == "linkedin"
    assert item.format == "article"


def test_content_plan_normalizes_channel_mix_keys():
    plan = ContentPlanSchema.model_validate(
        {
            "content_items": [
                {
                    "day": 1,
                    "title": "Post one",
                    "channel": "Instagram",
                    "format": "Reel",
                }
            ],
            "channel_mix": {"LinkedIn": 3, "YouTube": 2},
        }
    )
    assert plan.channel_mix == {"linkedin": 3, "youtube": 2}
    assert plan.content_items[0].channel == "instagram"
    assert plan.content_items[0].format == "reel"
