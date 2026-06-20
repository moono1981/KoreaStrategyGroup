import os
import requests
import json

# load .env simple
def _load_dotenv(path='.env'):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln or ln.startswith('#'):
                        continue
                    if '=' in ln:
                        k, v = ln.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        os.environ.setdefault(k, v)
    except Exception:
        pass

_load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', os.environ.get('ANTHROPIC_API_KEY',''))
print('GEMINI_API_KEY prefix:', GEMINI_API_KEY[:10] if GEMINI_API_KEY else '(missing)')

url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
params = {'key': GEMINI_API_KEY}
body = {
    'contents': [
        {'parts': [{'text': '테스트 질의: 최근 한국 공공정책 트렌드 간단히 적어줘.'}]}
    ]
}
headers = {'content-type': 'application/json'}
try:
    r = requests.post(url, params=params, json=body, headers=headers, timeout=20)
    print('status_code=', r.status_code)
    print('response_text=')
    print(r.text)
    try:
        print('\njson=')
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    except Exception:
        pass
except Exception as e:
    print('request error:', e)
