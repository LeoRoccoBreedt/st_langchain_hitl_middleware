# Streamlit LangChain Email Assistant

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://st-langchain-hitl-middleware.streamlit.app)

A Streamlit app demonstrating a LangChain agent with human-in-the-loop capabilities. The app is an AI email assistant that can look up contacts, compose emails, and simulate sending — with a human approval step before any email is dispatched.

## Features

- Chat interface for email composition
- LangChain agent with HITL middleware (approve / reject / edit)
- Contact directory with keyword search — drop-in replacement point for a real RAG retriever
- Multi-provider LLM support: Ollama (local), OpenAI, Groq, Anthropic, Google Gemini
- Dynamic model dropdown populated from the provider's API
- Environment-aware defaults: Ollama locally, OpenAI on Streamlit Cloud
- All credentials entered in the sidebar — no environment variables required
- Fresh session on provider or model switch
- Optional OPIK observability via `OpikTracer`
- In-memory checkpointing with LangGraph `InMemorySaver`

## Project structure

```
st_langchain_hitl_middleware/
├── src/
│   ├── agent.py       # create_email_agent() — model, tools, HITL middleware wiring
│   ├── contacts.py    # Fake contact directory + search_contacts()
│   ├── decisions.py   # approve / reject / edit decision schemas
│   ├── llm.py         # get_llm() and get_models() provider factory
│   └── tools.py       # send_email and lookup_contacts tools
├── st_app.py          # Streamlit UI — sidebar, chat, HITL buttons
└── pyproject.toml
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LeoRoccoBreedt/st_langchain_hitl_middleware.git
cd st_langchain_hitl_middleware
```

2. Install core dependencies:
```bash
uv sync
```

3. Install optional provider dependencies as needed:
```bash
uv pip install ".[groq]"       # Groq
uv pip install ".[anthropic]"  # Anthropic
uv pip install ".[google]"     # Google Gemini
uv pip install ".[all]"        # All providers
```

> This project uses [uv](https://github.com/astral-sh/uv) for dependency management. No `requirements.txt` — `uv sync` reads the lock file.

## Usage

```bash
streamlit run st_app.py
```

The app will be available at http://localhost:8501

### Selecting a provider

**Locally (default: Ollama)**
1. Make sure [Ollama](https://ollama.com) is running (`ollama serve`)
2. Pull a model — for MacBook Air, `llama3.2:3b` is recommended:
   ```bash
   ollama pull llama3.2:3b
   ```
3. Click **Connect to Ollama** in the sidebar — available models load automatically

**Other providers (Groq, OpenAI, Anthropic, Google)**
1. Select the provider from the dropdown
2. Enter your API key — the model list populates automatically on key entry
3. Select a model from the dropdown

> On Streamlit Cloud the default provider is OpenAI.

### Using the email assistant

1. Type in the chat input — e.g. *"Send Alice an update about the Q1 budget meeting"*
2. The agent uses `lookup_contacts` to find the recipient and relevant context
3. The agent drafts and attempts to send the email via `send_email`
4. The HITL middleware intercepts and shows an email preview with three options:
   - **Approve** — proceed with sending
   - **Reject** — cancel with a message back to the agent
   - **Edit** — modify recipient, subject, or body before sending
5. The agent confirms the outcome in the chat

### Enabling observability with OPIK (optional)

1. Toggle **Add observability** in the sidebar
2. Enter your OPIK project name (defaults to `Email_assistant_with_LangChain`)
3. Enter your [OPIK API key](https://www.comet.com/opik/)
4. All agent interactions are traced and sent to your OPIK project

## Contact directory

`src/contacts.py` contains a fake directory of 10 contacts, each with name, email, company, role, and context. The `search_contacts(query)` function performs a simple keyword search across all fields and is the single retrieval interface — swap its body for a vector store retrieval call to connect a real RAG system without changing any tool or agent code.

## Notebook

`example_hitl_middleware.ipynb` walks through the HITL interrupt/resume pattern interactively. Open with any Jupyter tooling or run in [Google Colab](https://colab.research.google.com/github/LeoRoccoBreedt/st_langchain_hitl_middleware/blob/main/example_hitl_middleware.ipynb).

## Changelog

### v0.3.0 — Multi-provider support, contact directory, Ollama integration

- **Multi-provider LLM:** Ollama, OpenAI, Groq, Anthropic, Google Gemini — selected from a sidebar dropdown
- **Dynamic model list:** model dropdown populated live from the provider's API on key entry
- **Ollama support:** local models listed via the Ollama Python SDK; no API key required
- **Environment-aware defaults:** Ollama locally, OpenAI on Streamlit Cloud (detected via `STREAMLIT_SHARING_MODE`)
- **Contact directory:** `src/contacts.py` with 10 fake contacts and `search_contacts()` — RAG-ready drop-in interface
- **`lookup_contacts` tool:** agent can search the contact directory before drafting emails
- **Agent code extracted to `src/`:** `agent.py`, `llm.py`, `tools.py`, `decisions.py` — `st_app.py` is UI-only
- **No environment variables required:** all credentials entered in the sidebar, scoped to `st.session_state`
- **Fresh session on switch:** changing provider or model resets chat history, agent, and checkpointer
- **Optional extras in `pyproject.toml`:** install only the provider packages you need

### v0.2.1 — API key session isolation
- OpenAI key passed directly to `ChatOpenAI` rather than via environment variables, scoping keys to each user session

### v0.2.0 — Observability, UI improvements & cloud stability
- Added optional OPIK observability via `OpikTracer` integration for LangChain
- Fixed `opik.configure()` hanging on Streamlit Cloud
- Cached `OpikTracer` in session state to avoid redundant network calls on reruns
- Added sidebar Resources section with GitHub and Google Colab links
- Added initial assistant greeting message on app load

### v0.1.1 — Approval workflow
- Human-in-the-loop UI: Approve / Reject / Edit buttons with email preview
- Edit dialog for modifying email details before sending
- Agent, checkpointer, and memory config persisted in `st.session_state`
- Updated to GPT-4o-mini for cost optimisation

### v0.1.0 — Initial release
- Basic chat interface with email composition assistant
- Simulated email sending via `send_email` tool
- In-memory checkpointing and session state persistence

## Development

- Python 3.12+
- [Streamlit](https://streamlit.io) — web interface
- [LangChain](https://python.langchain.com) — agent framework and tool abstractions
- [LangGraph](https://langchain-ai.github.io/langgraph/) — agent orchestration and HITL checkpointing
- [Ollama](https://ollama.com) — local model inference
- [uv](https://github.com/astral-sh/uv) — dependency management

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
