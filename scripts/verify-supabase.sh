#!/usr/bin/env bash
# Verify Supabase schema after running migration 001_initial_schema.sql
set -euo pipefail

if [[ -z "${SUPABASE_URL:-}" || -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  echo "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or source backend/.env)"
  exit 1
fi

TABLES=(profiles projects websites competitors content_plans content_items seo_keywords generated_assets analysis_jobs)

echo "Checking Supabase tables..."
for table in "${TABLES[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" \
    "${SUPABASE_URL}/rest/v1/${table}?select=id&limit=1" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")
  if [[ "$status" == "200" ]]; then
    echo "  ✓ public.${table}"
  else
    echo "  ✗ public.${table} (HTTP ${status})"
    exit 1
  fi
done

echo ""
echo "All tables reachable. Schema verification passed."
