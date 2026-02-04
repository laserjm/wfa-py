from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from models.jira import JiraIssue


@dataclass
class JiraService:
    base_url: str
    email: str
    api_token: str

    def fetch_issue(self, key: str) -> JiraIssue:
        url = f"{self.base_url}/rest/api/3/issue/{key}"
        response = requests.get(url, auth=(self.email, self.api_token), timeout=30)
        response.raise_for_status()
        payload = response.json()
        fields = payload.get("fields", {})
        summary = fields.get("summary") or ""
        description = self._extract_description(fields.get("description"))
        return JiraIssue(key=payload.get("key", key), summary=summary, description=description, raw=payload)

    def _extract_description(self, description: Any) -> str:
        if description is None:
            return ""
        if isinstance(description, str):
            return description
        if isinstance(description, dict):
            return self._extract_text_from_adf(description)
        return str(description)

    def _extract_text_from_adf(self, node: Any) -> str:
        if node is None:
            return ""
        if isinstance(node, str):
            return node
        if isinstance(node, list):
            return "\n".join(self._extract_text_from_adf(item) for item in node if item)
        if isinstance(node, dict):
            node_type = node.get("type")
            if node_type == "text":
                return node.get("text", "")
            content = node.get("content")
            if content is None:
                return ""
            chunks = [self._extract_text_from_adf(child) for child in content]
            return "".join(chunk for chunk in chunks if chunk)
        return ""
