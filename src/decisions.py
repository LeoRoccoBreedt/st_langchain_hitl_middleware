approval = {
    "decisions": [
        {
            "type": "approve"
        }
    ]
}

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

reject = {
    "decisions": [
        {
            "type": "reject",
            "message": "Do not send an email. The email needs more context or additionans from the user."
        }
    ]
}

decisions = {
    "approve": approval,
    "edit": edit,
    "reject": reject,
}
