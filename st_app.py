import streamlit as st

# LangChain code
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware

from langgraph.checkpoint.memory import InMemorySaver 
import uuid

from dotenv import load_dotenv
load_dotenv()

@tool()
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email to a recipient.
    Args:
        recipient: Email address of the recipient.
        subject: Subject line of the email.
        body: Body content of the email.
    Returns:
        Confirmation message.
    """
    return f"Email sent successfully to {recipient}"

# Sidebar # TODO: Add ability to set OpenAI API key
# with st.sidebar:
    # openai_api_key = st.text_input("OpenAI API key", type="password")

#config = {"configurable": {"thread_id": str(uuid.uuid4())}}
# config and agent: create once and keep in session_state so reruns don't recreate them
if "checkpointer" not in st.session_state:
    st.session_state["checkpointer"] = InMemorySaver()

if "agent" not in st.session_state:
    st.session_state["agent"] = create_agent(
        model="openai:gpt-4o",
        tools=[send_email],
        system_prompt="You are a helpful email assistant",
        # middleware=[HumanInTheLoopMiddleware(interrupt_on={"send_email": True})],
        checkpointer=st.session_state["checkpointer"],
    )

st.title("🦜🔗 Email Assistant")

# Create session state parameters
st.session_state.history = st.session_state.get("history", [])
st.session_state.stage = st.session_state.get("stage", "input")
st.session_state.agent_responses = st.session_state.get("agent_responses", [])

# initialize memory_config only if missing
st.session_state.setdefault("memory_config", {"configurable": {"thread_id": str(uuid.uuid4())}})

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("Ask me to send an email"):
    st.session_state.history.append({"role": "user", "content": user_input})

    # use the stored agent when invoking
    agent = st.session_state["agent"]
    agent_response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=st.session_state.memory_config
    )

    agent_response_message = agent_response["messages"][-1].content
    st.session_state.history.append({"role": "assistant", "content": agent_response_message})
    st.session_state.agent_responses = agent_response
    st.rerun()
