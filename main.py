import requests
import re
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

travel_date = input("What year would you want to travel to? Type the date in this format YYYY-MM-DD\n")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{travel_date}")
billboard_html = response.text
soup = BeautifulSoup(billboard_html, "html.parser")
all_titles = soup.select(selector="li .c-title")
top_100_titles = [re.sub("[\n,\t]", "", title.text) for title in all_titles]

# connect to spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     redirect_uri=REDIRECT_URI,
                     show_dialog=True,
                     cache_path="token.txt",
                     scope="playlist-modify-private"))

user_id = sp.current_user()["id"]

song_uri = []
year = travel_date.split("-")[0]
for index, song_title in enumerate(top_100_titles):
    response = sp.search(q=f"track:{song_title}year:{year}", type="track")
    try:
        uri = response["tracks"]["items"][0]["uri"]
        song_uri.append(uri)
    except IndexError:
        print(f"{song_title} does not exist in spotify")

print(song_uri)

#create playlist on spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{travel_date} Billboard 100", description="Billboard Hot 100 during a specific time", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uri)


