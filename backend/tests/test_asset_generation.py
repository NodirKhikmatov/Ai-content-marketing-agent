"""Asset generation routing tests."""

from workflows.asset_generation import _item_needs_caption, _item_needs_script


def test_linkedin_post_gets_caption_only():
    item = {"channel": "linkedin", "format": "post"}
    assert _item_needs_caption(item) is True
    assert _item_needs_script(item) is False


def test_youtube_video_gets_script_only():
    item = {"channel": "youtube", "format": "video"}
    assert _item_needs_caption(item) is False
    assert _item_needs_script(item) is True


def test_blog_article_gets_script_outline():
    item = {"channel": "blog", "format": "article"}
    assert _item_needs_caption(item) is False
    assert _item_needs_script(item) is True
