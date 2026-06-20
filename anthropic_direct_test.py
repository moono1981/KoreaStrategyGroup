import os
import requests
import json


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

key = os.environ.get('ANTHROPIC_API_KEY', '')
print('ANTHROPIC_API_KEY prefix:', key[:10] if key else '(missing)')
url = 'https://api.anthropic.com/v1/messages'
body = {
    'model': 'claude-sonnet-4-6',
    'messages': [
        {'role': 'system', 'content': '당신은 코리아전략그룹의 AI 비서입니다. 간결하고 실용적으로 답하세요.'},
        {'role': 'user', 'content': '테스트: 연결 및 권한 확인'}
    ],
    'max_tokens': 300
}
headers = {'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'}
try:
    r = requests.post(url, json=body, headers=headers, timeout=20)
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
