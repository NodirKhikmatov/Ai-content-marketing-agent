"""Usage limits tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import NotFoundError, QuotaExceededError
from services.usage.service import UsageService


def _mock_client(*, rpc_data):
    client = MagicMock()
    client.rpc.return_value.execute.return_value = MagicMock(data=rpc_data)
    return client


@patch("services.usage.service.get_supabase")
def test_get_usage_returns_stats(mock_get_supabase):
    mock_get_supabase.return_value.client = _mock_client(
        rpc_data=[
            {
                "analyses_used": 0,
                "analyses_limit": 1,
                "regenerations_used": 3,
                "regenerations_limit": 10,
                "plan": "free",
            }
        ]
    )
    usage = UsageService().get_usage("user-1")
    assert usage.analyses_used == 0
    assert usage.regenerations_used == 3
    assert usage.plan == "free"


@patch("services.usage.service.get_supabase")
def test_get_usage_not_found(mock_get_supabase):
    mock_get_supabase.return_value.client = _mock_client(rpc_data=[])
    with pytest.raises(NotFoundError):
        UsageService().get_usage("missing")


@patch("services.usage.service.get_supabase")
def test_consume_analysis_allowed(mock_get_supabase):
    client = _mock_client(rpc_data=True)
    mock_get_supabase.return_value.client = client
    UsageService().consume_analysis("user-1")
    client.rpc.assert_called_with("try_consume_analysis", {"user_uuid": "user-1"})


@patch("services.usage.service.get_supabase")
def test_consume_analysis_quota_exceeded(mock_get_supabase):
    client = MagicMock()

    def rpc_side_effect(fn, params):
        result = MagicMock()
        if fn == "try_consume_analysis":
            result.execute.return_value = MagicMock(data=False)
        elif fn == "get_usage_stats":
            result.execute.return_value = MagicMock(
                data=[
                    {
                        "analyses_used": 1,
                        "analyses_limit": 1,
                        "regenerations_used": 0,
                        "regenerations_limit": 10,
                        "plan": "free",
                    }
                ]
            )
        return result

    client.rpc.side_effect = rpc_side_effect
    mock_get_supabase.return_value.client = client

    with pytest.raises(QuotaExceededError, match="Analysis limit"):
        UsageService().consume_analysis("user-1")


@patch("services.usage.service.get_supabase")
def test_consume_regeneration_quota_exceeded(mock_get_supabase):
    client = MagicMock()

    def rpc_side_effect(fn, params):
        result = MagicMock()
        if fn == "try_consume_regeneration":
            result.execute.return_value = MagicMock(data=False)
        elif fn == "get_usage_stats":
            result.execute.return_value = MagicMock(
                data=[
                    {
                        "analyses_used": 0,
                        "analyses_limit": 1,
                        "regenerations_used": 10,
                        "regenerations_limit": 10,
                        "plan": "free",
                    }
                ]
            )
        return result

    client.rpc.side_effect = rpc_side_effect
    mock_get_supabase.return_value.client = client

    with pytest.raises(QuotaExceededError, match="Regeneration limit"):
        UsageService().consume_regeneration("user-1")
