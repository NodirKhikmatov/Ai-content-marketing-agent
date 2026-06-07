"""User-facing AI error formatting."""

import re

from services.ai.gemini_client import GeminiAPIError


def is_recoverable_provider_error(exc: BaseException) -> bool:
    """True when another configured provider may succeed (quota/rate limits)."""
    message = _unwrap_error_message(exc).lower()

    # Short Gemini RPM windows should retry on Gemini first, not jump providers.
    if "please retry in" in message:
        return False

    if isinstance(exc, GeminiAPIError) and exc.status_code in (429, 503):
        return True

    markers = (
        "quota",
        "rate limit",
        "too many requests",
        "resource exhausted",
        "resource has been exhausted",
        "insufficient_quota",
        "credit balance is too low",
        "exceeded your current quota",
    )
    return any(marker in message for marker in markers)


def _unwrap_error_message(exc: BaseException) -> str:
    message = str(exc)
    if "RetryError" in type(exc).__name__:
        inner = getattr(exc, "last_attempt", None)
        if inner is not None:
            try:
                inner_exc = inner.exception()
                if inner_exc is not None:
                    message = str(inner_exc)
            except Exception:
                pass
    return message


def should_skip_gemini_fallback(errors: list[BaseException]) -> bool:
    """Skip Gemini when paid providers are out of credits — free tier won't recover."""
    if not errors:
        return False
    combined = " ".join(_unwrap_error_message(e).lower() for e in errors)
    anthropic_exhausted = "credit balance is too low" in combined
    openai_exhausted = "insufficient_quota" in combined or (
        "exceeded your current quota" in combined and "google" not in combined
    )
    return anthropic_exhausted and openai_exhausted


def format_all_providers_failed(errors: list[BaseException]) -> str:
    """Summarize when every provider in the fallback chain failed."""
    if not errors:
        return "No AI provider configured"

    messages: list[str] = []
    seen: set[str] = set()
    for exc in errors:
        msg = format_ai_error(exc)
        if msg not in seen:
            seen.add(msg)
            messages.append(msg)

    if len(messages) == 1:
        return messages[0]

    summary = "; ".join(messages)
    return (
        f"All AI providers unavailable. {summary} "
        "For local UI testing without API credits, set AI_MOCK_MODE=true in backend/.env."
    )


def format_ai_error(exc: BaseException) -> str:
    """Turn provider/tenacity errors into a short message for the UI."""
    message = _unwrap_error_message(exc)

    lowered = message.lower()
    if "please retry in" in lowered:
        return (
            "Gemini free-tier rate limit reached (about 20 requests/min). "
            "Wait one minute and retry the analysis."
        )
    if "credit balance is too low" in lowered:
        return (
            "Anthropic API credits are exhausted. Add billing credits at console.anthropic.com, "
            "then retry the analysis."
        )
    if "exceeded your current quota" in lowered or "insufficient_quota" in lowered:
        if "google" in lowered or "gemini" in lowered or "resource exhausted" in lowered:
            return (
                "Gemini API quota is exhausted. Wait a few minutes or check usage at "
                "aistudio.google.com, then retry."
            )
        return (
            "OpenAI API quota is exhausted. Add billing credits at platform.openai.com, "
            "then retry the analysis."
        )
    if "resource exhausted" in lowered or "resource has been exhausted" in lowered:
        return (
            "Gemini API quota is exhausted. Wait a few minutes or check usage at "
            "aistudio.google.com, then retry."
        )
    if "invalid x-api-key" in lowered or "authentication" in lowered:
        return "AI API key is invalid. Check OPENAI_API_KEY and ANTHROPIC_API_KEY in backend/.env."

    # Trim noisy provider prefixes
    message = re.sub(r"^Error code: \d+\s*-\s*", "", message)
    if len(message) > 280:
        message = message[:277] + "..."
    return message
