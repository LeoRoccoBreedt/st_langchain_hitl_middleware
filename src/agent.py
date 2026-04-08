from langchain_core.language_models import BaseChatModel
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware

from src.tools import lookup_contacts, send_email


def create_email_agent(llm: BaseChatModel, checkpointer):
    """Create the email assistant agent with HITL middleware.

    Args:
        llm: A LangChain chat model (from src.llm.get_llm).
        checkpointer: A LangGraph checkpointer (e.g. InMemorySaver).

    Returns:
        A compiled LangGraph agent ready to invoke.
    """
    return create_agent(
        model=llm,
        tools=[lookup_contacts, send_email],
        system_prompt=(
            "You are a helpful email assistant. "
            "You have access to a contact directory — use the lookup_contacts tool "
            "to find recipients and relevant context before drafting emails. "
            "Always return a message to the user confirming the action taken."
        ),
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={"send_email": {"allowed_decisions": ["approve", "reject", "edit"]}}
            )
        ],
        checkpointer=checkpointer,
    )
