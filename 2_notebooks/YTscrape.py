import json
import time
import scrapetube
from datetime import datetime
from google import genai
# Import the specific function directly to avoid "type object" errors
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
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
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "3_outputs"))
DB_FILE = os.path.join(OUTPUT_FOLDER, "financial_summaries.json")

# [FINANCIAL_PROMPT remains the same]
FINANCIAL_PROMPT = """
**Role:** Act as a Senior Investment Analyst and Portfolio Manager with expertise in fundamental analysis, technical analysis, and market psychology. Your goal is to extract actionable investment intelligence from a raw video transcript.

**Context:** You will be provided with a transcript of a YouTube video discussing various financial assets. These transcripts may contain conversational noise, advertisements, irrelevant banter, or incomplete sentences.

**Objective:** Analyze the provided transcript to identify every distinct asset, asset class or macroeconomic element discussed. For each asset, asset class or macroeconomic element determine the speaker's sentiment, the core investment thesis, potential risks, and any specific price targets or time horizons mentioned.

**Instructions:** **1. Filter Noise:** Ignore all requests to "like and subscribe," sponsor reads, and off-topic personal anecdotes. Focus only on financial assertions and data.

**2. Identify Assets:** List every asset mentioned (Stocks, Crypto, Commodities, Forex). If a ticker symbol is available, use it (e.g., AAPL, BTC, GLD).

**3. Analyze Sentiment:** For each asset, classify the speaker's sentiment as Bullish, Bearish, or Neutral. Provide a confidence score (from -1 to 1) based on how explicitly the speaker states their position.

**4. Extract Details:** **The Thesis:** Why does the speaker believe this? (e.g., "Undervalued P/E," "New Product Launch," "Chart Breakout"). **The Risks:** What downside did they mention? (e.g., "Regulatory concerns," "Earnings miss"). **Catalysts:** What upcoming events are driving the price, what is the expected timeframe for the discussed recommendation/thesis to materialize?

**5. Output Format:** Provide the response in valid Markdown format by only using headings (no underline, italics or bolding). 

**Required Output Structure:**

**## Executive Summary** (A complete summary of the video's overall theme and market outlook). Make it heading of ## level.

**## Asset Breakdown** - provide each mentioned asset or asset class, macroeconomic elements mentioned with summary of findings of each. Make this whole section of ## heading level. 

**### [Insert Asset Name]** **Thesis:** (Detailed explanation of the argument). **Key Levels:** (Entry price, Stop loss, Take profit - if mentioned). **Risks:** (Specific counter-arguments mentioned). **Quote:** (A direct quote that summarizes the view).

repeat for all assets...

**# Critique** - Briefly critique the speaker's logic. Did they provide evidence? Did they ignore obvious risks?. Also mention the critique mentioned by the speaker itself. 

Important RULES: 
1. by no means use symbols "*" in your output to bold the output, instead use <b> formatting where you want to bold the text element.
2. Only bold <b> the asset breakdown section under each asset name sections "thesis", "key levels", "risks", "sentiment". Do not bold anything else AT ALL.
"""

client = genai.Client(api_key=API_KEY)

def get_video_transcript(video_id):
    try:
        # Use the static method directly from the class
        srt = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([snippet['text'] for snippet in srt])
    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"Transcript disabled or not found for {video_id}")
        return None
    except Exception as e:
        print(f"General transcript error for {video_id}: {e}")
        return None

def main_run_once():
    # Verify pathing in logs
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
            # Check 4 videos to ensure we don't miss anything pushed down
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
                    # Pause to stay within free tier limits
                    time.sleep(12)
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