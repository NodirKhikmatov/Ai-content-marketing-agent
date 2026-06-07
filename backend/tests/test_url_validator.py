"""URL validation tests."""

import pytest

from app.exceptions import ValidationError
from services.validation.url_validator import normalize_url, validate_website_url


def test_normalize_adds_https():
    assert normalize_url("example.com") == "https://example.com"


def test_normalize_preserves_https():
    assert normalize_url("https://Example.COM") == "https://example.com"


def test_rejects_localhost():
    with pytest.raises(ValidationError, match="not allowed"):
        validate_website_url("http://localhost:3000")


def test_rejects_empty():
    with pytest.raises(ValidationError):
        validate_website_url("")


def test_accepts_valid_url():
    assert validate_website_url("https://stripe.com") == "https://stripe.com"
