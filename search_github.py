import urllib.request
import json

def search_github(query):
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"Results for: {query}")
            for item in data.get("items", [])[:5]:
                print(f"- {item.get('name')}: {item.get('description')} ({item.get('html_url')})")
            print()
    except Exception as e:
        print(f"Error searching for {query}: {e}")

import urllib.parse
search_github("open source Google Jules")
search_github("AI coding agent")
