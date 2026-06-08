# Natsuki-Ren AI

## Overview

Natsuki-Ren is an AI-powered chatbot and learning assistant built with Python, Flask, and Gemini AI. It combines conversational AI, frontend chat UI, and optional Firebase integration to deliver:

- AI chat with flexible persona routing
- User sessions and memory persistence
- Study tools, code snippets, and AI utilities
- Optional Firebase analytics, auth, and Firestore storage

## Architecture

- `web_app.py` — Flask backend and API server
- `engine_gemini.py` — Gemini inference engine wrapper
- `memory.py` — local session memory manager
- `firebase_handler.py` — optional Firebase integration
- `config.py` — environment-driven configuration
- `index.html` — frontend chat UI and interface
- `api.js` — client-side JavaScript API calls

## Key Features

- **AI chat endpoint**: `/api/chat`
- **Healthcheck**: `/api/status`
- **AI tools**: image analysis, OCR, resume review, PDF summarization
- **Learning tools**: notes, quizzes, flashcards, study plans
- **Community tools**: public prompts, shared chats, marketplace, leaderboard
- **Gamification**: XP, badges, daily challenges

## Setup

1. Install dependencies:

```bash
cd c:\Ojas\NatsukiXRen
pip install -r requirements.txt
```

2. Create a `.env` file or set environment variables:

```text
GEMINI_API_KEY=your_gemini_api_key_here
HOST=0.0.0.0
PORT=5000
DEBUG_MODE=False
FIREBASE_SERVICE_ACCOUNT=serviceAccount.json
```

3. Run the server:

```bash
python web_app.py
```

4. Open the frontend:

```text
http://localhost:5000
```

## Environment Variables

- `GEMINI_API_KEY` — required for Gemini AI requests
- `HOST` — server host (default `0.0.0.0`)
- `PORT` — server port (default `5000`)
- `DEBUG_MODE` — Flask debug mode (`True` or `False`)
- `FIREBASE_SERVICE_ACCOUNT` — optional path to Firebase service account JSON

## Firebase Integration (Optional)

To enable Firebase features, provide a valid service account JSON file and set:

```text
FIREBASE_SERVICE_ACCOUNT=serviceAccount.json
```

Firebase is used for:

- user authentication token verification
- Firestore session storage
- shared chats, prompts, and leaderboard data

If Firebase is not enabled, the backend still runs and offers local chat memory.

## API Endpoints

### Core

- `GET /api/status`
- `POST /api/chat`

### Learning / Study

- `GET /api/dashboard`
- `POST /api/notes`
- `GET /api/notes`
- `POST /api/quizzes`
- `GET /api/quizzes`
- `POST /api/quizzes/<quiz_id>/complete`
- `POST /api/flashcards`
- `GET /api/flashcards`
- `POST /api/study-plans`
- `GET /api/study-plans`
- `POST /api/code-snippets`
- `GET /api/code-snippets`

### AI Tools

- `POST /api/analyze-image`
- `POST /api/ocr`
- `POST /api/resume-review`
- `POST /api/pdf-summary`

### Community

- `POST /api/share-chat`
- `GET /api/shared-chats`
- `POST /api/prompts`
- `GET /api/prompts`
- `POST /api/marketplace`
- `GET /api/marketplace`
- `GET /api/leaderboard`

## Notes

- The same Flask app serves the frontend at `/`.
- `config.py` loads `.env` using `dotenv` and creates required folders.
- The app will run even without Firebase; Firebase features simply stay disabled.

## Helpful Files

- `FEATURES.md` — detailed feature documentation
- `SETUP.md` — setup and deployment checklist
- `firestore.rules` — Firebase security rules
- `serviceAccount.json` — Firebase service account key (not tracked by git)

## Push to GitHub

This documentation file is committed and pushed to the `main` branch of the repository.
