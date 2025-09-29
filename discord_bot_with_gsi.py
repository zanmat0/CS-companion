import os
import asyncio
import tempfile
import subprocess
import requests
import pyttsx3
import discord
from discord.ext import commands
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import threading
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# === Konfig ===
TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = "!"
DEFAULT_MAP = "mirage"
DEFAULT_SIDE = "ct"

# === Discord bot ===
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# === Kommandoer ===
@bot.event
async def on_ready():
    print(f"[✅] Bot er online som {bot.user}")

@bot.command(name="start")
async def start_game(ctx, map_name: str = DEFAULT_MAP, side: str = DEFAULT_SIDE):
    global current_map, current_side

    map_name = map_name.lower()
    side = side.lower()

    if map_name not in TACTICS or side not in ("ct", "t"):
        await ctx.send("❌ Ugyldig map eller side.")
        return

    if not ctx.author.voice:
        await ctx.send("❌ Du må være i en voice-kanal.")
        return

    voice_channel = ctx.author.voice.channel
    vc: discord.VoiceClient = await voice_channel.connect()
    await asyncio.sleep(1)

    current_map = map_name
    current_side = side

    await ctx.send(f"🎮 Klar for {map_name.upper()} som {side.upper()}.\n🔊 Koblet til voice-kanalen: {voice_channel.name}")

@bot.command(name="say")
async def say(ctx, *, message: str):
    await speak_text(ctx, message)

# === TTS-funksjon ===
async def speak_text(ctx, text: str):
    if not ctx.author.voice:
        await ctx.send("❌ Du må være i en voice-kanal.")
        return

    voice_channel = ctx.author.voice.channel

    # Bruk eksisterende VC hvis mulig
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not vc or not vc.is_connected():
        vc = await voice_channel.connect()
        await asyncio.sleep(1)

    try:
        wav_path = os.path.join(tempfile.gettempdir(), "tts.wav")
        opus_path = os.path.join(tempfile.gettempdir(), "tts.opus")

        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        for voice in voices:
            print(f"{voice.id} — {voice.name}")

        # Sett ønsket stemme (f.eks. norsk mannsstemme hvis tilgjengelig)
        engine.setProperty("voice", voices[2].id)  # Prøv annen index!
        engine.setProperty("rate", 160)  # Juster hastighet

        engine.save_to_file(text, wav_path)
        engine.runAndWait()

        subprocess.check_call([
            "ffmpeg", "-y",
            "-i", wav_path,
            "-ar", "48000",
            "-ac", "1",
            "-c:a", "libopus",
            opus_path
        ])

        source = discord.FFmpegOpusAudio(opus_path)
        vc.play(source)

        await asyncio.sleep(0.5)
        while vc.is_playing():
            await asyncio.sleep(0.2)

    except Exception as e:
        print(f"[💥] Feil i speak_text: {e}")
        await ctx.send(f"❌ Klarte ikke spille av lyd: {e}")

    finally:
        print("[✅] Ferdig med taktikk – forblir i voice.")

# === FastAPI-server for hotkey trigger ===
app = FastAPI()

class TriggerRequest(BaseModel):
    tactic: str | None = None

@app.post("/trigger")
async def trigger_callout(req: TriggerRequest):
    if not current_map or not current_side:
        return {"status": "error", "message": "Bruk !start først."}

    tactic = req.tactic or np.random.choice(TACTICS[current_map][current_side])
    print(f"[📣] Taktikk: {tactic}")

    # Finn aktiv voice client
    for vc in bot.voice_clients:
        if vc.is_connected():
            try:
                # Spill lyd direkte på eksisterende VC
                await speak_text_with_vc(vc, tactic)
                return {"status": "ok", "tactic": tactic}
            except Exception as e:
                return {"status": "error", "message": f"Avspillingsfeil: {e}"}

    return {"status": "error", "message": "Botten er ikke tilkoblet noen voice channel."}

async def speak_text_with_vc(vc: discord.VoiceClient, text: str):
    api_key = os.getenv("ELEVEN_API_KEY")
    voice_id = os.getenv("ELEVEN_VOICE_ID")  # Rachel

    if not api_key:
        print("❌ ELEVEN_API_KEY mangler i .env")
        return

    try:
        print(f"[🗣️] Sender til ElevenLabs: {text}")

        # Kall API
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.6,
                    "speed": 0.7
                }
            }
        )

        if response.status_code != 200:
            print(f"[❌] ElevenLabs-feil: {response.status_code} {response.text}")
            return

        # Lagre som .mp3
        mp3_path = os.path.join(tempfile.gettempdir(), "tts.mp3")
        opus_path = os.path.join(tempfile.gettempdir(), "tts.opus")

        with open(mp3_path, "wb") as f:
            f.write(response.content)

        # Konverter til .opus
        subprocess.check_call([
            "ffmpeg", "-y",
            "-i", mp3_path,
            "-ar", "48000",
            "-ac", "1",
            "-c:a", "libopus",
            opus_path
        ])

        # Spill av i Discord
        source = discord.FFmpegOpusAudio(opus_path)
        vc.play(source)

        await asyncio.sleep(0.5)
        while vc.is_playing():
            await asyncio.sleep(0.2)

    except Exception as e:
        print(f"[💥] Feil i ElevenLabs avspilling: {e}")

# === Start FastAPI + Discord ===
def run_all():
    loop = asyncio.get_event_loop()

    async def main():
        config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()

        await bot.start(TOKEN)

    loop.run_until_complete(main())

if __name__ == "__main__":
    run_all()
