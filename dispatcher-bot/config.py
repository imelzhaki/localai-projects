import os

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

DEPARTMENTS = ["IT_SUPPORT", "HR", "FINANCE", "GENERAL"]

PRIORITIES = ["LOW", "MEDIUM", "HIGH", "URGENT"]

CATEGORIES = {
    "IT_SUPPORT": ["HARDWARE_FAILURE", "SOFTWARE_ISSUE", "NETWORK"],
    "HR": ["LEAVE_REQUEST", "PAYROLL", "ONBOARDING"],
    "FINANCE": ["INVOICE", "REIMBURSEMENT", "BUDGET"],
    "GENERAL": ["INQUIRY", "FEEDBACK"],
}

# department -> Telegram group chat_id (fill in real IDs before running)
DEPARTMENT_GROUPS = {
    "IT_SUPPORT": int(os.environ.get("IT_SUPPORT_GROUP_ID", "0")),
    "HR": int(os.environ.get("HR_GROUP_ID", "0")),
    "FINANCE": int(os.environ.get("FINANCE_GROUP_ID", "0")),
    "GENERAL": int(os.environ.get("GENERAL_GROUP_ID", "0")),
}

ADMIN_GROUP_ID = int(os.environ.get("ADMIN_GROUP_ID", "0"))
