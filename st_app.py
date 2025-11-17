import streamlit as st

# LangChain code
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware

from langgraph.checkpoint.memory import InMemorySaver 
from langgraph.types import Command
import uuid
import os

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
    return f"Email sent successfully to {recipient}, regarding '{subject}'."

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
        st.session_state["email_edited"] = True  # Set the flag to indicate the email was edited
        st.rerun()  # Rerun to update the state

# Choose decision
# Approval decision
approval = {
    "decisions": [
        {
            "type": "approve"
        }
    ]
}

# Decisions to parse to tool interruption
# Edit decision
edit = {
    "decisions": [
        {
            "type": "edit",
            "edited_action": {
                "name": "send_email",
                "args": {
                    "recipient": "partner@startup.com",
                    "subject": "Budget proposal for Q1 2026",
                    "body": "I can only approve up to 500k, please send over details.",
                }
            }
        }
    ]
}

# Reject decision
reject = {
    "decisions": [
        {
            "type": "reject",
            "message": "Do not send an email. The email needs more context or additionans from the user."
        }
    ]
}
# single dictionary to index into and return the correct dict
decisions = {
    "approve": approval,
    "edit": edit,
    "reject": reject,
}

# Sidebar # TODO: Add ability to set OpenAI API key
with st.sidebar:
    api_key = st.text_input(
        "OpenAI API key",
        value=st.session_state.get("api_key") or os.getenv("OPENAI_API_KEY", ""),
        type="password",
        icon=":material/password:")
    
    #Set session state for use of API and the environment variable for the create_agent
    if api_key:
        st.session_state["api_key"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    else:
        st.warning("Please enter your OpenAI API key to use the app.")

#config = {"configurable": {"thread_id": str(uuid.uuid4())}}
# config and agent: create once and keep in session_state so reruns don't recreate them
if "checkpointer" not in st.session_state:
    st.session_state["checkpointer"] = InMemorySaver()

if "agent" not in st.session_state:
    st.session_state["agent"] = create_agent(
        model="openai:gpt-4o-mini",
        tools=[send_email],
        system_prompt="You are a helpful email assistant for Leo. Always return a message to the user confirming the action taken.",
        middleware=[HumanInTheLoopMiddleware(interrupt_on={"send_email": {"allowed_decisions": ["approve", "reject", "edit"]}})],
        checkpointer=st.session_state["checkpointer"],
    )

st.title("🦜🔗 Email Assistant")

# Create session state parameters
st.session_state.history = st.session_state.get("history", [])
st.session_state.stage = st.session_state.get("stage", "input")
st.session_state.agent_responses = st.session_state.get("agent_responses", [])
#st.session_state["email"] = st.session_state.get("email", {"recipient": "", "subject": "", "body": ""})
# ensure there's always an 'email' dict in session_state
st.session_state.setdefault("email", {"recipient": "", "subject": "", "body": ""})

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
    if "__interrupt__" in agent_response:
        action_request = agent_response['__interrupt__'][-1].value['action_requests'][-1]
        recipient = action_request['args']['recipient']
        subject = action_request['args']['subject']
        body = action_request['args']['body']
        agent_response_message = f"**To:** {recipient}\n\n**Subject:** {subject}\n\n**Body:**\n\n{body}"
        st.session_state.stage = "intervention"

        st.session_state["email"] = {
            "recipient": recipient,
            "subject": subject,
            "body": body,
        }
    
    st.session_state.history.append({"role": "assistant", "content": agent_response_message})
    st.session_state.agent_responses = agent_response
    st.rerun()

if "__interrupt__" in st.session_state.agent_responses and st.session_state.stage == "intervention":
    # Extract initial AI message requiring human intervention
    description = st.session_state.agent_responses['__interrupt__'][-1].value['action_requests'][-1]
    st.warning(f"Human intervention required for tool: {description['name']}")

    buttons = st.columns(6)
    with buttons[0]:
        if st.button("Approve", key="approve", type="primary", width="stretch", help="Approve the email"):
            agent = st.session_state["agent"]
            result = agent.invoke(
                Command(
                    resume=decisions.get("approve")
                ),
                config=st.session_state.memory_config
            )
            st.session_state.history.append({"role": "assistant", "content": result["messages"][-1].content})
            st.session_state.stage = "input"
            st.session_state["agent_responses"] = result
            st.rerun()

    with buttons[1]:
        if st.button("Reject", key="reject", type="secondary", width="stretch", help="Reject the email"):
            agent = st.session_state["agent"]
            result = agent.invoke(
                Command(
                    resume=decisions.get("reject")
                ),
                config=st.session_state.memory_config
            )
            st.session_state.history.append({"role": "assistant", "content": result["messages"][-1].content})
            st.session_state.stage = "input"
            st.rerun()

    with buttons[2]:
        if st.button("Edit", key="edit", type="secondary", width="stretch", help="Edit the email"):
            st.session_state["email_edited"] = False
            edit_email()

        # Only proceed if user actually confirmed the edit
        if st.session_state.get("email_edited"):
            agent = st.session_state["agent"]
            result = agent.invoke(
                Command(
                    resume = {
                        "decisions": [
                            {
                                "type": "edit",
                                "edited_action": {
                                    "name": "send_email",
                                    "args": st.session_state["email"]
                                }
                            }
                        ]
                    }),
                config=st.session_state.memory_config 
            )
            st.session_state.history.append({"role": "assistant", "content": result["messages"][-1].content})
            st.session_state.stage = "input"
            st.success("Email edited and sent!")

            st.session_state["agent_responses"] = result

            st.rerun()

st.write(st.session_state["agent_responses"])