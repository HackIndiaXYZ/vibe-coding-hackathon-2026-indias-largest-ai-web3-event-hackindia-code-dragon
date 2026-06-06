"""
Firebase Handler - All data operations for Natsuki-Ren AI System
Manages: Users, Chats, Study Materials, Community, Gamification
"""

from firebase_admin import firestore
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FirebaseHandler:
    def __init__(self, db):
        """Initialize Firebase handler with Firestore client"""
        self.db = db
    
    # ============ USER PROFILE ============
    def create_user(self, uid, user_data):
        """Create user profile"""
        user_data['created_at'] = firestore.SERVER_TIMESTAMP
        user_data['updated_at'] = firestore.SERVER_TIMESTAMP
        user_data['xp'] = 0
        user_data['level'] = 1
        user_data['streak'] = 0
        user_data['badges'] = []
        self.db.collection('users').document(uid).set(user_data)
        return uid
    
    def get_user(self, uid):
        """Get user profile"""
        doc = self.db.collection('users').document(uid).get()
        return doc.to_dict() if doc.exists else None
    
    def update_user_stats(self, uid, stats):
        """Update user XP, level, streak"""
        stats['updated_at'] = firestore.SERVER_TIMESTAMP
        self.db.collection('users').document(uid).set(stats, merge=True)
    
    # ============ DASHBOARD STATS ============
    def add_chat_message(self, uid, message_data):
        """Add message to chat and update stats"""
        # Add message
        self.db.collection('users').document(uid).collection('messages').add({
            'text': message_data.get('text'),
            'sender': message_data.get('sender'),  # 'user' or 'ren'
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Update message count
        user = self.get_user(uid)
        messages_sent = user.get('messages_sent', 0) + 1
        self.update_user_stats(uid, {'messages_sent': messages_sent})
    
    def get_dashboard_stats(self, uid):
        """Get user dashboard stats"""
        user = self.get_user(uid)
        if not user:
            return None
        
        messages = self.db.collection('users').document(uid).collection('messages').stream()
        total_chats = len([m for m in messages])
        
        return {
            'total_chats': total_chats,
            'messages_sent': user.get('messages_sent', 0),
            'daily_streak': user.get('streak', 0),
            'ai_usage': user.get('ai_usage', 0),
            'level': user.get('level', 1),
            'xp': user.get('xp', 0)
        }
    
    # ============ STUDY HUB ============
    def create_note(self, uid, note_data):
        """Create study note"""
        note_data['created_at'] = firestore.SERVER_TIMESTAMP
        note_data['updated_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('users').document(uid).collection('study_notes').add(note_data)
        return ref[1].id
    
    def get_notes(self, uid):
        """Get all study notes for user"""
        docs = self.db.collection('users').document(uid).collection('study_notes').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def create_quiz(self, uid, quiz_data):
        """Create quiz"""
        quiz_data['created_at'] = firestore.SERVER_TIMESTAMP
        quiz_data['completed'] = False
        ref = self.db.collection('users').document(uid).collection('quizzes').add(quiz_data)
        return ref[1].id
    
    def get_quizzes(self, uid):
        """Get all quizzes"""
        docs = self.db.collection('users').document(uid).collection('quizzes').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def complete_quiz(self, uid, quiz_id, score):
        """Mark quiz as completed"""
        self.db.collection('users').document(uid).collection('quizzes').document(quiz_id).update({
            'completed': True,
            'score': score,
            'completed_at': firestore.SERVER_TIMESTAMP
        })
        # Award XP
        self.add_xp(uid, score * 10)
    
    def create_flashcard(self, uid, flashcard_data):
        """Create flashcard"""
        flashcard_data['created_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('users').document(uid).collection('flashcards').add(flashcard_data)
        return ref[1].id
    
    def get_flashcards(self, uid):
        """Get all flashcards"""
        docs = self.db.collection('users').document(uid).collection('flashcards').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def create_study_plan(self, uid, plan_data):
        """Create study plan"""
        plan_data['created_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('users').document(uid).collection('study_plans').add(plan_data)
        return ref[1].id
    
    def get_study_plans(self, uid):
        """Get all study plans"""
        docs = self.db.collection('users').document(uid).collection('study_plans').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    # ============ CODE HUB ============
    def save_generated_code(self, uid, code_data):
        """Save generated code snippet"""
        code_data['created_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('users').document(uid).collection('code_snippets').add(code_data)
        return ref[1].id
    
    def get_code_snippets(self, uid):
        """Get all code snippets"""
        docs = self.db.collection('users').document(uid).collection('code_snippets').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    # ============ AI TOOLS ============
    def save_image_analysis(self, uid, analysis_data):
        """Save image analysis result"""
        analysis_data['created_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('users').document(uid).collection('image_analyses').add(analysis_data)
        return ref[1].id
    
    def save_ocr_result(self, uid, ocr_data):
        """Save OCR result"""
        ocr_data['created_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('users').document(uid).collection('ocr_results').add(ocr_data)
        return ref[1].id
    
    def save_resume_review(self, uid, review_data):
        """Save resume review"""
        review_data['created_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('users').document(uid).collection('resume_reviews').add(review_data)
        return ref[1].id
    
    def save_pdf_summary(self, uid, summary_data):
        """Save PDF summary"""
        summary_data['created_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('users').document(uid).collection('pdf_summaries').add(summary_data)
        return ref[1].id
    
    # ============ COMMUNITY ============
    def share_chat(self, uid, chat_data):
        """Share chat publicly"""
        chat_data['shared_by'] = uid
        chat_data['created_at'] = firestore.SERVER_TIMESTAMP
        chat_data['likes'] = 0
        ref = self.db.collection('community_chats').add(chat_data)
        return ref[1].id
    
    def get_shared_chats(self):
        """Get all shared chats"""
        docs = self.db.collection('community_chats').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def create_prompt(self, uid, prompt_data):
        """Create public prompt"""
        prompt_data['created_by'] = uid
        prompt_data['created_at'] = firestore.SERVER_TIMESTAMP
        prompt_data['uses'] = 0
        ref = self.db.collection('prompts').add(prompt_data)
        return ref[1].id
    
    def get_prompts(self):
        """Get all public prompts"""
        docs = self.db.collection('prompts').order_by('uses', direction=firestore.Query.DESCENDING).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def add_marketplace_listing(self, uid, listing_data):
        """Add to marketplace"""
        listing_data['seller'] = uid
        listing_data['created_at'] = firestore.SERVER_TIMESTAMP
        ref = self.db.collection('marketplace').add(listing_data)
        return ref[1].id
    
    def get_marketplace(self):
        """Get marketplace listings"""
        docs = self.db.collection('marketplace').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def get_leaderboard(self, limit=50):
        """Get leaderboard by XP"""
        docs = self.db.collection('users').order_by('xp', direction=firestore.Query.DESCENDING).limit(limit).stream()
        return [{'uid': doc.id, **doc.to_dict()} for doc in docs]
    
    # ============ GAMIFICATION ============
    def add_xp(self, uid, xp_amount):
        """Add XP to user and handle level up"""
        user = self.get_user(uid)
        current_xp = user.get('xp', 0)
        current_level = user.get('level', 1)
        new_xp = current_xp + xp_amount
        new_level = current_level + (new_xp // 1000)  # 1000 XP per level
        
        self.update_user_stats(uid, {
            'xp': new_xp,
            'level': new_level
        })
        return new_level > current_level
    
    def add_badge(self, uid, badge_name):
        """Add badge to user"""
        user = self.get_user(uid)
        badges = user.get('badges', [])
        if badge_name not in badges:
            badges.append(badge_name)
            self.update_user_stats(uid, {'badges': badges})
    
    def update_streak(self, uid, days=1):
        """Update daily streak"""
        user = self.get_user(uid)
        current_streak = user.get('streak', 0)
        new_streak = current_streak + days
        self.update_user_stats(uid, {'streak': new_streak})
    
    def create_daily_challenge(self, uid, challenge_data):
        """Create daily challenge"""
        challenge_data['created_at'] = firestore.SERVER_TIMESTAMP
        challenge_data['completed'] = False
        ref = self.db.collection('users').document(uid).collection('daily_challenges').add(challenge_data)
        return ref[1].id
    
    def complete_challenge(self, uid, challenge_id):
        """Complete daily challenge"""
        self.db.collection('users').document(uid).collection('daily_challenges').document(challenge_id).update({
            'completed': True,
            'completed_at': firestore.SERVER_TIMESTAMP
        })
        # Award XP and update streak
        self.add_xp(uid, 50)
        self.update_streak(uid)
    
    def get_daily_challenges(self, uid):
        """Get daily challenges"""
        docs = self.db.collection('users').document(uid).collection('daily_challenges').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
