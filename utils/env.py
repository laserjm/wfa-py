from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    jira_base_url: str = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    jira_email: str = os.getenv("JIRA_EMAIL", "")
    jira_api_token: str = os.getenv("JIRA_API_TOKEN", "")

    confluence_base_url: str = os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")
    confluence_email: str = os.getenv("CONFLUENCE_EMAIL", "")
    confluence_api_token: str = os.getenv("CONFLUENCE_API_TOKEN", "")
    confluence_space_key: str = os.getenv("CONFLUENCE_SPACE_KEY", "")

    llm_api_url: str = os.getenv("LLM_API_URL", "")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "")

    def validate(self) -> list[str]:
        missing: list[str] = []
        if not self.jira_base_url:
            missing.append("JIRA_BASE_URL")
        if not self.jira_email:
            missing.append("JIRA_EMAIL")
        if not self.jira_api_token:
            missing.append("JIRA_API_TOKEN")
        if not self.confluence_base_url:
            missing.append("CONFLUENCE_BASE_URL")
        if not self.confluence_email:
            missing.append("CONFLUENCE_EMAIL")
        if not self.confluence_api_token:
            missing.append("CONFLUENCE_API_TOKEN")
        if not self.confluence_space_key:
            missing.append("CONFLUENCE_SPACE_KEY")
        if not self.llm_api_url:
            missing.append("LLM_API_URL")
        if not self.llm_api_key:
            missing.append("LLM_API_KEY")
        if not self.llm_model:
            missing.append("LLM_MODEL")
        return missing


def get_settings() -> Settings:
    return Settings()
