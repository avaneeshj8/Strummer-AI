import requests

def send_chord_feedback(song=None, query=None, user_chord=None):
    url = "http://localhost:8000/guitarzeno/song"
    payload = {"song": song, "query": query, "user_chord": user_chord}
    response = requests.post(url, json=payload)
    return response.json()
