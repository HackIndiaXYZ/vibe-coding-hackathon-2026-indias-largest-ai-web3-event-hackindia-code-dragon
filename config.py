import os

# -----------------------------------------------------------------------------
# CORE SYSTEM CONFIGURATION
# -----------------------------------------------------------------------------
# This file holds all central configurations for the NatsukiXRen protocol.
# Adjusting these parameters will fundamentally alter how the dual-core 
# system operates, its memory retention capabilities, and its intelligence.

# [API Configuration]
# The primary API key used to authenticate with the Groq Inference Engine.
# WARNING: Keep this secure. Use environment variables in production.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# [Model Configuration]
# Defines which underlying Language Model powers the dual-core identities.
# Recommended: 'llama3-70b-8192' for maximum reasoning and 15+ coding language support.
# Alternative: 'mixtral-8x7b-32768' for ultra-long context windows.
MODEL_NAME = "llama-3.3-70b-versatile"

# [Server Configuration]
# Flask server settings - configured for local and cloud (Render) environments.
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# [Memory Configuration]
# Location of the persistent JSON datastore.
# This file maintains the lifecycle of all conversational data, ensuring
# that Natsuki and Ren possess long-term memory across reboots.
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
SYSTEM_LOG_FILE = os.path.join(LOGS_DIR, "natsukixren_core.log")

# Initialization logic
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
