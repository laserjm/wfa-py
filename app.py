from __future__ import annotations

from datetime import datetime
import streamlit as st

from models.summary import SummaryResult
from services.confluence.service import ConfluenceService
from services.jira.service import JiraService
from services.llm.service import LlmService
from utils.confluence import build_confluence_body
from utils.env import get_settings


st.set_page_config(page_title="WFA", layout="centered")

st.title("WFA — Workflow Automation")
st.write("Create a Confluence summary from a Jira issue using an LLM.")

settings = get_settings()
missing = settings.validate()
if missing:
    st.warning(
        "Missing environment variables. Update your .env file and refresh:\n"
        + ", ".join(missing)
    )

with st.form("wfa-form"):
    jira_key = st.text_input("Jira key", placeholder="ABC-123")
    confluence_title = st.text_input("Confluence page title", placeholder="Weekly Summary - ABC-123")
    confluence_page_id = st.text_input("Confluence page ID (optional)", placeholder="123456")
    confluence_space_key = st.text_input(
        "Confluence space key", value=settings.confluence_space_key or "", placeholder="SPACE"
    )
    system_prompt = st.text_area(
        "System prompt",
        value=(
            "You are a concise technical writer. Summarize the Jira issue for a Confluence update. "
            "Return clear sections: Overview, Impact, Decisions, Next Steps."
        ),
        height=120,
    )
    submitted = st.form_submit_button("Create summary")

if submitted:
    if not jira_key or not confluence_title:
        st.error("Please provide Jira key and Confluence title.")
        st.stop()
    if not confluence_space_key and not confluence_page_id:
        st.error("Provide a Confluence space key or a page ID.")
        st.stop()

    try:
        jira_service = JiraService(
            base_url=settings.jira_base_url,
            email=settings.jira_email,
            api_token=settings.jira_api_token,
        )
        confluence_service = ConfluenceService(
            base_url=settings.confluence_base_url,
            email=settings.confluence_email,
            api_token=settings.confluence_api_token,
        )
        llm_service = LlmService(
            api_url=settings.llm_api_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )

        with st.spinner("Fetching Jira issue..."):
            issue = jira_service.fetch_issue(jira_key.strip())
        st.success("Jira issue loaded.")

        with st.spinner("Sending to LLM..."):
            llm_response = llm_service.summarize_jira(issue.raw, system_prompt)
        st.success("LLM response received.")

        summary = SummaryResult(
            jira_key=issue.key,
            jira_summary=issue.summary,
            jira_description=issue.description,
            llm_response=llm_response,
            created_at=datetime.utcnow(),
            metadata={"source": "wfa", "jira_key": issue.key},
        )

        st.subheader("Internal processing step")
        st.json(
            {
                "jira_key": summary.jira_key,
                "jira_summary": summary.jira_summary,
                "jira_description": summary.jira_description,
                "llm_response": summary.llm_response,
                "created_at": summary.created_at.isoformat(),
                "metadata": summary.metadata,
            }
        )

        body_html = build_confluence_body(summary)

        with st.spinner("Updating Confluence..."):
            result = confluence_service.upsert_page(
                space_key=confluence_space_key.strip(),
                title=confluence_title.strip(),
                body_html=body_html,
                page_id=confluence_page_id.strip() or None,
            )

        page_id = result.get("id")
        st.success("Confluence page created/updated.")
        if page_id:
            st.write(f"Confluence page ID: {page_id}")
            if settings.confluence_base_url:
                st.write(
                    f"Open page: {settings.confluence_base_url}/pages/viewpage.action?pageId={page_id}"
                )

    except Exception as exc:
        st.error(f"WFA failed: {exc}")
