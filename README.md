# Streamlit LangChain Email Assistant

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit-badge.svg)](https://stlangchainhitlmiddleware-fr2zh8xrql6ponturgtb25.streamlit.app)


A simple Streamlit app demonstrating LangChain integration with human-in-the-loop capabilities. The app serves as an AI email assistant that can help compose and (simulate) sending emails.

## Features

- Chat interface for email composition
- LangChain agent integration
- Human-in-the-loop approval workflow (approve / reject / edit)
- Session persistence for agent, checkpointer and memory config
- Email sending simulation
- GPT-4 powered responses
- In-memory checkpointing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/st_langchain_hitl_middleware.git
cd st_langchain_hitl_middleware
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Note: this repo uses UV for dependency management (no requirements.txt). uv sync will read the lock/project files included in the repo.

## Usage

Run the Streamlit app:
```bash
streamlit run st_app.py
```

The app will be available at http://localhost:8501

### Using the Email Assistant

1. Start typing in the chat input at the bottom of the screen.
2. Ask the assistant to compose or send an email.
3. If the agent proposes a tool action (send_email) the human-in-the-loop UI will appear with an email preview and action buttons:
   - Approve — proceeds with the action
   - Reject — cancels the action with an optional message
   - Edit — lets the user edit the suggested action arguments (in-progress)
4. Conversation history and the agent/checkpointer/memory_config are preserved during the Streamlit session.

## Notebook

An example notebook demonstrating the approval/interrupt workflow is included:
- example_hitl_middleware.ipynb

Open and run the notebook with your preferred Jupyter tooling to step through the flow interactively.

## Architecture

- Built with Streamlit for the web interface
- Uses LangChain for the AI agent implementation
- HumanInTheLoopMiddleware handles tool interruptions with allowed decisions: `approve`, `reject`, `edit`
- InMemorySaver used for checkpointing
- Session state is used to persist agent, checkpointer and memory configuration across reruns
- OpenAI GPT-4o-mini model for natural language understanding and email composition

## Changelog

### v0.1.1 — Approval workflow update
- Added human-in-the-loop approval workflow to the Streamlit app:
  - UI buttons for Approve / Reject / Edit with an email preview.
  - Interrupt handling to extract action requests and present them for human decision.
  - Edit dialog allows users to modify email details before sending.
- Persist agent, checkpointer and memory_config in st.session_state to avoid recreating them on reruns.
- Ensured memory_config (thread_id) is initialized once per session and reused for agent invocations.
- Updated to use GPT-4o-mini model for cost optimization.
- Agent system prompt now confirms all actions to the user.
- Minor UI improvements to show assistant preview and intervention stage.

### v0.1.0 — Initial release
- Basic chat interface
- Email composition assistant using GPT-4
- Simulated email sending capability
- Session state persistence for conversation history
- In-memory checkpointing for LangChain agent
- Thread ID management for conversation tracking

## Development

The project uses:
- Python 3.8+
- Streamlit for the web interface
- LangChain for AI agent capabilities
- OpenAI's GPT-4 model
- UV for dependency management

## License

MIT

## Contributing

1. Fork the repository  
2. Create your feature branch  
3. Commit your changes  
4. Push to the branch  
5. Create a new Pull Request