import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
import uuid

from dotenv import load_dotenv
load_dotenv()

from src.llm import get_llm, get_models, is_cloud, PROVIDER_DEFAULTS, REQUIRES_API_KEY
from src.agent import create_email_agent
from src.decisions import decisions


# ---------------------------------------------------------------------------
# Sidebar callbacks
# ---------------------------------------------------------------------------

_SESSION_KEYS = [
    "agent", "checkpointer", "history", "stage", "email", "email_edited",
    "agent_responses", "invoke_config", "available_models", "models_error",
    "api_key", "provider", "ollama_connected",
]


def _reset_session():
    """Clear all app state for a fresh session."""
    for key in _SESSION_KEYS:
        st.session_state.pop(key, None)


def _on_provider_change():
    _reset_session()


def _on_key_change():
    """Fetch models when the API key changes; start a fresh session."""
    key = st.session_state.get("_api_key_input", "").strip()
    provider = st.session_state.get("_provider_select", list(PROVIDER_DEFAULTS.keys())[0])

    _reset_session()

    if not key:
        return

    try:
        models = get_models(provider, key)
        st.session_state["available_models"] = models
        st.session_state["api_key"] = key
        st.session_state["provider"] = provider
    except Exception as e:
        st.session_state["models_error"] = str(e)


def _on_ollama_connect():
    """Fetch local Ollama models and start a fresh session."""
    provider = "Ollama"
    _reset_session()

    try:
        models = get_models(provider)
        st.session_state["available_models"] = models
        st.session_state["ollama_connected"] = True
        st.session_state["api_key"] = ""
        st.session_state["provider"] = provider
    except Exception as e:
        st.session_state["models_error"] = str(e)
        st.session_state["ollama_connected"] = False


def _on_model_change():
    """Reset chat session when selected model changes, keeping connection state."""
    available = st.session_state.get("available_models")
    provider = st.session_state.get("provider")
    api_key = st.session_state.get("api_key")
    ollama_connected = st.session_state.get("ollama_connected")
    _reset_session()
    st.session_state["available_models"] = available
    st.session_state["provider"] = provider
    st.session_state["api_key"] = api_key
    st.session_state["ollama_connected"] = ollama_connected


# ---------------------------------------------------------------------------
# Email edit dialog
# ---------------------------------------------------------------------------

@st.dialog("Edit Email", width="medium")
def edit_email():
    recipient = st.text_input(
        "Recipient",
        value=st.session_state.get("email", {}).get("recipient", "")
    )
    subject = st.text_input("Subject", value=st.session_state.get("email", {}).get("subject", ""))
    body = st.text_area("Body", value=st.session_state.get("email", {}).get("body", ""))

    if st.button("Send"):
        st.session_state["email"] = {
            "recipient": recipient,
            "subject": subject,
            "body": body,
        }
        st.session_state["email_edited"] = True
        st.rerun()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Model provider", divider="grey")

    providers = list(PROVIDER_DEFAULTS.keys())
    default_provider = "OpenAI" if is_cloud() else "Ollama"
    default_provider_idx = providers.index(default_provider)

    provider = st.selectbox(
        "Select provider",
        options=providers,
        index=default_provider_idx,
        key="_provider_select",
        on_change=_on_provider_change,
    )

    if provider in REQUIRES_API_KEY:
        st.text_input(
            f"{provider} API key",
            value="",
            type="password",
            icon=":material/password:",
            key="_api_key_input",
            on_change=_on_key_change,
        )
    else:
        # Ollama — no key needed, connect directly to local server
        if st.button("Connect to Ollama", on_click=_on_ollama_connect):
            pass

    if st.session_state.get("models_error"):
        st.error(f"Could not connect: {st.session_state['models_error']}")
    elif st.session_state.get("available_models"):
        available = st.session_state["available_models"]
        default = PROVIDER_DEFAULTS.get(provider)
        default_idx = available.index(default) if default in available else 0
        st.selectbox(
            "Model",
            options=available,
            index=default_idx,
            key="_model_select",
            on_change=_on_model_change,
        )
        st.success(f"Connected — {len(available)} models available")
    elif provider == "Ollama" and st.session_state.get("ollama_connected"):
        st.warning("No models found. Pull one first, e.g.:\n```\nollama pull llama3.2\n```")
    else:
        if provider in REQUIRES_API_KEY:
            st.warning(f"Enter your {provider} API key to load models.")
        else:
            st.warning("Click 'Connect to Ollama' to load local models.")

    st.header("Observability by OPIK", divider="grey")
    st.markdown("[What is OPIK?](https://www.comet.com/docs/opik/)", unsafe_allow_html=True)
    observe = st.toggle(
        "Add observability",
        value=False,
        help="Enable to send traces of agent interactions to OPIK for monitoring and analysis",
    )

    if observe:
        import opik
        from opik.integrations.langchain import OpikTracer

        opik_project = st.text_input(
            "OPIK Project Name",
            value=st.session_state.get("opik_project") or "Email_assistant_with_LangChain",
            help="Name of the project in OPIK where traces will be sent",
        )

        opik_key = st.text_input(
            "OPIK API Key",
            value=st.session_state.get("opik_key", ""),
            type="password",
            icon=":material/password:",
        )

        if opik_key:
            st.session_state["opik_key"] = opik_key

            if not st.session_state.get("opik_configured"):
                opik.configure(use_local=False, api_key=opik_key, automatic_approvals=True)
                st.session_state["opik_configured"] = True

            if "opik_tracer" not in st.session_state or st.session_state.get("opik_project") != opik_project:
                st.session_state["opik_project"] = opik_project
                st.session_state["opik_tracer"] = OpikTracer(project_name=opik_project)

            opik_tracer = st.session_state["opik_tracer"]
        else:
            st.warning("Please enter your OPIK API key to enable observability.")

    st.header("Resources", help="Links to the GitHub repo and Colab notebook for this demo", divider="grey")
    st.markdown(
        """
        <div style="font-size: 0.95rem; color: gray;">
            <a href="https://github.com/LeoRoccoBreedt/st_langchain_hitl_middleware" target="_blank" style="color: inherit; text-decoration: none; display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
                </svg>
                GitHub
            </a>
            <a href="https://colab.research.google.com/github/LeoRoccoBreedt/st_langchain_hitl_middleware/blob/main/example_hitl_middleware.ipynb" target="_blank" style="color: inherit; text-decoration: none; display: flex; align-items: center; gap: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#F9AB00">
                    <path d="M16.9414 4.9757a7.033 7.033 0 0 0-4.9308 2.0646 7.033 7.033 0 0 0-.1232 9.8068l2.395-2.395a3.6455 3.6455 0 0 1 5.1497-5.1478l2.397-2.3989a7.033 7.033 0 0 0-4.8877-1.9297zM7.07 4.9855a7.033 7.033 0 0 0-4.8878 1.9316l2.3911 2.3911a3.6434 3.6434 0 0 1 5.0227.1271l1.7341-2.9737-.0997-.0802A7.033 7.033 0 0 0 7.07 4.9855zm15.0093 2.1721l-2.3892 2.3911a3.6455 3.6455 0 0 1-5.1497 5.1497l-2.4067 2.4068a7.0362 7.0362 0 0 0 9.9456-9.9476zM1.932 7.1674a7.033 7.033 0 0 0-.002 9.6816l2.397-2.397a3.6434 3.6434 0 0 1-.004-4.8916zm7.664 7.4235c-1.38 1.3816-3.5863 1.411-5.0168.1134l-2.397 2.395c2.4693 2.3328 6.263 2.5753 9.0072.5455l.1368-.1115z"/>
                </svg>
                Open in Colab
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

st.title("Email Assistant")

_ready = st.session_state.get("available_models") and st.session_state.get("provider")
if not _ready:
    st.info("Select a provider and connect in the sidebar to get started.")
    st.stop()

# Initialise checkpointer and agent once per session (or after provider change)
if "checkpointer" not in st.session_state:
    st.session_state["checkpointer"] = InMemorySaver()

if "agent" not in st.session_state:
    provider = st.session_state["provider"]
    # _model_select is set by the widget; fall back to the provider default
    selected_model = (
        st.session_state.get("_model_select")
        or PROVIDER_DEFAULTS.get(provider)
    )
    llm = get_llm(
        provider=provider,
        model=selected_model,
        api_key=st.session_state.get("api_key", ""),
    )
    st.session_state["agent"] = create_email_agent(llm, st.session_state["checkpointer"])

# Session state defaults
st.session_state.history = st.session_state.get("history", [])
st.session_state.stage = st.session_state.get("stage", "input")
st.session_state.agent_responses = st.session_state.get("agent_responses", [])
st.session_state.setdefault("email", {"recipient": "", "subject": "", "body": ""})

st.session_state["invoke_config"] = {
    "configurable": st.session_state.get("invoke_config", {}).get("configurable") or {"thread_id": str(uuid.uuid4())},
    "callbacks": [opik_tracer] if observe and "opik_tracer" in dir() else [],
}

# Welcome message
if not st.session_state.history:
    with st.chat_message("assistant"):
        st.write(
            "Hi! I'm your email assistant. I can help you **draft and send emails** — "
            "just tell me who you'd like to email and what it's about.\n\n"
            "Before anything is sent, I'll ask you to **approve, edit, or reject** the email, "
            "so you're always in control."
        )

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

if user_input := st.chat_input("Ask me to send an email"):
    st.session_state.history.append({"role": "user", "content": user_input})

    agent = st.session_state["agent"]
    agent_response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=st.session_state.invoke_config,
    )

    agent_response_message = agent_response["messages"][-1].content
    if "__interrupt__" in agent_response:
        action_request = agent_response["__interrupt__"][-1].value["action_requests"][-1]
        recipient = action_request["args"]["recipient"]
        subject = action_request["args"]["subject"]
        body = action_request["args"]["body"]
        agent_response_message = f"**To:** {recipient}\n\n**Subject:** {subject}\n\n**Body:**\n\n{body}"
        st.session_state.stage = "intervention"
        st.session_state["email"] = {"recipient": recipient, "subject": subject, "body": body}

    st.session_state.history.append({"role": "assistant", "content": agent_response_message})
    st.session_state.agent_responses = agent_response
    st.rerun()

# ---------------------------------------------------------------------------
# HITL intervention buttons
# ---------------------------------------------------------------------------

if "__interrupt__" in st.session_state.agent_responses and st.session_state.stage == "intervention":
    description = st.session_state.agent_responses["__interrupt__"][-1].value["action_requests"][-1]
    st.warning(f"Human intervention required for tool: {description['name']}")

    buttons = st.columns(6)
    with buttons[0]:
        if st.button("Approve", key="approve", type="primary", width="stretch", help="Approve the email"):
            agent = st.session_state["agent"]
            result = agent.invoke(
                Command(resume=decisions.get("approve")),
                config=st.session_state.invoke_config,
            )
            st.session_state.history.append({"role": "assistant", "content": result["messages"][-1].content})
            st.session_state.stage = "input"
            st.session_state["agent_responses"] = result
            st.rerun()

    with buttons[1]:
        if st.button("Reject", key="reject", type="secondary", width="stretch", help="Reject the email"):
            agent = st.session_state["agent"]
            result = agent.invoke(
                Command(resume=decisions.get("reject")),
                config=st.session_state.invoke_config,
            )
            st.session_state.history.append({"role": "assistant", "content": result["messages"][-1].content})
            st.session_state.stage = "input"
            st.rerun()

    with buttons[2]:
        if st.button("Edit", key="edit", type="secondary", width="stretch", help="Edit the email"):
            st.session_state["email_edited"] = False
            edit_email()

        if st.session_state.get("email_edited"):
            agent = st.session_state["agent"]
            result = agent.invoke(
                Command(
                    resume={
                        "decisions": [
                            {
                                "type": "edit",
                                "edited_action": {
                                    "name": "send_email",
                                    "args": st.session_state["email"],
                                },
                            }
                        ]
                    }
                ),
                config=st.session_state.invoke_config,
            )
            st.session_state.history.append({"role": "assistant", "content": result["messages"][-1].content})
            st.session_state.stage = "input"
            st.success("Email edited and sent!")
            st.session_state["agent_responses"] = result
            st.rerun()
