import keyboard
import requests

def trigger():
    print("🔘 Trigger sendes...")
    try:
        res = requests.post("http://localhost:8000/trigger", json={})
        if res.ok:
            print(f"✅ Taktikk: {res.json().get('tactic')}")
        else:
            print(f"⚠️ Feil fra server: {res.status_code} {res.text}")
    except Exception as e:
        print(f"❌ Feil ved sending: {e}")

keyboard.add_hotkey("ctrl+alt+t", trigger)
print("🚀 Klar. Trykk CTRL + ALT + T for å sende callout")
keyboard.wait()
