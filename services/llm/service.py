from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests


@dataclass
class LlmService:
    api_url: str
    api_key: str
    model: str

    def summarize_jira(self, jira_payload: dict[str, Any], system_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._build_user_message(jira_payload)},
            ],
        }
        response = requests.post(self.api_url, headers=headers, json=body, timeout=60)
        response.raise_for_status()
        data = response.json()
        return self._extract_content(data)

    def _build_user_message(self, jira_payload: dict[str, Any]) -> str:
        return (
            "Summarize the following Jira issue for a Confluence update. "
            "Include key context, decisions, and next steps if present.\n\n"
            f"Jira JSON:\n{jira_payload}"
        )

    def _extract_content(self, payload: dict[str, Any]) -> str:
        if "choices" in payload and payload["choices"]:
            message = payload["choices"][0].get("message", {})
            content = message.get("content")
            if content:
                return content
        if "output" in payload:
            return str(payload["output"])
        if "text" in payload:
            return str(payload["text"])
        return str(payload)
