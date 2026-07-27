#!/usr/bin/env bash
# Apply Trigger Spacelift Stack (Option 2) resources to Port EU via REST API.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="${PORT_API_URL:-https://api.port.io/v1}"

if [[ -z "${PORT_CLIENT_ID:-}" || -z "${PORT_CLIENT_SECRET:-}" ]]; then
  echo "ERROR: Set PORT_CLIENT_ID and PORT_CLIENT_SECRET (Port EU Credentials)." >&2
  exit 1
fi

for cmd in curl jq; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

echo "==> Authenticating against ${API_URL}"
ACCESS_TOKEN="$(
  curl -sS -X POST "${API_URL}/auth/access_token" \
    -H 'Content-Type: application/json' \
    -d "$(jq -n --arg id "$PORT_CLIENT_ID" --arg secret "$PORT_CLIENT_SECRET" \
      '{clientId:$id, clientSecret:$secret}')" \
    | jq -er '.accessToken'
)"
AUTH_HEADER="Authorization: Bearer ${ACCESS_TOKEN}"

api_json() {
  local method="$1"
  local path="$2"
  local body_file="${3:-}"
  local tmp
  tmp="$(mktemp)"
  local http_code
  if [[ -n "$body_file" ]]; then
    http_code="$(
      curl -sS -o "$tmp" -w '%{http_code}' -X "$method" "${API_URL}${path}" \
        -H "$AUTH_HEADER" \
        -H 'Content-Type: application/json' \
        --data-binary @"$body_file"
    )"
  else
    http_code="$(
      curl -sS -o "$tmp" -w '%{http_code}' -X "$method" "${API_URL}${path}" \
        -H "$AUTH_HEADER" \
        -H 'Content-Type: application/json'
    )"
  fi
  cat "$tmp"
  echo
  rm -f "$tmp"
  [[ "$http_code" =~ ^2 ]]
}

echo "==> Upsert blueprint space_lift_stack"
if ! BP_RESP="$(api_json POST /blueprints "${SCRIPT_DIR}/blueprint.json")"; then
  echo "POST create failed or already exists; applying PUT (full replace of provided document — schema matches guide create)"
  BP_RESP="$(api_json PUT /blueprints/space_lift_stack "${SCRIPT_DIR}/blueprint.json")"
fi
echo "$BP_RESP" | jq '{ok, identifier: .blueprint.identifier, title: .blueprint.title}'
echo "$BP_RESP" | jq -e '.ok == true' >/dev/null

echo "==> Upsert mock entity mock-spacelift-stack"
ENT_RESP="$(
  curl -sS -X POST "${API_URL}/blueprints/space_lift_stack/entities?upsert=true&merge=true" \
    -H "$AUTH_HEADER" \
    -H 'Content-Type: application/json' \
    --data-binary @"${SCRIPT_DIR}/entity.mock.json"
)"
echo "$ENT_RESP" | jq '{ok, identifier: .entity.identifier, title: .entity.title}'
echo "$ENT_RESP" | jq -e '.ok == true' >/dev/null

upsert_action() {
  local file="$1"
  local identifier
  identifier="$(jq -er '.identifier' "$file")"
  local resp
  if ! resp="$(api_json POST /actions "$file")"; then
    resp="$(api_json PUT "/actions/${identifier}" "$file")"
  fi
  echo "$resp" | jq '{ok, identifier: .action.identifier, title: .action.title}'
  echo "$resp" | jq -e '.ok == true' >/dev/null
}

echo "==> Upsert action trigger_spacelift_stack"
upsert_action "${SCRIPT_DIR}/action.trigger.json"

echo "==> Upsert action refresh_spacelift_token"
upsert_action "${SCRIPT_DIR}/action.refresh.json"

echo "==> Upsert automation spacelift_token_refresh_sync"
upsert_action "${SCRIPT_DIR}/automation.token-refresh.json"

echo "==> Validate"
api_json GET /blueprints/space_lift_stack \
  | jq '{ok, identifier: .blueprint.identifier, properties: (.blueprint.schema.properties|keys)}'
curl -sS "${API_URL}/blueprints/space_lift_stack/entities" -H "$AUTH_HEADER" \
  | jq '{ok, entities: [.entities[]? | {identifier, title}]}'
api_json GET /actions/trigger_spacelift_stack | jq '{ok, identifier: .action.identifier}'
api_json GET /actions/refresh_spacelift_token | jq '{ok, identifier: .action.identifier}'
api_json GET /actions/spacelift_token_refresh_sync | jq '{ok, identifier: .action.identifier}'

echo
echo "Done. Seeded mock entity: mock-spacelift-stack ([MOCK] Demo Spacelift Stack)."
echo "Skipped: secrets, live Spacelift execute, webhook ingest."
echo "Do not run trigger_spacelift_stack until SPACELIFT_* secrets and a real GraphQL URL are configured."
