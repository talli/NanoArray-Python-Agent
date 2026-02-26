# NanoArray Python Agent

A standalone Python-based autonomous research agent designed to perform literature review, competitive intelligence, and patent analysis for the hyper-multiplexed single-molecule detection platform.

## Architecture
- Parses `CLAUDE.md` to extract research domains.
- Uses LLMs and web search to autonomously gather intelligence.
- Outputs structured markdown to `findings/`, `sources/`, and `summaries/`.
## Setup
Create a `.env` file in the root directory with your preferred API keys:
```env
# Choose your LLM Provider:
ANTHROPIC_API_KEY=your_anthropic_api_key  # For Claude 3.5 Sonnet (Default)
# OR
GOOGLE_API_KEY=your_google_api_key        # For Gemini 2.5 Pro

# Web Search
SERPAPI_API_KEY=your_serpapi_api_key      # Optional: For Google Search results
```

## Running
```bash
uv run python research_agent.py
```
