from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SummaryResult:
    jira_key: str
    jira_summary: str
    jira_description: str
    llm_response: str
    created_at: datetime
    metadata: dict[str, Any]
