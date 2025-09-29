import os
import tempfile
import subprocess
import requests
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()

async def speak_text_with_vc(vc: discord.VoiceClient, text: str):
    api_key = os.getenv("ELEVEN_API_KEY")
    voice_id = os.getenv("ELEVEN_VOICE_ID")

    if not api_key:
        print("❌ ELEVEN_API_KEY mangler")
        return

    try:
        print(f"[🗣️] Sender til ElevenLabs: {text}")

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

        print("[📥] Lyd mottatt fra ElevenLabs")

        mp3_path = os.path.join(tempfile.gettempdir(), "tts.mp3")
        opus_path = os.path.join(tempfile.gettempdir(), "tts.opus")

        with open(mp3_path, "wb") as f:
            f.write(response.content)

        print("[🎙️] Konverterer med ffmpeg...")
        subprocess.check_call([
            "ffmpeg", "-y",
            "-i", mp3_path,
            "-ar", "48000",
            "-ac", "1",
            "-c:a", "libopus",
            opus_path
        ])

        print("[🔊] Spiller av i Discord...")
        source = discord.FFmpegOpusAudio(opus_path)
        vc.play(source)

        await asyncio.sleep(0.5)
        while vc.is_playing():
            await asyncio.sleep(0.2)

        print("[✅] Ferdig å spille")

    except Exception as e:
        print(f"[💥] Feil i ElevenLabs avspilling: {e}")

