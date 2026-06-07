# REN × NATSUKI — THE PROTOCOL
## Dual-Personality AI Chatbot System

---

## [FILES] PROJECT STRUCTURE

```
ren-natsuki/
├── app.py                  ← Flask backend (AI logic, routing)
├── requirements.txt        ← Python dependencies
├── templates/
│   └── index.html          ← Full cinematic frontend
│       ├── Three.js 3D orb
│       ├── GSAP animations
│       ├── Dual personality chat UI
│       └── Loading / landing screens
└── static/                 ← (for future assets)
```

---

## [LIGHTNING] QUICK START

### 1. Get a FREE Groq API Key
Visit: https://console.groq.com/
- Sign up -> API Keys -> Create Key
- Copy your key

### 2. Install Dependencies
```bash
cd ren-natsuki
pip install -r requirements.txt
```

### 3. Set Your API Key

**Option A — Environment variable (recommended):**
```bash
# Linux/Mac:
export GROQ_API_KEY="your_key_here"

# Windows CMD:
set GROQ_API_KEY=your_key_here

# Windows PowerShell:
$env:GROQ_API_KEY="your_key_here"
```

**Option B — Edit app.py directly:**
Change line:
```python
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
```
to:
```python
GROQ_API_KEY = "gsk_your_actual_key_here"
```

### 4. Run
```bash
python app.py
```

### 5. Open
```
http://localhost:5000
```

---

## 🎭 HOW IT WORKS

### Personality Detection (Auto Mode)
The backend scores your message for keywords:
- **Code keywords** -> routes to **Ren** (hacker, precise, cold)
- **Casual/emotion keywords** -> routes to **Natsuki** (warm, creative, expressive)  
- **Mixed/ambiguous** -> routes to **Dual** (both reply)

### Manual Override
Use the mode pills in the chat:
- [LIGHTNING] **Auto-Detect** — AI decides
- ◈ **Force Ren** — always Ren
- ✿ **Force Natsuki** — always Natsuki
- ∞ **Dual Mode** — always both

### Personality Toggle (Top Right)
Switches the UI theme + 3D orb between:
- **REN mode**: Dark, hacker aesthetic, glitch orb, cyan/purple
- **NATSUKI mode**: Light, soft aesthetic, glowing orb, pink/lavender

---

## [TOOLS] CUSTOMIZATION

### Switch AI Provider
The backend uses **Groq** (free, fast). To switch:

**OpenAI:**
```python
GROQ_URL = "https://api.openai.com/v1/chat/completions"
MODEL    = "gpt-4o-mini"
GROQ_API_KEY = "sk-..."
```

**OpenRouter (100+ models):**
```python
GROQ_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL    = "meta-llama/llama-3-70b-instruct"
```

### Edit Personalities
In `app.py`, edit `REN_PROMPT` and `NATSUKI_PROMPT` to change how each character speaks.

---

## 🛠 TECH STACK

| Layer      | Technology |
|------------|------------|
| Backend    | Python + Flask |
| AI         | Groq (Llama 3 70B) |
| 3D         | Three.js (WebGL shaders) |
| Animations | GSAP 3 |
| Fonts      | Orbitron, Syne, JetBrains Mono, Cormorant Garamond |
| Styling    | Pure CSS with CSS variables |

---

## [BUG] TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| "Backend unreachable" | Make sure `python app.py` is running |
| "Invalid API key" | Check your GROQ_API_KEY is set correctly |
| Blank page | Open browser console (F12) for errors |
| Slow responses | Groq free tier is fast; check your internet |

---

Made with 🖤🌸 by REN × NATSUKI