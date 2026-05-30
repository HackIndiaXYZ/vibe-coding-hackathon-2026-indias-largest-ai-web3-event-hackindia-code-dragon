import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import config
from memory import MemoryManager
from engine import GroqInferenceEngine

# -----------------------------------------------------------------------------
# REN - ELITE TECHNICAL MENTOR PROTOCOL
# -----------------------------------------------------------------------------
# Main Entry Point. 
# This module bootstraps the Flask application, wires up the REST endpoints,
# and coordinates the interactions between Memory, Engine, and UI.

app = Flask(__name__)
CORS(app)

# Initialize Core Subsystems
print("[SYS] Bootstrapping Ren Technical Mentor Core...")
try:
    memory_sys = MemoryManager()
    inference_engine = GroqInferenceEngine()
    print("[SYS] Memory subsystem and Inference Engine online.")
except Exception as e:
    print(f"[SYS_ERR] Failed to initialize core subsystems: {e}")
    sys.exit(1)

# Configure Logging (Stream only to prevent reloads)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

@app.route('/')
def index():
    """Serve the primary UI."""
    return send_from_directory('.', 'index.html')

@app.route('/api/status', methods=['GET'])
def health_check():
    """Diagnostic endpoint to verify subsystem status."""
    return jsonify({
        "status": "ONLINE",
        "protocol": "RenCore",
        "engine": "Groq",
        "model": config.MODEL_NAME
    })

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Primary communication endpoint.
    Expects JSON payload:
    {
      "message": "user text",
      "mode": "auto" | "ren",
      "session_id": "optional-uuid"
    }
    """
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        mode = data.get('mode', 'auto')
        session_id = data.get('session_id')
        
        # Support client-side API key override
        client_api_key = request.headers.get('X-Groq-API-Key')
        api_key = client_api_key if client_api_key else config.GROQ_API_KEY

        if not user_message:
            return jsonify({"error": "Message payload empty."}), 400

        # Resolve Session & Store User Input
        session_id = memory_sys.initialize_session(session_id)
        memory_sys.add_message(session_id, "user", user_message)

        # Mode Routing Logic
        active_mode = mode
        # Logic moved to personas.py for smart routing
            
        logging.info(f"Incoming Request -> Session: {session_id} | Mode: {active_mode}")

        # Fetch Context Window
        context_window = memory_sys.get_context_window(session_id)

        # Execute Inference Sequence
        final_reply = inference_engine.generate_response(active_mode, context_window, api_key=api_key)

        # Store AI Output
        memory_sys.add_message(session_id, "assistant", final_reply)
        
        # Fetch Updated Analytics
        stats = memory_sys.get_session_stats(session_id)

        logging.info(f"Inference Complete -> Generated {len(final_reply)} chars.")

        return jsonify({
            "reply": final_reply,
            "mode": active_mode,
            "session_id": session_id,
            "meta": {
                "memory": stats
            }
        })

    except Exception as e:
        error_msg = str(e)
        if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            return jsonify({"error": "Invalid API Key. Please update your configuration."}), 401
        
        logging.error(f"Critical Exception in /api/chat: {error_msg}", exc_info=True)
        return jsonify({"error": f"System Error: {error_msg}"}), 500

if __name__ == '__main__':
    print(f"\n===========================================")
    print(f" REN - THE TECHNICAL TUTOR & CORE MATRIX")
    print(f"===========================================")
    print(f" Port: {config.PORT}")
    print(f" Debug: {config.DEBUG_MODE}")
    print(f" Model: {config.MODEL_NAME}")
    print(f"===========================================\n")
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG_MODE)
