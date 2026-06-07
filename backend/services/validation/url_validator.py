"""URL validation and normalization for website submission."""

import ipaddress
import re
from urllib.parse import urlparse

from app.exceptions import ValidationError

BLOCKED_HOSTS = frozenset({"localhost", "0.0.0.0"})


def normalize_url(raw: str) -> str:
    """Normalize user input to a canonical https URL."""
    value = raw.strip()
    if not value:
        raise ValidationError("URL is required")

    if not re.match(r"^https?://", value, re.IGNORECASE):
        value = f"https://{value}"

    parsed = urlparse(value)

    if parsed.scheme not in ("http", "https"):
        raise ValidationError("URL must use http or https")

    if not parsed.netloc:
        raise ValidationError("Invalid URL — missing domain")

    hostname = parsed.hostname
    if not hostname:
        raise ValidationError("Invalid URL — missing hostname")

    host_lower = hostname.lower()
    if host_lower in BLOCKED_HOSTS:
        raise ValidationError("This URL is not allowed")

    # Block private/reserved IPs (SSRF prevention)
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ValidationError("Private or internal URLs are not allowed")
    except ValueError:
        pass  # Not an IP — domain name is fine

    # Rebuild clean URL (no path manipulation for submission — homepage only)
    port = parsed.port
    netloc = hostname.lower()
    if port and port not in (80, 443):
        netloc = f"{netloc}:{port}"

    return f"{parsed.scheme.lower()}://{netloc}"


def validate_website_url(raw: str) -> str:
    """Validate and return normalized URL."""
    normalized = normalize_url(raw)

    if len(normalized) > 2048:
        raise ValidationError("URL is too long")

    return normalized
