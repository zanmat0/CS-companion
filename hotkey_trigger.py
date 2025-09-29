import keyboard
import requests

def trigger():
    print("🔘 Trigger sendes...")
    try:
        res = requests.post("http://localhost:8000/trigger", json={})
        data = res.json() if res.ok else {}
        tactic = data.get("tactic")
        if tactic:
            print(f"✅ Taktikk: {tactic}")
        else:
            print(f"⚠️ Feil: {data.get('message')}")
    except Exception as e:
        print(f"❌ Feil ved sending: {e}")

keyboard.add_hotkey("ctrl+alt+t", trigger)
print("🚀 Klar. Trykk CTRL + ALT + T for å sende callout")
keyboard.wait()
