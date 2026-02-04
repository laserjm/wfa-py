from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class ConfluenceService:
    base_url: str
    email: str
    api_token: str

    def get_page_by_title(self, space_key: str, title: str) -> dict[str, Any] | None:
        url = f"{self.base_url}/rest/api/content"
        params = {
            "spaceKey": space_key,
            "title": title,
            "expand": "version,body.storage",
        }
        response = requests.get(url, params=params, auth=(self.email, self.api_token), timeout=30)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        return results[0] if results else None

    def get_page(self, page_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {"expand": "version,body.storage"}
        response = requests.get(url, params=params, auth=(self.email, self.api_token), timeout=30)
        response.raise_for_status()
        return response.json()

    def create_page(self, space_key: str, title: str, body_html: str) -> dict[str, Any]:
        url = f"{self.base_url}/rest/api/content"
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {"storage": {"value": body_html, "representation": "storage"}},
        }
        response = requests.post(url, json=payload, auth=(self.email, self.api_token), timeout=30)
        response.raise_for_status()
        return response.json()

    def update_page(self, page_id: str, title: str, body_html: str, current_version: int) -> dict[str, Any]:
        url = f"{self.base_url}/rest/api/content/{page_id}"
        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
            "version": {"number": current_version + 1},
            "body": {"storage": {"value": body_html, "representation": "storage"}},
        }
        response = requests.put(url, json=payload, auth=(self.email, self.api_token), timeout=30)
        response.raise_for_status()
        return response.json()

    def upsert_page(self, space_key: str, title: str, body_html: str, page_id: str | None = None) -> dict[str, Any]:
        if page_id:
            page = self.get_page(page_id)
            current_version = page.get("version", {}).get("number", 1)
            return self.update_page(page_id, title, body_html, current_version)

        existing = self.get_page_by_title(space_key, title)
        if existing:
            existing_id = existing.get("id")
            current_version = existing.get("version", {}).get("number", 1)
            return self.update_page(existing_id, title, body_html, current_version)
        return self.create_page(space_key, title, body_html)
