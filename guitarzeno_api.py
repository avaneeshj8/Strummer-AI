from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests
import os
from dotenv import load_dotenv
import unicodedata

app = FastAPI()
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OpenRouter API key! Check your .env file.")

stored_progression: list[tuple[str, int]] = []
current_strum_index: int = 0
current_repeat_count: int = 0
current_song_name: Optional[str] = None

CHORD_BANK = {"C", "Cm", "D", "Dm", "E", "Em", "F", "Fm", "G", "Gm", "A", "Am", "B", "Bm"}

class SongRequest(BaseModel):
    song: Optional[str] = None
    query: Optional[str] = None
    user_chord: Optional[str] = None

def normalize_chord(chord: str) -> str:
    chord = chord.strip().lower()
    replacements = {"_minor": "m", " minor": "m", "_major": "", " major": "", "minor": "m", "major": ""}
    for k, v in replacements.items():
        chord = chord.replace(k, v)
    chord = chord.replace("_", "").capitalize()
    base_chord = ''.join([c for c in chord if c.isalpha() or c == "m"])
    if base_chord not in CHORD_BANK:
        base_chord = chord[0].upper() + ("m" if "m" in chord else "")
        if base_chord not in CHORD_BANK:
            base_chord = "C"
    return base_chord

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("–", "-").replace("—", "-").replace("\xa0", " ")
    text = text.replace("“", '"').replace("”", '"')
    return text.strip()

def get_llm_response(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"model": "openai/gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return clean_text(response.json()["choices"][0]["message"]["content"])

def parse_progression(text: str) -> list[tuple[str, int]]:
    parts = [p.strip() for p in text.replace("–", "-").split("-") if p.strip()]
    parsed = []
    for part in parts:
        if "x" in part:
            chord, times = part.split("x")
            parsed.append((normalize_chord(chord.strip()), int(times.strip())))
        else:
            parsed.append((normalize_chord(part), 1))
    return parsed

def format_progression(prog: list[tuple[str,int]]) -> str:
    return " - ".join([f"{c} x{n}" for c, n in prog])

@app.post("/guitarzeno/song")
async def get_song_info(req: SongRequest):
    global stored_progression, current_strum_index, current_repeat_count, current_song_name

    song_name = req.song or current_song_name
    if req.query:
        try:
            prompt_song = f"Suggest a single song that matches this description, artist, genre, or vibe: '{req.query}'. Respond only with the song name."
            song_name = get_llm_response(prompt_song)
        except Exception as e:
            return {"error": f"Failed to get song from description: {e}"}

    if song_name and (not stored_progression or song_name != current_song_name):
        try:
            prompt_prog = f"Give me the guitar chord progression for '{song_name}' including strum counts, like: Am x2 - G x1. Respond only with progression."
            progression_text = get_llm_response(prompt_prog)
            stored_progression = parse_progression(progression_text)
            current_strum_index = 0
            current_repeat_count = 0
            current_song_name = song_name
            return {
                "song": song_name,
                "chord_progression": stored_progression,
                "formatted_progression": format_progression(stored_progression),
                "message": f"Chord progression for '{song_name}' stored. Ready for strumming!"
            }
        except Exception as e:
            return {"error": f"Failed to get chord progression: {e}"}

    if req.user_chord:
        if not stored_progression:
            return {"error": "No chord progression loaded."}

        user_chord = normalize_chord(req.user_chord)
        expected_chord, expected_repeats = stored_progression[current_strum_index]

        if user_chord == expected_chord:
            current_repeat_count += 1
            if current_repeat_count >= expected_repeats:
                current_strum_index += 1
                current_repeat_count = 0
                if current_strum_index >= len(stored_progression):
                    current_strum_index = 0
            feedback = f"Correct! Played {expected_chord}."
        else:
            feedback = f"Incorrect. Played {user_chord}, expected {expected_chord} (x{expected_repeats})."

        return {
            "user_chord": user_chord,
            "expected_chord": expected_chord,
            "remaining_repeats": expected_repeats - current_repeat_count,
            "feedback": feedback,
            "progression": stored_progression,
            "formatted_progression": format_progression(stored_progression)
        }

    return {"error": "Provide either a song/query or a user_chord."}
