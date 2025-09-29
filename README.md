# 🧠 CS-Companion, the automated CS2 IGL for you — Discord + FastAPI + ElevenLabs

A real-time **In-Game Leader (IGL)** bot for CS2 that calls simple, natural, and paced tactics in your Discord voice channel.

- 🟣 **discord.py** – Discord commands + voice playback  
- ⚡ **FastAPI** – local HTTP trigger for hotkey scripts  
- 🗣️ **ElevenLabs** – high quality TTS (with timing via short sentences + ellipses)  
- ⌨️ **Hotkey script** – press `Ctrl + Alt + T` to trigger a random tactic for the current map/side

---

## ✨ Features

- `!start [map] [side]` — set current context (e.g. `!start mirage t`)
- `!say "text"` — speak any custom line
- **Hotkey trigger** (`Ctrl+Alt+T`) hits `POST /trigger` → bot plays a random tactic for the active map/side
- Keeps a **persistent voice connection** for quick callouts
- **Shared state** between Discord and the API via a single Python module
- Tactics are short, repeated, with **natural pauses** using `...`

---

## 📁 Project Structure

```
cs2-igl-bot/
├─ bot/
│  ├─ __init__.py        # creates Discord bot instance: `discord_bot` and imports cmds
│  ├─ cmds.py            # all Discord commands/events (!start, !say, on_ready)
│  ├─ tts.py             # ElevenLabs (and optional local TTS) + ffmpeg conversion
│  ├─ tactics.py         # TACTICS dict (maps → {ct:[], t:[]})
│  └─ state.py           # shared: current_map, current_side
│
├─ server/
│  └─ api.py             # FastAPI: POST /trigger  (uses shared state + discord_bot)
│
├─ trigger_hotkey.py     # local script with keyboard hotkey → POST /trigger
├─ main.py               # launches FastAPI + Discord concurrently
├─ .env                  # tokens/keys (not committed)
├─ install.sh            # setup using `python` (not python3)
├─ requirements.txt
└─ README.md
```

> **Important:** The Discord bot object is named **`discord_bot`** (not `bot`) to avoid name conflicts with the `bot` package.

---

## 🔑 Environment

Create a `.env` in project root:

```env
DISCORD_TOKEN=your_discord_bot_token
ELEVEN_API_KEY=your_elevenlabs_api_key
ELEVEN_VOICE_ID=rachel   # or another valid voice id
```

---

## 🧰 Installation

### Option A: install script (Linux/macOS/WSL)

```bash
chmod +x install.sh
./install.sh
```

### Option B: manual

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**External dependency:** [FFmpeg](https://ffmpeg.org/) must be installed and available on PATH.  
- Windows (Chocolatey): `choco install ffmpeg`  
- Ubuntu/Debian: `sudo apt install ffmpeg`  
- macOS (Homebrew): `brew install ffmpeg`

---

## 🚀 Run

```bash
python main.py
```

Expected startup logs:

```
🔥 cmds.py er lastet
🚀 Starter FastAPI + Discord-bot...
✅ FastAPI-server startet
🔑 Token OK. Starter bot...
[✅] Bot er online som <your-bot-name>#1234
```

---

## 🎮 Usage

### 1) In Discord (set context + join voice)
```
!start mirage t
```
- Bot joins your current voice channel  
- Sets `current_map="mirage"`, `current_side="t"`

### 2) Hotkey trigger (local)
```bash
python trigger_hotkey.py
```
Output:
```
🚀 Klar. Trykk CTRL + ALT + T for å sende callout
```
Press `Ctrl+Alt+T` while playing → bot speaks a random tactic for the current map/side.

### 3) Say anything
```
!say testing one two three
```

---

## 🌐 API

### `POST /trigger`
Triggers a random tactic for the current map/side stored in `bot/state.py`.

- **Request body:** optional JSON; if you include `"tactic"`, that exact line will be spoken
- **Requires:** `!start` must have been run to set map/side first
- **Response (JSON):**
  ```json
  { "status": "ok", "tactic": "Rush B... GO GO GO!" }
  ```
  or error:
  ```json
  { "status": "error", "message": "Bruk !start først.", "tactic": null }
  ```

---

## 🗺️ Supported Maps & Sides

Maps: `mirage`, `dust2`, `inferno`, `nuke`, `overpass`, `vertigo`, `train`, `ancient`  
Sides: `t`, `ct`

Tactics live in `bot/tactics.py` with this shape:

```python
TACTICS = {
  "mirage": {
    "ct": ["..."],
    "t":  ["..."]
  },
  # more maps...
}
```

Tips for natural TTS pacing:
- **Short sentences**, repeat key lines, use `...` for pauses
- Example: `“Rush B... I repeat — rush B. Flash now. GO GO GO!”`

---

## 🧪 Troubleshooting

### Bot starts, but no commands/events
- Ensure `bot/__init__.py` contains:
  ```python
  discord_bot = commands.Bot(...)
  from . import cmds  # must be after creating discord_bot
  ```
- Alternatively, add `import bot.cmds  # noqa: F401` in `main.py`

### `AttributeError: module 'bot' has no attribute 'start'`
- You likely imported the package, not the bot instance. In `main.py`:
  ```python
  from bot import discord_bot
  await discord_bot.start(token)
  ```

### Commands module not loading
- Avoid name conflicts between `bot/commands/` (package) and `bot/commands.py` (file).  
  Use `bot/cmds.py` for the commands file.

### Trigger returns `None` or no audio
- Make sure `!start` was executed first (map/side set)
- Check API responses: always return JSON in `/trigger`
- Verify ElevenLabs: valid `ELEVEN_API_KEY` + `ELEVEN_VOICE_ID`
- Ensure FFmpeg is installed and reachable
- Check logs in `bot/tts.py`:
  - `[📥] Lyd mottatt fra ElevenLabs`
  - `[🎙️] Konverterer med ffmpeg...`
  - `[🔊] Spiller av i Discord...`

### Windows notes
- Make sure Python and FFmpeg are in PATH
- If using WSL, `install.sh` works as-is

---

## 📦 Dependencies

`requirements.txt` example:
```
discord.py
fastapi
uvicorn
requests
numpy
python-dotenv
keyboard
pyttsx3
```

> `pyttsx3` is optional as a local TTS fallback if you want one.

---

## 📜 License

MIT — use freely for fragging and fun.


