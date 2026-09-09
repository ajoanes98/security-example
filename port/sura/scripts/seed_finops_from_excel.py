#!/usr/bin/env python3
"""Seed finops_tag entities from u_tags_de_finops Excel into Port US.

Usage (requires PORT_CLIENT_ID and PORT_CLIENT_SECRET or a bearer token):
  python seed_finops_from_excel.py --file /path/to/u_tags_de_finops.xlsx

Normalization rules (per SURA AFP design):
- identifier prefix per dimension: op-centrocosto:cl08py0988
- ascii_downcase on identifier; original value kept in title
- underscores and hyphens treated as equivalent in identifier (canonical: hyphen)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Iterable

try:
    import openpyxl
except ImportError:
    print("Install openpyxl: pip install openpyxl", file=sys.stderr)
    sys.exit(1)

import requests

COLUMNS = {
    "op-ambiente": ["op-ambiente", "u_op_ambiente"],
    "op-centrocosto": ["op-centrocosto", "u_op_centrocosto"],
    "op-codigo-activo": ["op-codigo-activo", "u_op_codigo_activo"],
    "op-ecosistema": ["op-ecosistema", "u_op_ecosistema"],
    "op-lider": ["op-lider", "u_op_lider"],
    "op-proveedor": ["op-proveedor", "u_op_proveedor"],
    "op-proyecto": ["op-proyecto", "u_op_proyecto"],
    "op-responsable-negocio": ["op-responsable-negocio", "u_op_responsable_negocio"],
}

API_BASE = os.environ.get("PORT_API_URL", "https://api.us.port.io/v1")


def canonical_id(value: str) -> str:
    v = value.strip().lower()
    v = v.replace("_", "-")
    v = re.sub(r"-+", "-", v)
    return v


def get_token() -> str:
    client_id = os.environ.get("PORT_CLIENT_ID")
    client_secret = os.environ.get("PORT_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit("Set PORT_CLIENT_ID and PORT_CLIENT_SECRET")
    r = requests.post(
        f"{API_BASE}/auth/access_token",
        json={"clientId": client_id, "clientSecret": client_secret},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["accessToken"]


def upsert_tag(token: str, tag_key: str, tag_value: str) -> None:
    identifier = f"{tag_key}:{canonical_id(tag_value)}"
    payload = {
        "identifier": identifier,
        "title": tag_value.strip(),
        "properties": {
            "tag_key": tag_key,
            "tag_value": tag_value.strip(),
            "source": "servicenow",
        },
    }
    r = requests.post(
        f"{API_BASE}/blueprints/finops_tag/entities?upsert=true&merge=true",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    r.raise_for_status()


def iter_rows(path: str) -> Iterable[dict[str, str]]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    headers = [str(c.value).strip() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
    col_index = {h: i for i, h in enumerate(headers)}
    for row in ws.iter_rows(min_row=2, values_only=True):
        yield {h: (str(row[i]).strip() if row[i] is not None else "") for h, i in col_index.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to u_tags_de_finops.xlsx")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    token = None if args.dry_run else get_token()
    seen: set[tuple[str, str]] = set()
    count = 0

    for record in iter_rows(args.file):
        for tag_key, aliases in COLUMNS.items():
            value = ""
            for alias in aliases:
                if alias in record and record[alias]:
                    value = record[alias]
                    break
            if not value:
                continue
            key = (tag_key, canonical_id(value))
            if key in seen:
                continue
            seen.add(key)
            if args.dry_run:
                print(f"would upsert {tag_key}:{canonical_id(value)} -> {value}")
            else:
                upsert_tag(token, tag_key, value)
            count += 1

    print(f"Done. {count} finops_tag entities processed.")


if __name__ == "__main__":
    main()
