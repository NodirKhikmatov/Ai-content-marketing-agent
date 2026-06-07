import asyncio
import logging
from typing import Any
from uuid import UUID

from agents.caption_writer import CaptionWriterAgent
from agents.script_writer import ScriptWriterAgent
from database.supabase import get_supabase

logger = logging.getLogger(__name__)

_VIDEO_CHANNELS = frozenset({"youtube", "tiktok", "instagram"})
_VIDEO_FORMATS = frozenset({"video", "reel", "story"})
_TEXT_FORMATS = frozenset({"post", "thread", "carousel"})


def _item_needs_caption(item: dict[str, Any]) -> bool:
    fmt = str(item.get("format", "")).lower()
    channel = str(item.get("channel", "")).lower()
    if fmt in _VIDEO_FORMATS:
        return False
    if fmt in _TEXT_FORMATS:
        return True
    return channel in {"linkedin", "twitter", "facebook"}


def _item_needs_script(item: dict[str, Any]) -> bool:
    fmt = str(item.get("format", "")).lower()
    channel = str(item.get("channel", "")).lower()
    if fmt in _TEXT_FORMATS and channel not in _VIDEO_CHANNELS:
        return False
    if fmt in _VIDEO_FORMATS or fmt == "article":
        return True
    return channel in _VIDEO_CHANNELS or channel == "blog"


class AssetGenerationWorkflow:
    """Generates captions, scripts, and other assets for content items."""

    def __init__(self):
        self.client = get_supabase().client
        self.caption_writer = CaptionWriterAgent()
        self.script_writer = ScriptWriterAgent()

    async def generate_for_items(
        self,
        project_id: UUID,
        content_items: list[dict[str, Any]],
        brand_tone: str,
        batch_size: int = 5,
        sample_limit: int = 0,
    ) -> None:
        targets = content_items
        if sample_limit > 0:
            targets = content_items[:sample_limit]
            logger.info(
                "Startup mode: generating sample assets for %s of %s items",
                len(targets),
                len(content_items),
            )

        for i in range(0, len(targets), batch_size):
            batch = targets[i : i + batch_size]
            await asyncio.gather(
                *[self._generate_for_item(project_id, item, brand_tone) for item in batch]
            )

    async def _generate_for_item(
        self, project_id: UUID, item: dict[str, Any], brand_tone: str
    ) -> None:
        context = {
            "content_item": item,
            "brand_tone": brand_tone,
            "instructions": item.get("instructions", ""),
        }
        assets: list[dict[str, Any]] = []
        caption_result = None
        script_result = None

        try:
            if _item_needs_caption(item):
                caption_result = await self.caption_writer.run(context)
                if caption_result.success:
                    data = caption_result.data
                    assets.append(
                        {
                            "project_id": str(project_id),
                            "content_item_id": item["id"],
                            "asset_type": "caption",
                            "platform": item.get("channel"),
                            "content": data.get("caption", ""),
                        }
                    )
                    if data.get("hashtags"):
                        assets.append(
                            {
                                "project_id": str(project_id),
                                "content_item_id": item["id"],
                                "asset_type": "hashtags",
                                "platform": item.get("channel"),
                                "content": " ".join(f"#{h}" for h in data["hashtags"]),
                            }
                        )

            if _item_needs_script(item):
                script_result = await self.script_writer.run(context)
                if script_result.success:
                    data = script_result.data
                    if data.get("script"):
                        assets.append(
                            {
                                "project_id": str(project_id),
                                "content_item_id": item["id"],
                                "asset_type": "script",
                                "platform": item.get("channel"),
                                "content": data["script"],
                            }
                        )
                    if data.get("blog_outline"):
                        import json

                        assets.append(
                            {
                                "project_id": str(project_id),
                                "content_item_id": item["id"],
                                "asset_type": "blog_outline",
                                "content": json.dumps(data["blog_outline"]),
                            }
                        )
                    if data.get("image_prompt"):
                        assets.append(
                            {
                                "project_id": str(project_id),
                                "content_item_id": item["id"],
                                "asset_type": "image_prompt",
                                "content": data["image_prompt"],
                            }
                        )

            if assets:
                self.client.table("generated_assets").insert(assets).execute()

            body = ""
            if caption_result and caption_result.success:
                body = caption_result.data.get("caption", "")
            elif script_result and script_result.success:
                body = script_result.data.get("script", "")

            update: dict[str, Any] = {"status": "ready"}
            if body:
                update["body"] = body
            self.client.table("content_items").update(update).eq("id", item["id"]).execute()

        except Exception as e:
            logger.warning("Asset generation failed for item %s: %s", item.get("id"), e)

    async def regenerate_item(
        self,
        project_id: UUID,
        content_item: dict[str, Any],
        brand_tone: str,
        asset_types: list[str] | None = None,
        instructions: str | None = None,
    ) -> list[dict[str, Any]]:
        self.client.table("content_items").update({"status": "generating"}).eq(
            "id", content_item["id"]
        ).execute()

        # Deactivate old assets
        self.client.table("generated_assets").update({"is_active": False}).eq(
            "content_item_id", content_item["id"]
        ).execute()

        item_context = {**content_item, "instructions": instructions or ""}
        await self._generate_for_item(project_id, item_context, brand_tone)

        result = (
            self.client.table("generated_assets")
            .select("*")
            .eq("content_item_id", content_item["id"])
            .eq("is_active", True)
            .execute()
        )
        return result.data or []
