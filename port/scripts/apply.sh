#!/usr/bin/env bash
# Apply Crear Proyecto Port template: blueprint first, then workflows.
# Requires: curl, jq
# Env:
#   PORT_CLIENT_ID / PORT_CLIENT_SECRET  (Port API credentials)
#   PORT_API_URL  (default https://api.port.io — use https://api.us.port.io for US)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_URL="${PORT_API_URL:-https://api.port.io}"

if [[ -z "${PORT_CLIENT_ID:-}" || -z "${PORT_CLIENT_SECRET:-}" ]]; then
  echo "Set PORT_CLIENT_ID and PORT_CLIENT_SECRET before running." >&2
  exit 1
fi

echo "Authenticating against ${API_URL}..."
TOKEN="$(curl -sS -X POST "${API_URL}/v1/auth/access_token" \
  -H 'Content-Type: application/json' \
  -d "{\"clientId\":\"${PORT_CLIENT_ID}\",\"clientSecret\":\"${PORT_CLIENT_SECRET}\"}" \
  | jq -r '.accessToken')"

if [[ -z "${TOKEN}" || "${TOKEN}" == "null" ]]; then
  echo "Failed to obtain access token." >&2
  exit 1
fi

auth=(-H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json")

upsert_blueprint() {
  local file="$1"
  local id
  id="$(jq -r '.identifier' "${file}")"
  echo "Blueprint: ${id}"
  code="$(curl -sS -o /tmp/port_bp_resp.json -w '%{http_code}' \
    -X GET "${API_URL}/v1/blueprints/${id}" "${auth[@]}")" || true
  if [[ "${code}" == "200" ]]; then
    curl -sS -X PUT "${API_URL}/v1/blueprints/${id}" "${auth[@]}" --data @"${file}" | jq '{ok: .ok, identifier: .blueprint.identifier}'
  else
    curl -sS -X POST "${API_URL}/v1/blueprints" "${auth[@]}" --data @"${file}" | jq '{ok: .ok, identifier: .blueprint.identifier}'
  fi
}

upsert_workflow() {
  local file="$1"
  local id
  id="$(jq -r '.identifier' "${file}")"
  echo "Workflow: ${id}"
  code="$(curl -sS -o /tmp/port_wf_resp.json -w '%{http_code}' \
    -X GET "${API_URL}/v1/workflows/${id}" "${auth[@]}")" || true
  if [[ "${code}" == "200" ]]; then
    curl -sS -X PUT "${API_URL}/v1/workflows/${id}" "${auth[@]}" --data @"${file}" | jq '{identifier: .workflow.identifier // .identifier // "'"${id}"'"}'
  else
    curl -sS -X POST "${API_URL}/v1/workflows" "${auth[@]}" --data @"${file}" | jq '{identifier: .workflow.identifier // .identifier // "'"${id}"'"}'
  fi
}

echo "=== Blueprints ==="
for f in "${ROOT}/blueprints/"*.json; do
  upsert_blueprint "${f}"
done

echo "=== Workflows ==="
for f in "${ROOT}/workflows/"*.json; do
  upsert_workflow "${f}"
done

echo "Done. Replace REPLACE_*@example.com responders and example.com webhook URLs before go-live."
