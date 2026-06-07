#!/usr/bin/env bash
# Quick smoke test for the running API (requires valid Supabase JWT)
set -euo pipefail

API="${API_URL:-http://localhost:8000}"
TOKEN="${ACCESS_TOKEN:-}"

echo "=== Health (public) ==="
curl -s "${API}/health" | python3 -m json.tool

echo ""
echo "=== API health ==="
curl -s "${API}/api/v1/health" | python3 -m json.tool

if [[ -z "$TOKEN" ]]; then
  echo ""
  echo "Set ACCESS_TOKEN to a Supabase JWT to test authenticated routes."
  echo "  export ACCESS_TOKEN=\$(curl ... )  # or copy from browser devtools"
  exit 0
fi

echo ""
echo "=== Auth probe ==="
curl -s "${API}/api/v1/me" -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool

echo ""
echo "=== User profile ==="
curl -s "${API}/api/v1/users/me" -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool

echo ""
echo "=== List projects ==="
curl -s "${API}/api/v1/projects" -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
