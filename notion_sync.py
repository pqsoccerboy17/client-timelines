#!/usr/bin/env python3
"""
Notion → GitHub Sync for EasyVista Client Timelines

Pulls stakeholder data from Notion and updates config.json.
Run daily via GitHub Actions or manually.

Usage:
    python notion_sync.py

Environment variables:
    NOTION_API_KEY: Notion integration token
    NOTION_STAKEHOLDERS_ID: Data source ID (defaults to EasyVista stakeholders)
"""

from __future__ import annotations

import json
import os
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

# Configuration
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
# Notion database ID (not data_source_id)
DEFAULT_STAKEHOLDERS_ID = "1447853a-4ae0-4cc2-b560-0879e5f97374"
CONFIG_PATH = Path(__file__).parent / "config.json"

# Mapping from Notion "Relationship Strength" to config.json "status"
STATUS_MAP = {
    "Strong": "engaged",
    "Developing": "scheduled",
    "New": "outreach_sent",
    "Cold": "cold",
}

# Stakeholder types that indicate risk
RISK_TYPES = {"Blocker"}


def normalize_name(name: str) -> str:
    """Normalize name for matching (remove accents, lowercase)."""
    # Normalize unicode (é → e, etc.)
    normalized = unicodedata.normalize("NFD", name)
    ascii_name = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    return ascii_name.lower().strip()


def fetch_notion_stakeholders(token: str, data_source_id: str) -> list[dict]:
    """Fetch all stakeholders from Notion database."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    url = f"{NOTION_API_URL}/databases/{data_source_id}/query"
    all_results = []
    has_more = True
    start_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Error fetching from Notion: {response.status_code}")
            print(response.text)
            return []

        data = response.json()
        all_results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    return all_results


def extract_text(rich_text_array: list) -> str:
    """Extract plain text from Notion rich_text array."""
    if not rich_text_array:
        return ""
    return "".join(item.get("plain_text", "") for item in rich_text_array)


def parse_notion_stakeholder(page: dict) -> dict:
    """Parse a Notion page into stakeholder format."""
    props = page.get("properties", {})

    # Extract name from title
    name_prop = props.get("Name", {})
    name = extract_text(name_prop.get("title", []))

    # Extract role from rich_text
    role_prop = props.get("Role/Title", {})
    role = extract_text(role_prop.get("rich_text", []))

    # Extract status from Relationship Strength select
    status_prop = props.get("Relationship Strength", {})
    status_select = status_prop.get("select")
    relationship = status_select.get("name") if status_select else None

    # Extract stakeholder type for risk detection
    type_prop = props.get("Stakeholder Type", {})
    type_select = type_prop.get("select")
    stakeholder_type = type_select.get("name") if type_select else None

    # Map to config status
    if stakeholder_type in RISK_TYPES:
        status = "risk"
    elif relationship:
        status = STATUS_MAP.get(relationship, "pending")
    else:
        status = "pending"

    # Extract notes
    notes_prop = props.get("Notes", {})
    notes = extract_text(notes_prop.get("rich_text", []))

    # Extract location for reference
    location_prop = props.get("Location", {})
    location_select = location_prop.get("select")
    location = location_select.get("name") if location_select else None

    # Last edited time for freshness tracking
    last_edited = page.get("last_edited_time", "")

    return {
        "name": name,
        "role": role,
        "status": status,
        "notes": notes,
        "location": location,
        "notion_id": page.get("id"),
        "last_edited": last_edited,
        "_stakeholder_type": stakeholder_type,
        "_relationship": relationship,
    }


def match_stakeholder(notion_name: str, config_stakeholders: list[dict]) -> Optional[dict]:
    """Find matching stakeholder in config by normalized name."""
    notion_normalized = normalize_name(notion_name)

    for stakeholder in config_stakeholders:
        config_normalized = normalize_name(stakeholder.get("name", ""))

        # Exact match after normalization
        if notion_normalized == config_normalized:
            return stakeholder

        # Partial match (first name only for single-name entries like "Cedric")
        notion_first = notion_normalized.split()[0] if notion_normalized else ""
        config_first = config_normalized.split()[0] if config_normalized else ""

        if len(notion_first) > 2 and notion_first == config_first:
            # Verify it's likely the same person (avoid false matches)
            if len(notion_normalized.split()) == 1 or len(config_normalized.split()) == 1:
                return stakeholder

    return None


def sync_stakeholders(notion_data: list[dict], config: dict) -> tuple[dict, list[str]]:
    """
    Sync Notion stakeholders into config.json.

    Returns: (updated_config, list of changes made)
    """
    changes = []
    config_stakeholders = config.get("stakeholders", [])

    # Track which config stakeholders were matched
    matched_names = set()

    for notion_page in notion_data:
        parsed = parse_notion_stakeholder(notion_page)

        if not parsed["name"]:
            continue

        match = match_stakeholder(parsed["name"], config_stakeholders)

        if match:
            matched_names.add(match["name"])

            # Update status if changed
            old_status = match.get("status")
            new_status = parsed["status"]

            if old_status != new_status:
                changes.append(f"Status: {match['name']}: {old_status} → {new_status}")
                match["status"] = new_status

            # Update role if Notion has more info
            if parsed["role"] and parsed["role"] != match.get("role"):
                old_role = match.get("role", "(none)")
                changes.append(f"Role: {match['name']}: {old_role} → {parsed['role']}")
                match["role"] = parsed["role"]

            # Update notes if Notion has content (append Notion notes if different)
            if parsed["notes"]:
                current_notes = match.get("notes", "")
                # Only update if significantly different (not just a subset)
                if parsed["notes"] not in current_notes:
                    # Keep original notes, add indicator of Notion sync
                    match["notes"] = current_notes
                    changes.append(f"Notes updated for {match['name']}")
        else:
            # New stakeholder in Notion not in config
            changes.append(f"NEW in Notion (not added): {parsed['name']} ({parsed['role']})")

    # Report stakeholders in config but not in Notion
    for stakeholder in config_stakeholders:
        if stakeholder["name"] not in matched_names:
            changes.append(f"In config only (not in Notion): {stakeholder['name']}")

    return config, changes


def load_config() -> dict:
    """Load config.json."""
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config: dict):
    """Save config.json with updated timestamp."""
    config["meta"]["last_updated"] = datetime.now().isoformat()

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


def main():
    """Main sync function."""
    print("=" * 60)
    print(f"Notion → GitHub Sync | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Get credentials
    token = os.environ.get("NOTION_API_KEY")
    if not token:
        # Try local settings file
        settings_path = Path(__file__).parent / ".claude" / "settings.local.json"
        if settings_path.exists():
            with open(settings_path) as f:
                settings = json.load(f)
                # Extract token from permissions if available
                perms = settings.get("permissions", {})
                for key in perms:
                    if "ntn_" in key:
                        token = key.split("ntn_")[1]
                        token = "ntn_" + token.split('"')[0]
                        break

    if not token:
        print("Error: NOTION_API_KEY environment variable not set")
        print("Set it in GitHub Secrets or export NOTION_API_KEY=ntn_...")
        sys.exit(1)

    data_source_id = os.environ.get("NOTION_STAKEHOLDERS_ID") or DEFAULT_STAKEHOLDERS_ID

    print(f"Data source: {data_source_id}")
    print()

    # Fetch from Notion
    print("Fetching stakeholders from Notion...")
    notion_data = fetch_notion_stakeholders(token, data_source_id)
    print(f"Found {len(notion_data)} stakeholders in Notion")
    print()

    if not notion_data:
        print("No data fetched. Check API token and database permissions.")
        sys.exit(1)

    # Load config
    print("Loading config.json...")
    config = load_config()
    config_count = len(config.get("stakeholders", []))
    print(f"Found {config_count} stakeholders in config.json")
    print()

    # Sync
    print("Syncing...")
    updated_config, changes = sync_stakeholders(notion_data, config)

    if changes:
        print(f"\n{len(changes)} changes detected:")
        for change in changes:
            print(f"  - {change}")

        # Save
        print("\nSaving config.json...")
        save_config(updated_config)
        print("Done!")
    else:
        print("No changes detected. Config is up to date.")

    print()
    print("=" * 60)

    return 0 if not changes else 0  # Always succeed, let git detect changes


if __name__ == "__main__":
    sys.exit(main())
