"""Robust JSON parsing for LLM responses."""

import json
import re
from typing import Any


def strip_json_fences(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return content.strip()


def _sanitize_json_text(text: str) -> str:
    """Best-effort cleanup for slightly invalid JSON from LLMs."""
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'")
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return text


def _close_json(text: str) -> str:
    """Close unclosed strings and brackets in truncated JSON."""
    in_string = False
    escape = False
    stack: list[str] = []

    for char in text:
        if escape:
            escape = False
            continue
        if char == "\\" and in_string:
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            stack.append("}")
        elif char == "[":
            stack.append("]")
        elif char in "}]" and stack and stack[-1] == char:
            stack.pop()

    result = text.rstrip()
    if result.endswith(","):
        result = result[:-1]
    if in_string:
        result += '"'
    result += "".join(reversed(stack))
    return result


def _parse_object(text: str) -> dict[str, Any]:
    parsed: Any = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("Expected JSON object from model")
    return parsed


def parse_json_content(content: str) -> dict[str, Any]:
    """Parse JSON from model output, tolerating trailing text or markdown."""
    text = strip_json_fences(content)
    if not text:
        raise ValueError("Empty JSON response from model")

    candidates: list[str] = [text, _sanitize_json_text(text)]

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        snippet = text[start : end + 1]
        sanitized = _sanitize_json_text(snippet)
        candidates.extend([snippet, sanitized, _close_json(sanitized)])

    candidates.append(_close_json(_sanitize_json_text(text)))

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            return _parse_object(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
            if "Extra data" in exc.msg:
                try:
                    parsed, _ = json.JSONDecoder().raw_decode(candidate)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError as inner_exc:
                    last_error = inner_exc
        except ValueError as exc:
            last_error = exc

    msg = last_error.msg if isinstance(last_error, json.JSONDecodeError) else str(last_error)
    raise ValueError(f"Invalid JSON from model: {msg}") from last_error
