"""Fake contact directory mimicking a CRM / address book.

The `search_contacts` function is the single retrieval interface.
To plug in a real RAG system later, replace only that function — the
`lookup_contacts` tool and the rest of the app stay unchanged.
"""

CONTACTS: list[dict] = [
    {
        "name": "Alice Johnson",
        "email": "alice.johnson@acme.com",
        "company": "Acme Corp",
        "role": "Head of Finance",
        "context": (
            "Key budget decision-maker. Prefers concise, data-driven emails. "
            "Previously discussed Q1 2026 budget allocation and cost reduction targets."
        ),
    },
    {
        "name": "Ben Carter",
        "email": "ben.carter@acme.com",
        "company": "Acme Corp",
        "role": "VP of Engineering",
        "context": (
            "Oversees all engineering teams. Values technical precision. "
            "Currently leading the platform migration to cloud infrastructure."
        ),
    },
    {
        "name": "Clara Nguyen",
        "email": "clara.nguyen@partnercorp.io",
        "company": "PartnerCorp",
        "role": "Partnership Manager",
        "context": (
            "Primary contact for the joint go-to-market initiative. "
            "Prefers communication via email rather than calls. "
            "Awaiting updated contract terms from our legal team."
        ),
    },
    {
        "name": "David Osei",
        "email": "david.osei@investfirm.com",
        "company": "Invest Firm",
        "role": "Investment Analyst",
        "context": (
            "Handles due diligence for Series B. "
            "Requested a financial model update by end of Q1. "
            "Very responsive, usually replies within a few hours."
        ),
    },
    {
        "name": "Elena Rossi",
        "email": "elena.rossi@designstudio.co",
        "company": "Design Studio",
        "role": "Creative Director",
        "context": (
            "Managing the brand refresh project. "
            "Last discussion was about the new logo concepts and colour palette approval. "
            "Deadline for final assets is end of April."
        ),
    },
    {
        "name": "Frank Liu",
        "email": "frank.liu@acme.com",
        "company": "Acme Corp",
        "role": "Head of Sales",
        "context": (
            "Leads the enterprise sales team. "
            "Currently pushing to close two major deals before end of quarter. "
            "Needs updated pricing deck from product team."
        ),
    },
    {
        "name": "Grace Okafor",
        "email": "grace.okafor@legalco.com",
        "company": "LegalCo",
        "role": "Legal Counsel",
        "context": (
            "External legal advisor handling contractor agreements and NDAs. "
            "Currently reviewing the PartnerCorp contract. "
            "Prefers formal language in correspondence."
        ),
    },
    {
        "name": "Henry Blake",
        "email": "henry.blake@techpress.io",
        "company": "Tech Press",
        "role": "Journalist",
        "context": (
            "Covers B2B SaaS industry. "
            "Reached out previously about a product launch story. "
            "Any press-related emails should be approved by marketing first."
        ),
    },
    {
        "name": "Isla Fernandez",
        "email": "isla.fernandez@acme.com",
        "company": "Acme Corp",
        "role": "Product Manager",
        "context": (
            "Owns the roadmap for the core product. "
            "Coordinating with engineering and design on the Q2 feature release. "
            "Point of contact for all product feedback and prioritisation discussions."
        ),
    },
    {
        "name": "James Park",
        "email": "james.park@cloudvendor.com",
        "company": "Cloud Vendor",
        "role": "Account Executive",
        "context": (
            "Our main rep for cloud infrastructure contracts. "
            "Negotiating a volume discount renewal due in May. "
            "Has offered additional support credits if we commit early."
        ),
    },
]


def search_contacts(query: str) -> list[dict]:
    """Search the contact directory by keyword.

    Searches across name, email, company, role, and context fields.
    Case-insensitive. Returns all matching contacts.

    This function is the drop-in replacement point for a real RAG retriever —
    swap the body here without changing the tool or agent code.

    Args:
        query: Free-text search string.

    Returns:
        List of matching contact dicts. Empty list if no matches.
    """
    q = query.lower()
    return [
        c for c in CONTACTS
        if any(q in str(v).lower() for v in c.values())
    ]
