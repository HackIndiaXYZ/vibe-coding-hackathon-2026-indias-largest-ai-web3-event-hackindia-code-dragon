import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


MODEL_NAME = "llama-3.3-70b-versatile"

# [Server Configuration]
# Flask server settings - configured for local and cloud (Render) environments.
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# [Memory Configuration]
# Location of the persistent JSON datastore.
# This file maintains the lifecycle of all conversational data, ensuring
# that Ren possesses long-term memory across reboots.
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "data")
MEMORY_FILE = os.path.join(MEMORY_DIR, "system_memory.json")

# Number of past messages to inject into the active context window.
# Higher values increase conversational awareness but consume more tokens.
CONTEXT_WINDOW_SIZE = 25

# Max turns before old memories are compressed (simulated)
MAX_MEMORY_TURNS = 100

# [System Logistics]
# Paths for logging and analytics
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
SYSTEM_LOG_FILE = os.path.join(LOGS_DIR, "ren_core.log")

# Initialization logic
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
