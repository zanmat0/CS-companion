# bot/__init__.py

from discord.ext import commands
import discord

COMMAND_PREFIX = "!"
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

discord_bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Importer kommandoer så de blir registrert
from . import cmds
