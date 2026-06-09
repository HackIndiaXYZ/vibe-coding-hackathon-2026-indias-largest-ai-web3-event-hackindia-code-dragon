import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import config
from memory import MemoryManager
from engine_gemini import GeminiInferenceEngine  # Changed from GroqInferenceEngine
from firebase_handler import FirebaseHandler

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
    inference_engine = GeminiInferenceEngine()  # Changed to Gemini
    print("[SYS] Memory subsystem and Inference Engine online.")
except Exception as e:
    print(f"[SYS_ERR] Failed to initialize core subsystems: {e}")
    sys.exit(1)

# Initialize Firebase Admin if configured
db = None
firebase_handler = None
if FIREBASE_AVAILABLE and getattr(config, 'FIREBASE_SERVICE_ACCOUNT', None):
    try:
        cred = credentials.Certificate(config.FIREBASE_SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred)
        db = firebase_firestore.client()
        firebase_handler = FirebaseHandler(db)
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
        "engine": "Gemini",
        "model": config.GEMINI_MODEL
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
        
        # Gemini API is handled by the engine, no need to check here
        
        if not user_message:
            return jsonify({"error": "Message payload empty."}), 400

        # Resolve Session & Store User Input (local memory)
        session_id = memory_sys.initialize_session(session_id)
        memory_sys.add_message(session_id, "user", user_message)

        # Mirror to Firestore (if available and authenticated)
        try:
            if db is not None and uid:
                sess_ref = db.collection('sessions').document(session_id)
                sess_ref.set({
                    'owner': uid,
                    'last_updated': firebase_firestore.SERVER_TIMESTAMP
                }, merge=True)
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
        final_reply = inference_engine.generate_response(active_mode, context_window, settings=settings)

        # Store AI Output
        memory_sys.add_message(session_id, "assistant", final_reply)

        # Mirror assistant reply to Firestore
        try:
            if db is not None and uid:
                sess_ref = db.collection('sessions').document(session_id)
                sess_ref.set({'last_updated': firebase_firestore.SERVER_TIMESTAMP}, merge=True)
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



# ==================== NEW ENDPOINTS FOR FEATURES ====================

def get_uid_from_token():
    """Helper to extract UID from auth header"""
    if not FIREBASE_AVAILABLE or db is None:
        return None
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    id_token = auth_header.split(' ', 1)[1]
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded.get('uid')
    except Exception:
        return None


# ============ DASHBOARD ============
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = firebase_handler.get_dashboard_stats(uid)
    return jsonify(stats)


# ============ STUDY HUB ============
@app.route('/api/notes', methods=['POST'])
def create_note():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    note_id = firebase_handler.create_note(uid, {
        'title': data.get('title'),
        'content': data.get('content'),
        'subject': data.get('subject')
    })
    return jsonify({'id': note_id, 'success': True})


@app.route('/api/notes', methods=['GET'])
def get_notes():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    notes = firebase_handler.get_notes(uid)
    return jsonify({'notes': notes})


@app.route('/api/quizzes', methods=['POST'])
def create_quiz():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    quiz_id = firebase_handler.create_quiz(uid, {
        'title': data.get('title'),
        'questions': data.get('questions', []),
        'subject': data.get('subject')
    })
    return jsonify({'id': quiz_id, 'success': True})


@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    quizzes = firebase_handler.get_quizzes(uid)
    return jsonify({'quizzes': quizzes})


@app.route('/api/quizzes/<quiz_id>/complete', methods=['POST'])
def complete_quiz(quiz_id):
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    firebase_handler.complete_quiz(uid, quiz_id, data.get('score', 0))
    return jsonify({'success': True})


@app.route('/api/flashcards', methods=['POST'])
def create_flashcard():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    card_id = firebase_handler.create_flashcard(uid, {
        'question': data.get('question'),
        'answer': data.get('answer'),
        'category': data.get('category')
    })
    return jsonify({'id': card_id, 'success': True})


@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    cards = firebase_handler.get_flashcards(uid)
    return jsonify({'flashcards': cards})


@app.route('/api/study-plans', methods=['POST'])
def create_study_plan():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    plan_id = firebase_handler.create_study_plan(uid, {
        'title': data.get('title'),
        'schedule': data.get('schedule'),
        'duration': data.get('duration')
    })
    return jsonify({'id': plan_id, 'success': True})


@app.route('/api/study-plans', methods=['GET'])
def get_study_plans():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    plans = firebase_handler.get_study_plans(uid)
    return jsonify({'plans': plans})


# ============ CODE HUB ============
@app.route('/api/code-snippets', methods=['POST'])
def save_code_snippet():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    snippet_id = firebase_handler.save_generated_code(uid, {
        'language': data.get('language'),
        'code': data.get('code'),
        'description': data.get('description')
    })
    return jsonify({'id': snippet_id, 'success': True})


@app.route('/api/code-snippets', methods=['GET'])
def get_code_snippets():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    snippets = firebase_handler.get_code_snippets(uid)
    return jsonify({'snippets': snippets})


# ============ AI TOOLS ============
@app.route('/api/analyze-image', methods=['POST'])
def analyze_image_tool():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400
    
    f = request.files['file']
    filename = f.filename or 'image'
    path = os.path.join(UPLOAD_DIR, f'{uid}_{int(time.time())}_{filename}')
    f.save(path)
    
    try:
        caption = inference_engine.analyze_image(path)
    except Exception:
        caption = 'Image received. Analysis unavailable.'
    
    analysis_id = firebase_handler.save_image_analysis(uid, {
        'image_path': path,
        'analysis': caption
    })
    return jsonify({'id': analysis_id, 'analysis': caption, 'success': True})


@app.route('/api/ocr', methods=['POST'])
def ocr_tool():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400
    
    f = request.files['file']
    filename = f.filename or 'image'
    path = os.path.join(UPLOAD_DIR, f'{uid}_{int(time.time())}_{filename}')
    f.save(path)
    
    try:
        text = inference_engine.extract_text_from_image(path)
    except Exception:
        text = 'OCR unavailable.'
    
    ocr_id = firebase_handler.save_ocr_result(uid, {
        'image_path': path,
        'extracted_text': text
    })
    return jsonify({'id': ocr_id, 'text': text, 'success': True})


@app.route('/api/resume-review', methods=['POST'])
def review_resume():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    resume_text = data.get('resume', '')
    
    try:
        feedback = inference_engine.review_resume(resume_text)
    except Exception:
        feedback = 'Resume review unavailable.'
    
    review_id = firebase_handler.save_resume_review(uid, {
        'resume': resume_text,
        'feedback': feedback
    })
    return jsonify({'id': review_id, 'feedback': feedback, 'success': True})


@app.route('/api/pdf-summary', methods=['POST'])
def summarize_pdf():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    pdf_content = data.get('content', '')
    
    try:
        summary = inference_engine.summarize_pdf(pdf_content)
    except Exception:
        summary = 'PDF summary unavailable.'
    
    summary_id = firebase_handler.save_pdf_summary(uid, {
        'pdf_content': pdf_content,
        'summary': summary
    })
    return jsonify({'id': summary_id, 'summary': summary, 'success': True})


# ============ COMMUNITY ============
@app.route('/api/share-chat', methods=['POST'])
def share_chat():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    chat_id = firebase_handler.share_chat(uid, {
        'title': data.get('title'),
        'messages': data.get('messages'),
        'description': data.get('description')
    })
    return jsonify({'id': chat_id, 'success': True})


@app.route('/api/shared-chats', methods=['GET'])
def get_shared_chats():
    if not firebase_handler:
        return jsonify({'error': 'Firebase unavailable'}), 500
    
    chats = firebase_handler.get_shared_chats()
    return jsonify({'chats': chats})


@app.route('/api/prompts', methods=['POST'])
def create_public_prompt():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    prompt_id = firebase_handler.create_prompt(uid, {
        'title': data.get('title'),
        'content': data.get('content'),
        'category': data.get('category')
    })
    return jsonify({'id': prompt_id, 'success': True})


@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    if not firebase_handler:
        return jsonify({'error': 'Firebase unavailable'}), 500
    
    prompts = firebase_handler.get_prompts()
    return jsonify({'prompts': prompts})


@app.route('/api/marketplace', methods=['POST'])
def add_marketplace_item():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    item_id = firebase_handler.add_marketplace_listing(uid, {
        'title': data.get('title'),
        'description': data.get('description'),
        'price': data.get('price'),
        'category': data.get('category')
    })
    return jsonify({'id': item_id, 'success': True})


@app.route('/api/marketplace', methods=['GET'])
def get_marketplace():
    if not firebase_handler:
        return jsonify({'error': 'Firebase unavailable'}), 500
    
    items = firebase_handler.get_marketplace()
    return jsonify({'items': items})


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    if not firebase_handler:
        return jsonify({'error': 'Firebase unavailable'}), 500
    
    limit = request.args.get('limit', 50, type=int)
    leaderboard = firebase_handler.get_leaderboard(limit)
    return jsonify({'leaderboard': leaderboard})


# ============ GAMIFICATION ============
@app.route('/api/user/xp', methods=['POST'])
def add_user_xp():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    xp_amount = data.get('xp', 0)
    leveled_up = firebase_handler.add_xp(uid, xp_amount)
    user = firebase_handler.get_user(uid)
    
    return jsonify({
        'success': True,
        'xp': user.get('xp'),
        'level': user.get('level'),
        'leveled_up': leveled_up
    })


@app.route('/api/user/badge', methods=['POST'])
def add_user_badge():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    badge_name = data.get('badge')
    firebase_handler.add_badge(uid, badge_name)
    user = firebase_handler.get_user(uid)
    
    return jsonify({'success': True, 'badges': user.get('badges', [])})


@app.route('/api/daily-challenges', methods=['POST'])
def create_daily_challenge():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    challenge_id = firebase_handler.create_daily_challenge(uid, {
        'title': data.get('title'),
        'description': data.get('description'),
        'reward_xp': data.get('reward_xp', 50)
    })
    return jsonify({'id': challenge_id, 'success': True})


@app.route('/api/daily-challenges', methods=['GET'])
def get_daily_challenges():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    challenges = firebase_handler.get_daily_challenges(uid)
    return jsonify({'challenges': challenges})


@app.route('/api/daily-challenges/<challenge_id>/complete', methods=['POST'])
def complete_daily_challenge(challenge_id):
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    firebase_handler.complete_challenge(uid, challenge_id)
    return jsonify({'success': True})


@app.route('/api/config/firebase', methods=['GET'])
def get_firebase_config():
    """Serve Firebase public config safely from environment variables"""
    import os
    from dotenv import load_dotenv
    
    # Load from .env file
    load_dotenv()
    
    firebase_config = {
        'apiKey': os.getenv('FIREBASE_API_KEY', ''),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': os.getenv('FIREBASE_PROJECT_ID', ''),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', ''),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': os.getenv('FIREBASE_APP_ID', ''),
        'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID', '')
    }
    
    # Validate config is present
    if not firebase_config['apiKey']:
        return jsonify({'error': 'Firebase not configured'}), 500
    
    return jsonify(firebase_config)


@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401

    session_id = request.args.get('session_id')
    session_ref = None

    if session_id:
        session_ref = db.collection('sessions').document(session_id)
        session_doc = session_ref.get()
        if not session_doc.exists:
            return jsonify({'error': 'Session not found'}), 404
        if session_doc.to_dict().get('owner') != uid:
            return jsonify({'error': 'Unauthorized session access'}), 403
    else:
        sessions = db.collection('sessions')\
            .where('owner', '==', uid)\
            .order_by('last_updated', direction=firebase_firestore.Query.DESCENDING)\
            .limit(1)\
            .stream()
        session_doc = next(iter(sessions), None)
        if not session_doc:
            return jsonify({'session_id': None, 'messages': []})
        session_id = session_doc.id
        session_ref = db.collection('sessions').document(session_id)

    messages_query = session_ref.collection('messages').order_by('timestamp', direction=firebase_firestore.Query.ASCENDING).stream()
    messages = []
    for doc in messages_query:
        msg = doc.to_dict() or {}
        messages.append({
            'id': doc.id,
            'sender': msg.get('sender'),
            'text': msg.get('text', ''),
            'timestamp': msg.get('timestamp')
        })

    return jsonify({'session_id': session_id, 'messages': messages})

if __name__ == '__main__':
    print(f"\n===========================================")
    print(f" REN - THE TECHNICAL TUTOR & CORE MATRIX")
    print(f"===========================================")
    print(f" Port: {config.PORT}")
    print(f" Debug: {config.DEBUG_MODE}")
    print(f" Model: {config.GEMINI_MODEL}")
    print(f"===========================================\n")
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG_MODE)
