import requests
import json

character = input("Guh: ")
search = input("FAH: ")
url = f"https://spire-codex.com/api/cards?color={character}&rarity=Ancient&search={search}&lang=eng"

response = requests.get(url)

if response.status_code == 200:
    spire = response.json()
    slay = json.dumps(spire, indent=4)
    print(slay)
else:
    print(f"Error: {response.status_code}")