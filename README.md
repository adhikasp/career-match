## Career Match Evaluator

A simple Streamlit app to evaluate how well a job matches your resume and personal criteria using OpenRouter LLMs.

### Features
- **Resume input**: paste your resume text
- **Job description input**: paste the job description
- **Misc criteria**: add preferences like location, domain, salary range, work style
- **API key management**: enter and persist your OpenRouter API key through the UI
- **Model options**: configurable model and temperature
- **Light persistence**: resume, misc criteria, and API key saved to `career_match_data.json`

### Requirements
- **Python**: 3.9.8+
- **OpenRouter API key**: get one from [openrouter.ai](https://openrouter.ai)

### Setup
1) Install dependencies

  ```bash
  poetry install
  ```

### Run
   
   Using Poetry
  ```bash
  poetry run streamlit run app.py
  ```

### Usage
- Enter your OpenRouter API key in the sidebar (persisted across sessions)
- Paste your resume and the job description
- Add any misc criteria (e.g., remote-first, fintech, base pay range)
- Press "Run Evaluation" to get a structured analysis with strengths, gaps, and suggestions

### Configuration
- **API Key**: enter your OpenRouter API key in the sidebar
- **Model**: set in the sidebar; defaults to `openrouter/sonoma-dusk-alpha`
- **Temperature**: adjust creativity vs. determinism

### Data persistence
- The app stores your last "Resume", "Misc Criteria", and "API Key" entries in `career_match_data.json` (project root) so they persist across sessions. Delete this file to reset.

### Notes
- OpenRouter supports many providers/models. See [OpenRouter models](https://openrouter.ai/models) for names and availability.
- The response is displayed as Markdown; expand "Show raw response" to inspect the full JSON.

### Troubleshooting
- **Missing API key**: Enter your OpenRouter API key in the sidebar.
- **401/403 errors**: Verify your key has access to the selected model.
- **Network/timeout errors**: Check connectivity; try again later. Raw responses are shown in the expander.
