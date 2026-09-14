import json

def run_trivial_baseline(text):
    return {
        "intent": "general_inquiry",
        "escalate": True,
        "escalate_reason": "Always escalate to a human",
        "draft_reply": "Thanks for reaching out! Please DM us your account details so we can assist you."
    }

def run_simple_baseline(text):
    text_lower = text.lower()
    
    intent = "general_inquiry"
    if any(word in text_lower for word in ["password", "login", "account", "locked", "id"]):
        intent = "account_access"
    elif any(word in text_lower for word in ["charge", "bill", "refund", "subscription", "pay", "money"]):
        intent = "billing_subscription"
    elif any(word in text_lower for word in ["broken", "screen", "battery", "repair", "store"]):
        intent = "hardware_issue"
    elif any(word in text_lower for word in ["bug", "update", "ios", "crash", "app"]):
        intent = "software_bug"
    elif any(word in text_lower for word in ["terrible", "worst", "sucks", "hate", "lawyer"]):
        intent = "complaint_feedback"

    escalate = False
    escalate_reason = "Can be auto-handled"
    
    if intent in ["hardware_issue", "complaint_feedback"] or any(word in text_lower for word in ["sucks", "lawyer", "manager"]):
        escalate = True
        escalate_reason = "Requires human empathy or physical inspection"

    return {
        "intent": intent,
        "escalate": escalate,
        "escalate_reason": escalate_reason,
        "draft_reply": f"Hi there. We understand you are having an issue related to {intent}. Let's look into this."
    }
