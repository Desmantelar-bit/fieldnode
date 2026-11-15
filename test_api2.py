import urllib.request
import json

try:
    response = urllib.request.urlopen('http://localhost:8000/api/leituras/ultimas/')
    data = json.load(response)
    print(f'Count: {len(data)}')
    for item in data[:5]:
        print(f'  - {item.get("maquina_id")}: temp={item.get("temperatura")}, vib={item.get("vibracao")}, rpm={item.get("rpm")}')
except Exception as e:
    print(f'Error: {e}')