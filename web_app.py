import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import config
from memory import MemoryManager
from engine import GroqInferenceEngine

# Firebase admin (optional - configured via config.FIREBASE_SERVICE_ACCOUNT)
try:
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth, firestore as firebase_firestore
    FIREBASE_AVAILABLE = True
except Exception:
    FIREBASE_AVAILABLE = False


app = Flask(__name__)
CORS(app)

import os
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)
import time


print("[SYS] Bootstrapping Ren Technical Mentor Core...")
try:
    memory_sys = MemoryManager()
    inference_engine = GroqInferenceEngine()
    print("[SYS] Memory subsystem and Inference Engine online.")
except Exception as e:
    print(f"[SYS_ERR] Failed to initialize core subsystems: {e}")
    sys.exit(1)

# Initialize Firebase Admin if configured
db = None
if FIREBASE_AVAILABLE and getattr(config, 'FIREBASE_SERVICE_ACCOUNT', None):
    try:
        cred = credentials.Certificate(config.FIREBASE_SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred)
        db = firebase_firestore.client()
        print('[SYS] Firebase Admin initialized.')
    except Exception as e:
        print(f'[SYS_ERR] Firebase Admin init failed: {e}')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

@app.route('/')
def index():
 
    return send_from_directory('.', 'index.html')

@app.route('/api/status', methods=['GET'])
def health_check():
 
    return jsonify({
        "status": "ONLINE",
        "protocol": "RenCore",
        "engine": "Groq",
        "model": config.MODEL_NAME
    })

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
   
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        mode = data.get('mode', 'auto')
        session_id = data.get('session_id')
        # Verify Firebase ID token if present
        uid = None
        if FIREBASE_AVAILABLE and db is not None:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split(' ', 1)[1]
                try:
                    decoded = firebase_auth.verify_id_token(id_token)
                    uid = decoded.get('uid')
                except Exception as e:
                    # Token invalid - respond 401
                    return jsonify({'error': 'Invalid or expired auth token.'}), 401
        
        api_key = config.GROQ_API_KEY
        if not api_key:
            return jsonify({"error": "Server not configured with GROQ_API_KEY."}), 500

        if not user_message:
            return jsonify({"error": "Message payload empty."}), 400

        # Resolve Session & Store User Input (local memory)
        session_id = memory_sys.initialize_session(session_id)
        memory_sys.add_message(session_id, "user", user_message)

        # Mirror to Firestore (if available and authenticated)
        try:
            if db is not None and uid:
                sess_ref = db.collection('sessions').document(session_id)
                sess_ref.set({'owner': uid}, merge=True)
                msgs = sess_ref.collection('messages')
                msgs.add({
                    'sender': 'user',
                    'text': user_message,
                    'timestamp': firebase_firestore.SERVER_TIMESTAMP,
                    'status': 'sent'
                })
        except Exception as e:
            logging.warning(f'Failed to write message to Firestore: {e}')

        # Mode Routing Logic
        active_mode = mode
        # Logic moved to personas.py for smart routing
            
        logging.info(f"Incoming Request -> Session: {session_id} | Mode: {active_mode}")

        # Fetch Context Window
        context_window = memory_sys.get_context_window(session_id)

        # Execute Inference Sequence
        settings = data.get('settings', {})
        final_reply = inference_engine.generate_response(active_mode, context_window, api_key=api_key, settings=settings)

        # Store AI Output
        memory_sys.add_message(session_id, "assistant", final_reply)

        # Mirror assistant reply to Firestore
        try:
            if db is not None and uid:
                sess_ref = db.collection('sessions').document(session_id)
                msgs = sess_ref.collection('messages')
                msgs.add({
                    'sender': 'ren',
                    'text': final_reply,
                    'timestamp': firebase_firestore.SERVER_TIMESTAMP,
                    'status': 'sent'
                })
        except Exception as e:
            logging.warning(f'Failed to write assistant reply to Firestore: {e}')
        
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


@app.route('/api/upload_pdf', methods=['POST'])
def upload_pdf():
    # Accept a PDF file, verify user, save, and return document id
    uid = None
    if FIREBASE_AVAILABLE and db is not None:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            id_token = auth_header.split(' ', 1)[1]
            try:
                decoded = firebase_auth.verify_id_token(id_token)
                uid = decoded.get('uid')
            except Exception:
                return jsonify({'error': 'Invalid auth token.'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400
    f = request.files['file']
    filename = f.filename or 'upload.pdf'
    safe_name = f'{uid or "anon"}_{int(time.time())}_{filename}'
    path = os.path.join(UPLOAD_DIR, safe_name)
    f.save(path)
    # TODO: enqueue document processing (OCR, embeddings)
    return jsonify({'ok': True, 'file': safe_name})


@app.route('/api/analyze_image', methods=['POST'])
def analyze_image():
    # Placeholder: accept image, save and return a simple caption via engine
    uid = None
    if FIREBASE_AVAILABLE and db is not None:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            id_token = auth_header.split(' ', 1)[1]
            try:
                decoded = firebase_auth.verify_id_token(id_token)
                uid = decoded.get('uid')
            except Exception:
                return jsonify({'error': 'Invalid auth token.'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400
    f = request.files['file']
    filename = f.filename or 'image'
    path = os.path.join(UPLOAD_DIR, f'{uid or "anon"}_{int(time.time())}_{filename}')
    f.save(path)
    # Here you would call an image analysis model; we'll call inference_engine for placeholder
    try:
        caption = inference_engine.analyze_image(path)
    except Exception:
        caption = 'Image received. Analysis unavailable.'
    return jsonify({'ok': True, 'caption': caption})


@app.route('/api/upload_voice', methods=['POST'])
def upload_voice():
    # Save voice file and optionally transcribe
    uid = None
    if FIREBASE_AVAILABLE and db is not None:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            id_token = auth_header.split(' ', 1)[1]
            try:
                decoded = firebase_auth.verify_id_token(id_token)
                uid = decoded.get('uid')
            except Exception:
                return jsonify({'error': 'Invalid auth token.'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400
    f = request.files['file']
    filename = f.filename or 'voice.webm'
    path = os.path.join(UPLOAD_DIR, f'{uid or "anon"}_{int(time.time())}_{filename}')
    f.save(path)
    # Placeholder: call engine.transcribe_audio(path)
    try:
        text = inference_engine.transcribe_audio(path)
    except Exception:
        text = ''
    return jsonify({'ok': True, 'transcript': text})

if __name__ == '__main__':
    print(f"\n===========================================")
    print(f" REN - THE TECHNICAL TUTOR & CORE MATRIX")
    print(f"===========================================")
    print(f" Port: {config.PORT}")
    print(f" Debug: {config.DEBUG_MODE}")
    print(f" Model: {config.MODEL_NAME}")
    print(f"===========================================\n")
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG_MODE)
