from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class JiraIssue:
    key: str
    summary: str
    description: str
    raw: dict[str, Any]
