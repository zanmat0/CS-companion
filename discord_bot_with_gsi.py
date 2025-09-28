import discord
from discord.ext import commands
import asyncio
import sounddevice as sd
import numpy as np
import whisper
import tempfile
from scipy.io.wavfile import write
import pyttsx3
from dotenv import load_dotenv
import os
import sys
import traceback

# ========== Global feil-logg ==========
def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("[💥 GLOBAL EXCEPTION]")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler

# ========== Konfigurasjon ==========
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TRIGGER_WORD = os.getenv("TRIGGER_WORD", "taktikk").lower()
SAMPLE_SECONDS = int(os.getenv("SAMPLE_SECONDS", 4))
SAMPLE_RATE = 16000
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
DEFAULT_MAP = os.getenv("MAP", "mirage").lower()
DEFAULT_SIDE = os.getenv("SIDE", "ct").lower()

MODEL = whisper.load_model("medium")

# ========== Taktikkdatabase ==========
TACTICS = {
    "mirage": {
        "ct": [
            "Hold B passivt med en i jungle klar til å rotere.",
            "Spill 2 B, 2 mid, og en på A. Roter raskt ved push.",
            "Boost mid tidlig og fall tilbake om ingen info."
        ],
        "t": [
            "Rush mid til connector, smoke window.",
            "Gå A kontakt med en lurk palace.",
            "Fake B, roter til A etter 10 sek."
        ]
    }
}

# ========== State ==========
current_map = None
current_side = None
current_vc = None

# ========== Bot-oppsett ==========
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"[✅] Bot er online som {bot.user}")

@bot.command(name="start")
async def start_game(ctx, map_name: str = DEFAULT_MAP, side: str = DEFAULT_SIDE):
    global current_map, current_side, current_vc

    map_name = map_name.lower()
    side = side.lower()

    if map_name not in TACTICS:
        await ctx.send(f"❌ Ukjent map: {map_name}")
        return
    if side not in ["ct", "t"]:
        await ctx.send("❌ Side må være enten 'ct' eller 't'")
        return

    if ctx.author.voice:
        current_vc = await ctx.author.voice.channel.connect()
        await ctx.send(f"🔊 Bli med i {ctx.author.voice.channel.name} – jeg hører etter '{TRIGGER_WORD}'...")
    else:
        await ctx.send("⚠️ Du må være i en voice channel for at jeg skal kunne høre deg!")
        return

    current_map = map_name
    current_side = side
    await ctx.send(f"🎯 Klar for **{map_name.upper()}** som **{side.upper()}**. Si “{TRIGGER_WORD}” for callout.")

    asyncio.create_task(safe_listen_wrapper(ctx))

async def safe_listen_wrapper(ctx):
    try:
        await listen_for_trigger(ctx)
    except Exception as e:
        print(f"[💥] FEIL i lytte-loop: {e}")
        await ctx.send(f"❌ Feil i lytte-loop: {e}")

async def listen_for_trigger(ctx):
    print("[👂] Lytter etter trigger...")

    while True:
        await asyncio.sleep(1)
        try:
            print("[🎙️] Opptak starter...")
            recording = sd.rec(int(SAMPLE_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
            sd.wait()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                write(tmpfile.name, SAMPLE_RATE, recording)
                print(f"[🧠] Whisper-transkribering: {tmpfile.name}")
                result = MODEL.transcribe(tmpfile.name, language='no')

            text = result.get("text", "").strip().lower()
            print(f"[📝] Gjenkjent tekst: {text}")

            if any(trigger in text for trigger in [TRIGGER_WORD, TRIGGER_WORD.replace('k', 'g'), TRIGGER_WORD.replace('kk', 'k'), TRIGGER_WORD.upper()]) and current_map and current_side:
                call = get_call()
                await ctx.send(f"📣 **Taktikk** ({current_map.upper()} | {current_side.upper()}): {call}")
                await speak_text(call)
            else:
                print("[⏭️] Trigger ikke oppdaget.")

        except Exception as err:
            print(f"[🚨] Opptak/transkripsjon-feil: {err}")

def get_call():
    return np.random.choice(TACTICS[current_map][current_side])

async def speak_text(text):
    try:
        print(f"[🔊] Leser opp: {text}")
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tf:
            engine.save_to_file(text, tf.name)
            engine.runAndWait()
            wav_path = tf.name

        if current_vc and current_vc.is_connected():
            current_vc.play(discord.FFmpegPCMAudio(wav_path))
            while current_vc.is_playing():
                await asyncio.sleep(0.5)
    except Exception as e:
        print(f"[🔇] FEIL i TTS/avspilling: {e}")

@bot.command(name="disconnect")
async def disconnect(ctx):
    global current_vc
    if current_vc:
        await current_vc.disconnect()
        current_vc = None
        await ctx.send("🔇 Botten har forlatt voice.")

# ========== Start bot ==========
if __name__ == "__main__":
    try:
        print("[🚀] Starter bot...")
        bot.run(TOKEN)
    except Exception as e:
        print(f"[💥] Bot run feilet: {e}")
