# [GOAL] Natsuki-Ren AI System - COMPLETE FEATURE GUIDE

## [OK] What's Been Built

All 6 feature modules are now **fully functional** with Firebase integration:

---

## [BUILD] **ARCHITECTURE OVERVIEW**

```
Frontend (index.html + api.js)
         |
    Navigation UI
         |
Backend (web_app.py + firebase_handler.py)
         |
    Firebase Firestore
```

---

## [NOTES] **API ENDPOINTS & FEATURES**

### **1) DASHBOARD** [DASHBOARD]
Get user stats, messages, streaks, XP, level, AI usage

**Endpoint:** `GET /api/dashboard`

**Returns:**
```json
{
  "total_chats": 10,
  "messages_sent": 45,
  "daily_streak": 3,
  "ai_usage": 150,
  "level": 2,
  "xp": 450
}
```

---

### **2) STUDY HUB** [BOOKS]

#### **Study Notes**
```
POST /api/notes          -> Create note
GET  /api/notes          -> Get all notes
```

#### **Quizzes**
```
POST /api/quizzes                      -> Create quiz
GET  /api/quizzes                      -> Get all quizzes
POST /api/quizzes/{id}/complete        -> Mark complete (awards XP)
```

#### **Flashcards**
```
POST /api/flashcards     -> Create flashcard
GET  /api/flashcards     -> Get all flashcards
```

#### **Study Plans**
```
POST /api/study-plans    -> Create plan
GET  /api/study-plans    -> Get all plans
```

---

### **3) CODE HUB** [CODE]

#### **Code Snippets**
```
POST /api/code-snippets  -> Save code snippet
GET  /api/code-snippets  -> Get all snippets
```

**Example:**
```json
{
  "language": "python",
  "code": "def hello():\n    print('hello')",
  "description": "Simple hello function"
}
```

---

### **4) AI TOOLS** [TOOLS]

#### **Image Analysis**
```
POST /api/analyze-image  -> Upload & analyze image
```

#### **OCR (Text Extraction)**
```
POST /api/ocr            -> Extract text from image
```

#### **Resume Review**
```
POST /api/resume-review  -> Get feedback on resume
```

**Example:**
```json
{
  "resume": "John Doe\nSoftware Engineer at XYZ Corp..."
}
```

#### **PDF Summarizer**
```
POST /api/pdf-summary    -> Get PDF summary
```

---

### **5) COMMUNITY** [PEOPLE]

#### **Share Chats**
```
POST /api/share-chat     -> Share chat publicly
GET  /api/shared-chats   -> Get all shared chats
```

#### **Public Prompts**
```
POST /api/prompts        -> Create public prompt
GET  /api/prompts        -> Browse prompts (sorted by usage)
```

#### **Marketplace**
```
POST /api/marketplace    -> List item for sale
GET  /api/marketplace    -> Browse marketplace
```

#### **Leaderboard**
```
GET  /api/leaderboard?limit=50  -> Get top users by XP
```

**Returns:**
```json
{
  "leaderboard": [
    {"uid": "user123", "xp": 5000, "level": 5, "badges": [...]}
  ]
}
```

---

### **6) GAMIFICATION** [GAME]

#### **XP & Levels**
```
POST /api/user/xp        -> Add XP (auto level-up at 1000 XP)
```

**Example:**
```json
{
  "xp": 100,
  "success": true,
  "xp": 150,
  "level": 2,
  "leveled_up": true
}
```

#### **Badges**
```
POST /api/user/badge     -> Award badge
```

**Example:**
```json
{
  "badge": "Code_Warrior"
}
```

#### **Daily Challenges**
```
POST /api/daily-challenges                    -> Create challenge
GET  /api/daily-challenges                    -> Get challenges
POST /api/daily-challenges/{id}/complete      -> Complete challenge
```

---

## [ROCKET] **HOW TO USE**

### **1. Frontend Navigation**
Click tabs at top: [CHAT] Chat | [DASHBOARD] Dashboard | [BOOKS] Study | [CODE] Code | [TOOLS] Tools | [PEOPLE] Community | [GAME] Gamify

### **2. JavaScript API** (in browser console)
```javascript
// Dashboard
await window.NatsukiAPI.getDashboard()

// Study
await window.NatsukiAPI.createNote("Title", "Content", "Math")
await window.NatsukiAPI.getNotes()

// Gamification
await window.NatsukiAPI.addXP(100)
await window.NatsukiAPI.addBadge("Code_Warrior")

// Community
await window.NatsukiAPI.getLeaderboard(50)
```

### **3. Authentication**
Must be logged in with Firebase. The app automatically attaches `Authorization: Bearer {ID_TOKEN}` header.

---

## [FILES] **FIREBASE COLLECTIONS STRUCTURE**

```
users/
  └─ {uid}/
      ├─ name: string
      ├─ email: string
      ├─ level: number
      ├─ xp: number
      ├─ streak: number
      ├─ badges: array
      ├─ messages_sent: number
      ├─ ai_usage: number
      └─ created_at: timestamp
      
      messages/
      └─ (user messages for that session)
      
      study_notes/
      └─ {note_id}/
          ├─ title: string
          ├─ content: string
          ├─ subject: string
          ├─ created_at: timestamp
      
      quizzes/
      └─ {quiz_id}/
          ├─ title: string
          ├─ questions: array
          ├─ completed: boolean
          ├─ score: number
      
      flashcards/
      code_snippets/
      daily_challenges/
      ...

community_chats/
  └─ {chat_id}/
      ├─ title: string
      ├─ messages: array
      ├─ shared_by: uid
      ├─ likes: number
      ├─ created_at: timestamp

prompts/
  └─ {prompt_id}/
      ├─ title: string
      ├─ content: string
      ├─ created_by: uid
      ├─ uses: number
      ├─ category: string
```

---

## 🔒 **FIREBASE SECURITY RULES**

Users can only read/write their own data. Community data is public. See `firestore.rules`.

---

## [SPARKLE] **QUICK START**

### **Step 1: Ensure Firebase is Connected**
```bash
# Check if serviceAccount.json exists
ls serviceAccount.json

# If not, download from Firebase Console -> Settings ⚙️ -> Service Accounts
```

### **Step 2: Start the Server**
```bash
python web_app.py
```

### **Step 3: Open Browser**
```
http://localhost:5000
```

### **Step 4: Sign In with Firebase**
Click "Sign in" button (top right)

### **Step 5: Try Features**
- [CHAT] Chat normally
- [DASHBOARD] Dashboard shows your stats (updated in real-time)
- [BOOKS] Create study notes, quizzes, flashcards
- [CODE] Save code snippets
- [GAME] Earn XP by using the app

---

## [GIFT] **DATA FLOW EXAMPLE**

**User completes a quiz:**

1. Frontend: User clicks "Complete Quiz"
2. Frontend calls: `await NatsukiAPI.completeQuiz(quizId, score)`
3. Backend receives: `POST /api/quizzes/{id}/complete` with score
4. Backend: Updates quiz in Firebase to `completed: true`
5. Backend: Awards 50 XP via `add_xp(uid, score*10)`
6. Backend: Checks if level-up (every 1000 XP)
7. Firebase updated: `users/{uid}/xp` and `users/{uid}/level`
8. Frontend: Shows "Level Up! [PARTY]"

---

## [TOOLS] **EXTENDING FEATURES**

### **Add New Endpoint**
1. Create function in `firebase_handler.py`
2. Add route in `web_app.py`:
```python
@app.route('/api/my-feature', methods=['POST'])
def my_feature():
    uid = get_uid_from_token()
    if not uid or not firebase_handler:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    result = firebase_handler.my_function(uid, data)
    return jsonify(result)
```
3. Add method to `NatsukiRenAPI` in `api.js`:
```javascript
async myFeature(data) {
    return this.request('/my-feature', 'POST', data);
}
```

---

## [BUG] **TROUBLESHOOTING**

### Firebase not connecting?
```
Error: FIREBASE_SERVICE_ACCOUNT path invalid
-> Check config.py, ensure serviceAccount.json in repo root
```

### API returning 401?
```
Error: Unauthorized
-> User not logged in, or token expired
-> Have them click "Sign in" button
```

### Data not saving?
```
-> Check browser console for errors
-> Verify Firebase rules allow write access
-> Check /logs/ren_core.log for backend errors
```

---

## [DASHBOARD] **FEATURE CHECKLIST**

[OK] Dashboard - Real-time stats
[OK] Study Hub - Notes, quizzes, flashcards, plans
[OK] Code Hub - Snippet storage & tools
[OK] AI Tools - Image, OCR, resume, PDF
[OK] Community - Sharing, prompts, marketplace, leaderboard
[OK] Gamification - XP, levels, badges, challenges

**All endpoints documented and ready to use!**

---

## [PARTY] **YOU'RE GOOD TO GO!**

All features are live. Start using them now! [ROCKET]
