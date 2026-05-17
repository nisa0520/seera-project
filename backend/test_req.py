import urllib.request
import urllib.error
import json

data = json.dumps({"session_id": 1}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/recommend', data=data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    response = urllib.request.urlopen(req)
    print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")
    print(e.read().decode())
