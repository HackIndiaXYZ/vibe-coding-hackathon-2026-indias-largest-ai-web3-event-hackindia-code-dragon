# 🧪 API TESTING GUIDE

## 🎬 Quick Test - Try These in Browser Console (F12)

### Test 1: Get Dashboard Stats
```javascript
const stats = await window.NatsukiAPI.getDashboard()
console.log(stats)
```

**Expected Response:**
```json
{
  "total_chats": 0,
  "messages_sent": 0,
  "daily_streak": 0,
  "ai_usage": 0,
  "level": 1,
  "xp": 0
}
```

---

### Test 2: Create a Study Note
```javascript
const note = await window.NatsukiAPI.createNote(
  "Introduction to Python",
  "Python is a programming language that emphasizes readability...",
  "Programming"
)
console.log(note)
```

**Expected Response:**
```json
{
  "id": "note_12345",
  "success": true
}
```

---

### Test 3: Get All Notes
```javascript
const notes = await window.NatsukiAPI.getNotes()
console.log(notes)
```

**Expected Response:**
```json
{
  "notes": [
    {
      "id": "note_12345",
      "title": "Introduction to Python",
      "content": "Python is a programming language...",
      "subject": "Programming",
      "created_at": {...}
    }
  ]
}
```

---

### Test 4: Create Quiz
```javascript
const quiz = await window.NatsukiAPI.createQuiz(
  "Python Basics Quiz",
  [
    { "question": "What is Python?", "answer": "A programming language" },
    { "question": "How do you print in Python?", "answer": "print()" }
  ],
  "Programming"
)
console.log(quiz)
```

---

### Test 5: Complete Quiz & Earn XP
```javascript
const result = await window.NatsukiAPI.completeQuiz("quiz_id", 85)
console.log(result)
```

**Expected Response:**
```json
{
  "success": true
}
```

---

### Test 6: Add XP & Level Up
```javascript
const xp = await window.NatsukiAPI.addXP(100)
console.log(xp)
```

**Expected Response:**
```json
{
  "success": true,
  "xp": 100,
  "level": 1,
  "leveled_up": false
}
```

---

### Test 7: Add Badge
```javascript
const badge = await window.NatsukiAPI.addBadge("Code_Warrior")
console.log(badge)
```

**Expected Response:**
```json
{
  "success": true,
  "badges": ["Code_Warrior"]
}
```

---

### Test 8: Get Leaderboard
```javascript
const leaderboard = await window.NatsukiAPI.getLeaderboard(10)
console.log(leaderboard)
```

**Expected Response:**
```json
{
  "leaderboard": [
    {
      "uid": "user_123",
      "xp": 5000,
      "level": 5,
      "badges": ["Code_Warrior", "Quiz_Master"]
    }
  ]
}
```

---

### Test 9: Create Daily Challenge
```javascript
const challenge = await window.NatsukiAPI.createDailyChallenge(
  "Complete 5 quizzes",
  "Answer questions in 5 different quizzes",
  50
)
console.log(challenge)
```

---

### Test 10: Complete Daily Challenge
```javascript
const completed = await window.NatsukiAPI.completeDailyChallenge("challenge_id")
console.log(completed)
```

---

## [TOOLS] Advanced Testing - Using cURL

### 1. Get Dashboard
```bash
curl -X GET http://localhost:5000/api/dashboard \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json"
```

### 2. Create Note
```bash
curl -X POST http://localhost:5000/api/notes \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Note",
    "content": "Note content here",
    "subject": "Tech"
  }'
```

### 3. Create Quiz
```bash
curl -X POST http://localhost:5000/api/quizzes \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Quiz",
    "questions": [{"q": "What is Python?"}],
    "subject": "Programming"
  }'
```

### 4. Add XP
```bash
curl -X POST http://localhost:5000/api/user/xp \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"xp": 100}'
```

### 5. Get Leaderboard
```bash
curl -X GET http://localhost:5000/api/leaderboard?limit=50 \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

---

## 🔍 Expected Behavior

### Authentication
- [OK] Without Bearer token: Returns 401 Unauthorized
- [OK] With invalid token: Returns 401 Unauthorized
- [OK] With valid token: Returns data

### Database
- [OK] Data persists after page refresh
- [OK] All users see their own data (private)
- [OK] Community data visible to all
- [OK] Leaderboard shows everyone's XP

### Gamification
- [OK] 1000 XP = 1 Level up
- [OK] Badges accumulate (no duplicates)
- [OK] Streak increases on daily challenges
- [OK] Quiz score × 10 = XP awarded

---

## [BUG] Debugging Tips

### Check Console for Errors
```javascript
// In browser F12 Console
window.NatsukiAPI.getDashboard()
  .then(r => console.log(r))
  .catch(e => console.error(e))
```

### Check Network Requests
1. Open DevTools (F12)
2. Go to Network tab
3. Try an action
4. Click the request -> see status & response

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Not logged in | Click "Sign in" button |
| 400 Bad Request | Missing field | Check JSON body |
| 500 Server Error | Backend bug | Check logs/ren_core.log |
| CORS Error | Browser policy | Check CORS enabled |

---

## [DASHBOARD] Test Scenarios

### Scenario 1: Study Workflow
```javascript
// 1. Create study materials
await NatsukiAPI.createNote("Topic", "Details", "Subject")
await NatsukiAPI.createQuiz("Title", [...], "Subject")

// 2. Complete quiz
await NatsukiAPI.completeQuiz(quizId, 90)

// 3. Check XP gained
const stats = await NatsukiAPI.getDashboard()
console.log(`You earned ${stats.xp} XP!`)
```

### Scenario 2: Gamification Workflow
```javascript
// 1. Get daily challenges
const challenges = await NatsukiAPI.getDailyChallenges()

// 2. Complete challenge
await NatsukiAPI.completeDailyChallenge(challenges[0].id)

// 3. Check streaks & level
const stats = await NatsukiAPI.getDashboard()
console.log(`Streak: ${stats.daily_streak}, Level: ${stats.level}`)
```

### Scenario 3: Community Workflow
```javascript
// 1. Create public prompt
await NatsukiAPI.createPublicPrompt(
  "Write SQL Query",
  "Write a query to find users with most purchases",
  "Database"
)

// 2. Browse prompts
const prompts = await NatsukiAPI.getPublicPrompts()
console.log(`Found ${prompts.prompts.length} prompts`)

// 3. View leaderboard
const leaders = await NatsukiAPI.getLeaderboard(10)
console.log(leaders)
```

---

## [OK] Full API Checklist

### Dashboard
- [x] GET /api/dashboard

### Study Hub
- [x] POST /api/notes
- [x] GET /api/notes
- [x] POST /api/quizzes
- [x] GET /api/quizzes
- [x] POST /api/quizzes/{id}/complete
- [x] POST /api/flashcards
- [x] GET /api/flashcards
- [x] POST /api/study-plans
- [x] GET /api/study-plans

### Code Hub
- [x] POST /api/code-snippets
- [x] GET /api/code-snippets

### AI Tools
- [x] POST /api/analyze-image
- [x] POST /api/ocr
- [x] POST /api/resume-review
- [x] POST /api/pdf-summary

### Community
- [x] POST /api/share-chat
- [x] GET /api/shared-chats
- [x] POST /api/prompts
- [x] GET /api/prompts
- [x] POST /api/marketplace
- [x] GET /api/marketplace
- [x] GET /api/leaderboard

### Gamification
- [x] POST /api/user/xp
- [x] POST /api/user/badge
- [x] POST /api/daily-challenges
- [x] GET /api/daily-challenges
- [x] POST /api/daily-challenges/{id}/complete

**Total: 30+ endpoints** [OK]

---

## [GOAL] Performance Notes

- Dashboard stats: < 100ms
- Create note: < 200ms
- Get leaderboard: < 300ms (50 users)
- All requests include Firebase overhead

---

## [ROCKET] Ready to Test!

Start the server and try the console commands above!

```bash
python web_app.py
# Open browser console: F12
# Run: await window.NatsukiAPI.getDashboard()
```

Let me know if you find any issues! [BUG]
