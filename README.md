## Career Match Evaluator

A simple Streamlit app to evaluate how well a job matches your resume and personal criteria using OpenRouter LLMs.

### Features
- **Resume input**: paste your resume text
- **Job description input**: paste the job description
- **Misc criteria**: add preferences like location, domain, salary range, work style
- **Model options**: configurable model and temperature
- **Light persistence**: resume and misc criteria saved to `career_match_data.json`

### Requirements
- **Python**: 3.9.8+
- **OpenRouter API key**: get one from [openrouter.ai](https://openrouter.ai)

### Setup
1) Install dependencies
   
  ```bash
  poetry install
  ```
   

2) Configure your OpenRouter API key
   Create a `.env` file in the project root and set your key. The app reads `OPENROUTER_API_KEY` automatically.
  ```dotenv
  OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxxxxx
  ```

### Run
   
   Using Poetry
  ```bash
  poetry run streamlit run app.py
  ```

### Usage
- Paste your resume and the job description
- Add any misc criteria (e.g., remote-first, fintech, base pay range)
- Press "Run Evaluation" to get a structured analysis with strengths, gaps, and suggestions

### Configuration
- **Model**: set in the sidebar; defaults to `openrouter/sonoma-dusk-alpha`
- **Temperature**: adjust creativity vs. determinism
- **Environment**: the app loads `.env` automatically if present

### Data persistence
- The app stores your last "Resume" and "Misc Criteria" entries in `career_match_data.json` (project root) so they persist across sessions. Delete this file to reset.

### Notes
- OpenRouter supports many providers/models. See [OpenRouter models](https://openrouter.ai/models) for names and availability.
- The response is displayed as Markdown; expand "Show raw response" to inspect the full JSON.

### Troubleshooting
- **Missing API key**: Set `OPENROUTER_API_KEY` in `.env` or your shell environment.
- **401/403 errors**: Verify your key has access to the selected model.
- **Network/timeout errors**: Check connectivity; try again later. Raw responses are shown in the expander.
