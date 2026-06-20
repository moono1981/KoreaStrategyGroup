#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ksg_ai_assistant.py

Telegram AI assistant using Anthropic Claude (polling, requests only).
Features:
- Polls Telegram for messages every 2 seconds.
- For any user text, forwards to Anthropic Claude and returns the answer.
- Special commands: /start, /help, /clear
- Keeps per-chat conversation history (last 10 messages).

Configuration: edit the tokens below as needed.
"""
import requests
import time
import os
import sys
from collections import deque

# .env will be loaded by the loader defined below

# Configuration (from env or fallback)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', "8761693245:AAEXlr4MML2U00gDFGRxOm17vHJ95roP8M4")
CHAT_ID = os.environ.get('CHAT_ID', "475983619")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

SYSTEM_PROMPT = (
    "당신은 코리아전략그룹의 AI 비서입니다. 공공정책, AI, 핀테크, 에너지, 지방행정, 정치컨설팅 분야의 "
    "전문적인 답변을 제공합니다. 간결하고 실용적으로 답하세요."
)

API_URL_SEND = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
API_URL_GETUPDATES = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

# Ensure script runs from its directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    os.chdir(SCRIPT_DIR)
except Exception:
    pass


# Load simple .env if present (KEY=VALUE lines)
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

# GEMINI key loaded after .env
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', os.environ.get('ANTHROPIC_API_KEY', ''))

# Per-chat histories: chat_id (int) -> deque of {'role': 'user'|'assistant', 'content': str}
HISTORIES = {}
HISTORY_MAX = 10


def send_message(text, chat_id=None):
    cid = chat_id or CHAT_ID
    payload = {"chat_id": cid, "text": text}
    try:
        r = requests.post(API_URL_SEND, json=payload, timeout=10)
        if r.ok:
            print(f"전송 완료 -> chat_id={cid}")
        else:
            print("전송 실패:", r.status_code, r.text)
    except Exception as e:
        print("전송 중 오류:", e)


def call_claude(chat_messages):
    """Call Anthropic Claude with the given messages list (role/content dicts).

    chat_messages should be a list like [{'role':'user','content':...}, ...]
    Returns assistant text or error message.
    """
    if not GEMINI_API_KEY:
        return "(Gemini API 키가 설정되어 있지 않습니다.)"

    # Build a single prompt text combining system prompt and recent conversation
    parts = [SYSTEM_PROMPT, '']
    for m in chat_messages:
        role = m.get('role')
        content = m.get('content', '')
        if role == 'user':
            parts.append(f"User: {content}")
        elif role == 'assistant':
            parts.append(f"Assistant: {content}")
    prompt_text = '\n'.join(parts)

    # Gemini request per requested format
    body = {
        "contents": [
            {"parts": [{"text": prompt_text}]}
        ]
    }
    params = {"key": GEMINI_API_KEY}
    headers = {"content-type": "application/json"}
    try:
        resp = requests.post(GEMINI_URL, params=params, json=body, headers=headers, timeout=20)
        if not resp.ok:
            print("Gemini API 실패:", resp.status_code, resp.text)
            return f"(Gemini API 오류 {resp.status_code})"
        data = resp.json()
        # Parse as requested: response['candidates'][0]['content']['parts'][0]['text']
        try:
            candidates = data.get('candidates', [])
            if candidates and isinstance(candidates, list):
                first = candidates[0]
                content = first.get('content') or {}
                # content may be dict with 'parts'
                parts_list = content.get('parts') if isinstance(content, dict) else None
                if parts_list and isinstance(parts_list, list) and len(parts_list) > 0:
                    text = parts_list[0].get('text', '')
                    if text:
                        return text.strip()
        except Exception as e:
            print('응답 파싱 오류:', e)
        # fallback: try other fields
        text = data.get('output') or data.get('response') or ''
        if not text:
            return '(Gemini가 응답하지 않았습니다.)'
        return text.strip()
    except Exception as e:
        print('Gemini 호출 오류:', e)
        return f'(Gemini 호출 오류: {e})'


def ensure_history(chat_id):
    if chat_id not in HISTORIES:
        HISTORIES[chat_id] = deque(maxlen=HISTORY_MAX)
    return HISTORIES[chat_id]


def handle_command(text, chat_id):
    cmd = text.strip().lower()
    if cmd == '/start':
        send_message('안녕하세요. 코리아전략그룹 AI 비서입니다. /help 를 입력하면 사용법을 볼 수 있습니다.', chat_id=chat_id)
    elif cmd == '/help':
        send_message('/start — 안내\n/help — 사용법\n/clear — 대화기록 초기화\n그냥 질문을 보내면 답변을 드립니다.', chat_id=chat_id)
    elif cmd == '/clear':
        HISTORIES.pop(chat_id, None)
        send_message('대화 기록을 초기화했습니다.', chat_id=chat_id)
    else:
        send_message('알 수 없는 명령어입니다. /help 를 참조하세요.', chat_id=chat_id)


def process_message(msg):
    if not msg:
        return
    text = msg.get('text')
    if not text:
        return
    chat = msg.get('chat', {})
    cid = chat.get('id')
    if cid is None:
        return

    if text.strip().startswith('/'):
        print(f'명령 수신: {text} from {cid}')
        handle_command(text, cid)
        return

    # user message -> append to history and call Claude
    print(f'질문 수신 (chat={cid}): {text}')
    hist = ensure_history(cid)
    hist.append({'role': 'user', 'content': text})
    # prepare messages for Claude
    conv = list(hist)
    # call Claude
    send_message('답변을 생성 중입니다... 잠시만 기다려주세요.', chat_id=cid)
    reply = call_claude(conv)
    # append assistant reply to history
    hist.append({'role': 'assistant', 'content': reply})
    send_message(reply, chat_id=cid)


def start_polling():
    print('AI 비서 리스닝 중... (Ctrl+C로 종료)')
    offset = None
    try:
        while True:
            try:
                params = {'limit': 10}
                if offset is not None:
                    params['offset'] = offset
                r = requests.get(API_URL_GETUPDATES, params=params, timeout=10)
                if not r.ok:
                    print('getUpdates 실패', r.status_code, r.text)
                else:
                    data = r.json()
                    for upd in data.get('result', []):
                        # process message
                        msg = upd.get('message') or upd.get('edited_message')
                        process_message(msg)
                        offset = upd.get('update_id', offset) + 1
            except Exception as e:
                print('폴링 오류:', e)
            time.sleep(2)
    except KeyboardInterrupt:
        print('\n리스닝 중지 (Ctrl+C)')


if __name__ == '__main__':
    # Allow overriding GEMINI key via env at runtime
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', GEMINI_API_KEY)
    try:
        start_polling()
    except Exception as e:
        print('종료: ', e)
