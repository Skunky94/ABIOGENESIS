import requests
import json

r = requests.get('http://localhost:8283/v1/agents/agent-3dd9a54f-dc55-4d7f-adc3-d5cbb1aca950/messages?limit=5')
data = r.json()

print('Totale messaggi:', len(data))
print()

for m in data[-3:]:
    role = m.get('role', '?')
    content = m.get('content', '')[:300]
    print(f'[{role}]:')
    print(content)
    print('-' * 50)
