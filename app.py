import os
import json
import textwrap
from typing import Optional, Dict, Any

import requests
import streamlit as st

# Data persistence file
DATA_FILE = "career_match_data.json"


def save_user_data(resume_text: str, misc_criteria: str, api_key: str = "") -> None:
    """Save user data to a JSON file for persistence."""
    data = {
        "resume_text": resume_text,
        "misc_criteria": misc_criteria,
        "api_key": api_key,
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        # Silently fail if we can't save - don't interrupt user experience
        pass


def load_user_data() -> Dict[str, str]:
    """Load user data from JSON file, return defaults if file doesn't exist."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "resume_text": data.get("resume_text", ""),
                    "misc_criteria": data.get("misc_criteria", ""),
                    "api_key": data.get("api_key", ""),
                }
    except Exception:
        # Silently fail if we can't load - return defaults
        pass
    return {"resume_text": "", "misc_criteria": "", "api_key": ""}


# OpenRouter API key is now managed through the UI
DEFAULT_MODEL = "openrouter/sonoma-dusk-alpha"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(
    api_key: str,
    resume_text: str,
    job_description: str,
    misc_criteria: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    request_timeout_seconds: int = 60,
) -> Dict[str, Any]:
    """Call OpenRouter chat completion with a structured prompt for job match analysis.

    Returns a dict with keys: {"ok": bool, "content": str, "raw": dict, "error": Optional[str]}.
    """

    system_message = textwrap.dedent(
        """
        You are a career coach and resume expert. Evaluate how well a my resume aligns with a specific job description, incorporating any additional criteria I care about. Provide:
        - A clear "Go apply" or "Don't bother" verdict and confidence level of your certainity (0-100%).
        - Top strengths that align well.
        - Key gaps or risks.
        - Actionable suggestions to improve the resume and application.
        - Tailored advice for interview preparation.
        Keep the response concise, structured, and directly useful. Use bullet points where appropriate.
        Use markdown format for the response.
        """
    ).strip()

    user_message = textwrap.dedent(
        f"""
        <MyResume>
        {resume_text}   
        </MyResume>

        <JobDescription>
        {job_description}
        </JobDescription>

        <MiscCriteria>
        {misc_criteria}
        </MiscCriteria>
        """
    ).strip()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    }

    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=request_timeout_seconds,
        )
    except requests.RequestException as exc:
        return {
            "ok": False,
            "content": "",
            "raw": {},
            "error": f"Network error: {exc}",
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "content": "",
            "raw": {
                "status_code": response.status_code,
                "text": response.text,
            },
            "error": f"API error {response.status_code}: {response.text}",
        }

    try:
        data = response.json()
    except Exception:
        return {
            "ok": False,
            "content": "",
            "raw": {"text": response.text},
            "error": "Failed to parse API response as JSON.",
        }

    content: Optional[str] = None
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = None

    if not content:
        return {
            "ok": False,
            "content": "",
            "raw": data,
            "error": "Empty response from model.",
        }

    return {"ok": True, "content": content, "raw": data, "error": None}


def main() -> None:
    st.set_page_config(page_title="Career Match Evaluator", page_icon="💼", layout="wide")
    st.title("Career Match Evaluator")
    st.caption("Analyze how well a role matches your resume and preferences.")

    # Load persisted data
    persisted_data = load_user_data()

    # Initialize session state with persisted data
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = persisted_data["resume_text"]
    if "misc_criteria" not in st.session_state:
        st.session_state.misc_criteria = persisted_data["misc_criteria"]
    if "api_key" not in st.session_state:
        st.session_state.api_key = persisted_data["api_key"]

    with st.sidebar:
        st.subheader("Settings")
        default_model = DEFAULT_MODEL
        model = st.text_input(
            label="Model",
            value=default_model,
            help=(
                "OpenRouter model to use (e.g., 'openrouter/auto', 'anthropic/claude-3.5-sonnet', 'openai/gpt-4o-mini')."
            ),
        )
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        api_key = st.text_input(
            label="OpenRouter API Key",
            value=st.session_state.api_key,
            type="password",
            help="Enter your OpenRouter API key. Get one from https://openrouter.ai",
            key="api_key",
        )
        if not api_key:
            st.warning("Please enter your OpenRouter API key to use the application.")

    col1, col2 = st.columns(2)
    with col1:
        resume_text = st.text_area(
            label="Your Resume",
            placeholder="Paste your resume text here...",
            height=300,
            key="resume_text",
        )
    with col2:
        job_description = st.text_area(
            label="Job Description",
            placeholder="Paste the job description here...",
            height=300,
        )

    misc_criteria = st.text_area(
        label="Misc Criteria / Preferences",
        placeholder="e.g., Remote-first, growth-stage startups, fintech domain, base salary range $X–$Y, strong mentorship, visa support, etc.",
        height=140,
        key="misc_criteria",
    )

    submit = st.button("Run Evaluation", type="primary")

    if submit:
        if not resume_text.strip():
            st.error("Please paste your resume.")
            return
        if not job_description.strip():
            st.error("Please paste the job description.")
            return
        if not api_key:
            st.error("Please enter your OpenRouter API key in the sidebar.")
            return

        with st.spinner("Analyzing match with the LLM..."):
            result = call_openrouter(
                api_key=api_key,
                resume_text=resume_text,
                job_description=job_description,
                misc_criteria=misc_criteria,
                model=model.strip() or DEFAULT_MODEL,
                temperature=float(temperature),
            )

            # Save user data for persistence
            if resume_text.strip() or misc_criteria.strip() or api_key.strip():
                save_user_data(resume_text, misc_criteria, api_key)

        if not result.get("ok"):
            st.error(result.get("error") or "Unknown error")
            with st.expander("Show raw response"):
                st.code(json.dumps(result.get("raw"), indent=2))
            return

        st.subheader("Results")
        st.markdown(result["content"])  # Model usually returns Markdown-friendly text

        with st.expander("Show raw response"):
            st.code(json.dumps(result.get("raw"), indent=2))


if __name__ == "__main__":
    main()


