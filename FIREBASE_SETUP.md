# Firebase + Ren Setup Guide

## What's Already Done [OK]
- Backend (`web_app.py`) can verify Firebase ID tokens
- Chat messages auto-save to Firestore when users are authenticated
- Sign-in/Sign-out button in navbar
- Mobile optimizations (fixed alignment, Enter key, touch handlers)
- File upload endpoints (PDF, images, voice) ready for integration

## Next Steps (Easy Mode)

### Step 1: Get Firebase Config
1. Open [Firebase Console](https://console.firebase.google.com/)
2. Click your project: **Ren-AI**
3. Click Settings ⚙️ (top-left gear icon)
4. Scroll down -> **Your apps** -> Click the web app (looks like `</>`
5. Copy the config object that looks like:
```javascript
{
  apiKey: "AIza...",
  authDomain: "ren-ai.firebaseapp.com",
  projectId: "ren-ai-xxxxx",
  ...
}
```

### Step 2: Add Config to index.html
1. Open `index.html`
2. Find `<!-- ══════════════════════════════════════════════ JAVASCRIPT`
3. Right before the first `<script>` tag, add:
```html
<script>
  window.FIREBASE_CONFIG = {
    apiKey: "YOUR_API_KEY_HERE",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "1:YOUR_APP_ID:web:YOUR_WEB_ID"
  };
</script>
```
4. Replace the values with your actual config from Step 1

### Step 3: Get Firebase Service Account (for backend)
1. Firebase Console -> Settings ⚙️ -> **Service Accounts** tab
2. Click **Generate New Private Key** (big blue button)
3. Save the JSON file as `serviceAccount.json` in your project folder: `c:\Ojas\NatsukiXRen\serviceAccount.json`
4. Open `config.py` and add:
```python
FIREBASE_SERVICE_ACCOUNT = 'serviceAccount.json'
```

### Step 4: Deploy Firestore Rules
1. Install Firebase CLI (if not already):
```bash
npm install -g firebase-tools
```

2. Login:
```bash
firebase login
```

3. Deploy rules:
```bash
firebase deploy --only firestore:rules
```
(It will find the `firestore.rules` file automatically)

### Step 5: Test!
```bash
python web_app.py
```
- Open `http://localhost:5000` on your browser
- Click **Sign in** button (top-right)
- Sign in with Google
- Send a message
- Check [Firebase Console](https://console.firebase.google.com/) -> Firestore -> Collections -> `sessions` -> should see your chat there! [PARTY]

## Security Checklist
- [OK] Firestore rules deployed (only owners see their chats)
- [OK] Service account JSON is in `.gitignore` (never commit it!)
- [OK] ID tokens verified on backend before saving
- [OK] API keys not hardcoded in client

## Troubleshooting
- **"Sign in button doesn't work"** -> Firebase config not set or wrong. Check browser console for errors.
- **"Messages not saving to Firestore"** -> Check that you signed in, and that Firestore rules are deployed.
- **"Auth token error"** -> Make sure `config.FIREBASE_SERVICE_ACCOUNT` points to a valid service account JSON.

## Next Advanced Features (whenever ready)
- Real-time chat sync (listen to Firestore changes + auto-update chat)
- Chat history sidebar (list all past sessions)
- Document ingestion (PDF -> embeddings -> search)
- Voice-to-text transcription
- Multi-language support

---

**Questions?** I can help with any step! [ROCKET]
