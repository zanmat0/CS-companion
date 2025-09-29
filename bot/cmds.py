import discord
from discord.ext import commands
import asyncio

from .tts import speak_text_with_vc
from .tactics import TACTICS
from . import state

from bot import discord_bot  

print("🔥 cmds.py er lastet")

@discord_bot.event
async def on_ready():
    print(f"[✅] Bot er online som {discord_bot.user}")

@discord_bot.command(name="start")
async def start_game(ctx, map_name: str = "mirage", side: str = "ct"):
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
    vc = await voice_channel.connect()
    await asyncio.sleep(1)

    state.current_map = map_name
    state.current_side = side

    await ctx.send(f"🎮 Klar for {map_name.upper()} som {side.upper()}.\n🔊 Koblet til voice-kanalen: {voice_channel.name}")

@discord_bot.command(name="say")
async def say(ctx, *, message: str):
    vc = discord.utils.get(discord_bot.voice_clients, guild=ctx.guild)
    if not vc or not vc.is_connected():
        vc = await ctx.author.voice.channel.connect()
        await asyncio.sleep(1)

    await speak_text_with_vc(vc, message)
