# main.py

import os
import asyncio
import uvicorn
from fastapi import FastAPI
from bot import discord_bot  # <-- Bruk nytt navn
from server.api import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.include_router(router)

async def start_fastapi():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    print("🚀 Starter FastAPI + Discord-bot...")

    fastapi_task = asyncio.create_task(start_fastapi())
    print("✅ FastAPI-server startet")

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN mangler i .env")
        return

    print("🔑 Token OK. Starter bot...")
    await discord_bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
