import urllib.request
import json

try:
    response = urllib.request.urlopen('http://localhost:8000/api/colheitadeira/')
    data = json.load(response)
    print(f'Count: {len(data)}')
    for item in data:
        print(f'  - {item.get("maquina_id")}: {item.get("modelo", {}).get("nome")} (op: {item.get("status_de_operacao", {}).get("em_operacao")})')
except Exception as e:
    print(f'Error: {e}')