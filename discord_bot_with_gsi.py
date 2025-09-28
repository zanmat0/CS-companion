import threading
import discord
from discord.ext import commands
from flask import Flask, request, jsonify
from flask_cors import CORS

DISCORD_TOKEN = "Ditt_Discord_Token_Her"
DISCORD_CHANNEL_NAME = "general"  # Endre til din kanal

# Flask app for GSI
app = Flask(__name__)
CORS(app)

# Discord bot-setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
discord_channel = None

# Status-tracking
last_round = -1
last_winner = None

@app.route("/gsi", methods=["POST"])
def gsi():
    global last_round, last_winner

    data = request.json

    round_phase = data.get("round", {}).get("phase")
    map_info = data.get("map", {})
    team_ct = map_info.get("team_ct", {}).get("score", 0)
    team_t = map_info.get("team_t", {}).get("score", 0)
    round_number = map_info.get("round", 0)

    # Bare send hvis ny runde
    if round_number != last_round and round_phase == "over":
        last_round = round_number
        if team_ct > team_t:
            last_winner = "Counter-Terrorists"
        else:
            last_winner = "Terrorists"

        if discord_channel:
            text = f"💥 Runde {round_number} er ferdig. Vinner: **{last_winner}** (CT: {team_ct} - T: {team_t})"
            coro = discord_channel.send(text)
            fut = discord_client.loop.create_task(coro)

    return jsonify({"status": "ok"})

# Flask-kjøring i egen tråd
def run_flask():
    app.run(host="0.0.0.0", port=3000)

# Discord-bot startup
@bot.event
async def on_ready():
    global discord_channel
    print(f"[DISCORD] Logget inn som {bot.user}")
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == DISCORD_CHANNEL_NAME:
                discord_channel = channel
                print(f"[DISCORD] Fant kanal: {channel.name}")
                return

# Start Flask server i bakgrunnen
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Start Discord bot
discord_client = bot
bot.run(DISCORD_TOKEN)
