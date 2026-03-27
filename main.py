import time
import json
import os
import requests

STREAMER = "adinross"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1487180223349919847/vFyLvnWXYhZa9N3NeoRGwhG96h82HtG6XKLrBJokVGXOH0KQB7VSUDbDokBK_Z-xVW4J"
SEEN_FILE = "seen_clips.json"

print(f"🚀 Checking for new clips from {STREAMER}...")

seen_clips = set()
if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r") as f:
            seen_clips = set(json.load(f))
    except:
        pass

def send_to_discord(clip):
    embed = {
        "title": clip.get("title", "New Kick Clip!"),
        "url": f"https://kick.com/{STREAMER}/clip/{clip.get('id')}",
        "description": f"New clip from **{STREAMER}**!",
        "color": 0x00ff00,
        "thumbnail": {"url": clip.get("thumbnail_url", clip.get("thumbnail", ""))},
        "footer": {"text": "Auto-posted • GitHub Actions"}
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        print(f"✅ Sent: {clip.get('title', 'Clip')}")
    except Exception as e:
        print(f"Discord error: {e}")

try:
    urls_to_try = [
        f"https://kick.com/api/v2/channels/{STREAMER}/clips",
        f"https://kick.com/api/v1/channels/{STREAMER}/clips"
    ]

    success = False
    for url in urls_to_try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=15, headers=headers)

        if response.status_code == 200:
            data = response.json()
            clips_list = data.get("clips", []) if isinstance(data, dict) else []

            new_clips = []
            for clip in clips_list[:20]:
                clip_id = str(clip.get("id"))
                if clip_id and clip_id not in seen_clips:
                    new_clips.append(clip)
                    seen_clips.add(clip_id)

            for clip in reversed(new_clips):
                send_to_discord(clip)

            if new_clips:
                with open(SEEN_FILE, "w") as f:
                    json.dump(list(seen_clips), f)
                print(f"Found and sent {len(new_clips)} new clip(s)")

            success = True
            break

    if not success:
        print("⚠️ Could not fetch clips this time.")

except Exception as e:
    print(f"Error: {e}")

print("✅ Check completed.")
