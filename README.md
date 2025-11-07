# Streamlit LangChain Email Assistant

A simple Streamlit app demonstrating LangChain integration with human-in-the-loop capabilities. The app serves as an AI email assistant that can help compose and (simulate) sending emails.

## Features

- Chat interface for email composition
- LangChain agent integration
- Session persistence
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

## Usage

Run the Streamlit app:
```bash
streamlit run st_app.py
```

The app will be available at http://localhost:8501

### Using the Email Assistant

1. Start typing in the chat input at the bottom of the screen
2. Ask the assistant to help you compose or send an email
3. The assistant will help draft the email content and simulate sending it
4. Your conversation history is preserved during the session

## Architecture

- Built with Streamlit for the web interface
- Uses LangChain for the AI agent implementation
- Implements session state management for persistence
- Uses OpenAI's GPT-4 model for natural language understanding
- Includes in-memory checkpointing for conversation state

## Changelog

### v0.1.0

Initial release with the following functionality:
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