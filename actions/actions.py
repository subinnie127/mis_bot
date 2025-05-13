from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import base64
import os

class ActionBuscarCancionesNCT(Action):
    def name(self) -> Text:
        return "action_buscar_canciones_nct"

    def get_token(self, client_id: str, client_secret: str) -> str:
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        try:
            token = self.get_token(client_id, client_secret)
            url = "https://api.spotify.com/v1/search?q=NCT&type=track&limit=5"
            headers = {
                "Authorization": f"Bearer {token}"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            tracks = response.json()["tracks"]["items"]
            if not tracks:
                dispatcher.utter_message(text="No encontré canciones de NCT.")
            else:
                canciones = "\n".join(
                    f"{t['name']} - {', '.join(a['name'] for a in t['artists'])}" for t in tracks
                )
                dispatcher.utter_message(text=f"Aquí tienes algunas canciones de NCT:\n{canciones}")
        except Exception as e:
            dispatcher.utter_message(text="Ocurrió un error al buscar canciones.")
            print(e)

        return []

