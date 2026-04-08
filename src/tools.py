import json
from langchain_core.tools import tool
from src.contacts import search_contacts


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


@tool()
def lookup_contacts(query: str) -> str:
    """Search the contact directory for people to email.

    Use this tool to find a recipient's email address and background context
    before drafting an email. Search by name, company, role, or topic.

    Args:
        query: Name, company, role, or topic to search for (e.g. "finance", "Alice", "legal").
    Returns:
        Matching contacts with name, email, role, company, and context. Returns a message
        if no contacts are found.
    """
    results = search_contacts(query)
    if not results:
        return f"No contacts found matching '{query}'."
    return json.dumps(results, indent=2)
