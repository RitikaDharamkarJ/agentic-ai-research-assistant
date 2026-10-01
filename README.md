# Agentic AI Research Assistant

A Python command-line project that uses LangChain, LangGraph, Gemini, and Tavily to search the web, review retrieved evidence, and save a structured Markdown research report.

The project adapts the supplied `06a_Agent_CreateAgent` example: arithmetic tools are replaced with bounded web search and text analysis. Separate workflow stages gather research, review the evidence, summarize findings, and propose recommendations.

## Purpose and Workflow

Enter a research topic. The research agent chooses web searches and can call a text-analysis tool. The application retains retrieved source excerpts and IDs. A Gemini evidence-review call compares research notes against those excerpts; subsequent calls summarize the findings and produce recommendations.

The sequence is **Research → Evidence review → Summary → Recommendations → Report files**. Only the research stage has tools; the other stages are model calls coordinated through LangGraph. Evidence review is not independent fact verification.

## Technologies

| Technology | Role |
|---|---|
| Python | CLI, tools, configuration, and report export |
| LangChain `create_agent` | Model/tool execution loop for research |
| LangGraph `StateGraph` | Explicit stages and shared workflow state |
| Gemini via `langchain-google-genai` | Research, evidence review, summary, and recommendations |
| Tavily Python SDK | Public web search and page excerpts |
| python-dotenv | Loading API credentials from a local file |
| unittest | Offline search, citation, analysis, and reporting checks |

## Files and Execution Order

| File | Responsibility / when used |
|---|---|
| `.env.example` | Template to copy to a private `.env` before running |
| `requirements.txt` | Dependencies to install before running |
| `tools.py` | Search budget, source registry, text analysis, and citation-ID checks |
| `research_assistant.py` | Entry point; constructs and runs the workflow and exports reports |
| `test_tools.py` | Offline checks; run separately |
| `.gitignore` | Excludes secrets, environment, bytecode, and generated reports |

Run `research_assistant.py`; it imports `tools.py` automatically. The original PDF examples are learning references, not scripts that must be run in sequence, and are not included because they contain embedded API keys.

## Setup on Windows PowerShell

Use Python 3.10 or later. From the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally with your own replacement credentials:

```dotenv
GEMINI_API_KEY=your_new_gemini_key
TAVILY_API_KEY=your_tavily_key
GEMINI_MODEL=gemini-2.5-flash
```

Do not commit `.env` or the original PDFs containing keys. API access and any provider charges require your own accounts. The model is configurable; availability depends on your account. Dependencies use version ranges rather than a lock file.

## Run

```powershell
python research_assistant.py "What are the benefits and limitations of AI in healthcare?" --output reports/healthcare_ai.md
```

Outputs:

- `reports/healthcare_ai.md`: summary, evidence review, recommendations, source list, and limitations.
- `reports/healthcare_ai.sources.json`: retrieved excerpts, source IDs, URLs, and retrieval timestamps.

Choose a new output filename for each run; the program refuses to overwrite existing outputs. Reports are excluded from Git by default.

The default search budget is four requests, with at most five results per request. To adjust it:

```powershell
python research_assistant.py "Your topic" --max-searches 3 --output reports/topic.md
```

## Checks

```powershell
python -m unittest -v test_tools.py
```

Offline tests exercise source deduplication, unsafe URL-scheme filtering, search budget enforcement, search failures, text analysis, citation-ID checks, and report rendering. The actual LangChain tool loop and all LangGraph stages also passed an integration check with simulated model and search providers. A live end-to-end run with Gemini and Tavily has not been completed in the delivery environment.

## Editing Guide

- **Change the research topic:** supply a different CLI argument; no source edits needed.
- **Change credentials or model:** edit private `.env` only.
- **Change search result count or excerpt length:** edit `ResearchTools.search()` in `tools.py`.
- **Change role instructions:** edit prompts in `build_workflow()` in `research_assistant.py`.
- **Change report sections:** edit `render_report()` in `research_assistant.py`.
- **Change output location:** use `--output`.

## Limits

The system relies on external search results and bounded excerpts (up to 6,000 characters per source). It cannot guarantee completeness or factual accuracy. Text analysis reports word counts and frequent terms, not a scientific sentiment or fact-check score. Citation checks validate known source IDs, not whether a source entails a claim. Some sources may be uncited in the report's source inventory.

Retrieved pages are treated as untrusted data in prompts, but prompt instructions cannot guarantee protection from malicious page content. There is no chat persistence, deployed UI, automated factual benchmark, or human approval loop. Each run starts fresh. Topics and retrieved evidence are sent to external services; use public, nonconfidential material.

## Author

**Ritika Dharamkar** — [GitHub](https://github.com/RitikaDharamkarJ)

## API References

- [LangChain create_agent](https://reference.langchain.com/python/langchain/agents/factory/create_agent)
- [Tavily Python SDK](https://github.com/tavily-ai/tavily-python)
