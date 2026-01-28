import json
import time
import scrapetube
from datetime import datetime
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
import os

# --- CONFIGURATION ---
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Ensure it is set in GitHub Secrets, Rayne.")

CHANNEL_IDS = ["UCw9Yjk4De_l21-sxLUvCbTw", "UCRvqjQPSeaWn-uEx-w0XOIg", "UCkrwgzhIBKccuDsi_SvZtnQ"]

CHANNEL_MAP = {
    "UCw9Yjk4De_l21-sxLUvCbTw": "Tom Hayes",
    "UCRvqjQPSeaWn-uEx-w0XOIg": "Benjamin Cowen",
    "UCkrwgzhIBKccuDsi_SvZtnQ": "Forward Guidance"
}

# --- DYNAMIC PATHING ---
# Ensure we find the folder regardless of where the command is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "3_outputs"))
DB_FILE = os.path.join(OUTPUT_FOLDER, "financial_summaries.json")

# [FINANCIAL_PROMPT stays exactly as you have it]
FINANCIAL_PROMPT = """[Your Prompt Text Here]"""

client = genai.Client(api_key=API_KEY)

def get_video_transcript(video_id):
    try:
        # FIX: Call the class method directly, do not use an instance ()
        srt = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([snippet['text'] for snippet in srt])
    except Exception as e:
        print(f"Transcript error for {video_id}: {e}")
        return None

def main_run_once():
    print(f"Target Database File: {DB_FILE}")

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    try:
        with open(DB_FILE, "r") as f:
            all_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_data = []

    seen_ids = {entry['video_id'] for entry in all_data}
    new_entries_added = False

    print("Checking for new financial videos, Rayne...")

    for channel in CHANNEL_IDS:
        try:
            # Look back further (limit=5) to catch anything missed
            videos = list(scrapetube.get_channel(channel, limit=4))
            
            for video in videos:
                v_id = video['videoId']
                v_title = video.get('title', {}).get('runs', [{}])[0].get('text', 'No Title')
                
                if v_id in seen_ids:
                    print(f"Skipping: {v_title} (Already in database)")
                    continue
                
                transcript = get_video_transcript(v_id)
                if transcript:
                    v_time = video.get('publishedTimeText', {}).get('simpleText', 'Unknown Date')
                    print(f"Processing: {v_title} ({v_time})")
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[f"{FINANCIAL_PROMPT}\n\nTranscript:\n{transcript}"]
                    )

                    all_data.append({
                        "video_id": v_id,
                        "channel_name": CHANNEL_MAP.get(channel, "Unknown Analyst"),
                        "title": v_title,
                        "date_of_interest": v_time,
                        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "analysis": response.text
                    })
                    seen_ids.add(v_id)
                    new_entries_added = True
                    time.sleep(10)
        except Exception as e:
            print(f"Could not fetch channel {channel}: {e}")
            continue

    if new_entries_added:
        all_data.sort(key=lambda x: x['processed_at'], reverse=True)
        with open(DB_FILE, "w") as f:
            json.dump(all_data, f, indent=4)
        print("Database updated successfully, Rayne.")
    else:
        print("No new videos found today, Rayne.")

if __name__ == "__main__":
    main_run_once()