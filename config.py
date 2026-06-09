import os
from dotenv import load_dotenv

load_dotenv()

# ========== GEMINI AI CONFIG ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"  # Primary AI model (stable)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# ========== FIREBASE CONFIG ==========
FIREBASE_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# [Server Configuration]
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# [Memory Configuration]
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "data")
MEMORY_FILE = os.path.join(MEMORY_DIR, "system_memory.json")

CONTEXT_WINDOW_SIZE = 25
MAX_MEMORY_TURNS = 100

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
SYSTEM_LOG_FILE = os.path.join(LOGS_DIR, "ren_core.log")

os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# [Firebase Configuration (Optional)]
# Set this to the path of your Firebase service account JSON file
# Download from: Firebase Console → Settings ⚙️ → Service Accounts → Generate New Private Key
FIREBASE_SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT", None)
# Example: FIREBASE_SERVICE_ACCOUNT = 'serviceAccount.json'