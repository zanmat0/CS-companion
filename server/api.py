from fastapi import APIRouter
from pydantic import BaseModel
import numpy as np
from bot import discord_bot, tactics, tts, state

router = APIRouter()

class TriggerRequest(BaseModel):
    tactic: str | None = None

@router.post("/trigger")
async def trigger_callout(req: TriggerRequest):
    print(f"📡 Mottatt trigger. Map: {state.current_map}, Side: {state.current_side}")

    if not state.current_map or not state.current_side:
        return {"status": "error", "message": "Bruk !start først."}

    try:
        options = tactics.TACTICS[state.current_map][state.current_side]
        tactic = req.tactic or np.random.choice(options)
    except Exception as e:
        print(f"[💥] Feil i taktikkvalg: {e}")
        return {"status": "error", "message": f"Taktikkfeil: {e}", "tactic": None}

    print(f"[📣] Taktikk valgt: {tactic}")

    try:
        for vc in discord_bot.voice_clients:
            if vc.is_connected():
                await tts.speak_text_with_vc(vc, tactic)
                return {"status": "ok", "tactic": tactic}
    except Exception as e:
        print(f"[💥] Avspillingsfeil: {e}")
        return {"status": "error", "message": str(e), "tactic": tactic}

    return {"status": "error", "message": "Ingen aktiv voice channel", "tactic": tactic}


