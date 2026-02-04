from __future__ import annotations

from datetime import datetime
from html import escape

from models.summary import SummaryResult


def build_confluence_body(summary: SummaryResult) -> str:
    created_at = summary.created_at.strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"<h1>WFA Summary for {escape(summary.jira_key)}</h1>"
        f"<p><strong>Generated:</strong> {escape(created_at)}</p>"
        "<h2>Jira Summary</h2>"
        f"<p>{escape(summary.jira_summary)}</p>"
        "<h2>Jira Description</h2>"
        f"<p>{escape(summary.jira_description).replace('\n', '<br />')}</p>"
        "<h2>LLM Response</h2>"
        f"<pre>{escape(summary.llm_response)}</pre>"
    )
