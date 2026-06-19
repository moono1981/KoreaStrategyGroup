#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ksg_bot.py

Simple Telegram briefing bot for Korea Strategy Group.
Sends 오전/오후/저녁 브리핑 messages via Telegram Bot API using requests only.
All data hardcoded inline.
"""
import requests
import datetime
import sys
import time
import argparse

# Configuration (provided)
TELEGRAM_TOKEN = "8761693245:AAEXlr4MML2U00gDFGRxOm17vHJ95roP8M4"
CHAT_ID = "475983619"

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
GETUPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

# Anthropic / Claude
ANTHROPIC_API_KEY = "sk-ant-api03-RmF...7AAA"
ANTHROPIC_URL = "https://api.anthropic.com/v1/complete"
ANTHROPIC_MODEL = "claude-sonnet-4-6"


def send_message(text, chat_id=None):
    cid = chat_id or CHAT_ID
    payload = {"chat_id": cid, "text": text}
    try:
        r = requests.post(API_URL, json=payload, timeout=10)
        if r.ok:
            print(f"전송 완료 -> chat_id={cid}")
        else:
            print("전송 실패:", r.status_code, r.text)
    except Exception as e:
        print("전송 중 오류:", e)


# Hardcoded data for briefings
TODAY = datetime.date.today().strftime('%Y-%m-%d')

MEETINGS_TODAY = [
    {"time":"09:00","title":"전사 월례회의","attendees":"CEO, 전직원","note":"월간 성과/계획 공유"},
    {"time":"11:00","title":"연구부문 회의","attendees":"부문장, 연구팀","note":"진행 중 연구 점검"},
    {"time":"15:00","title":"프로젝트 PM 미팅","attendees":"PM, 담당자","note":"주간 마일스톤 점검"}
]

PROJECT_STATUS = [
    {"name":"스마트도시 여론분석","status":"진행중","progress":42},
    {"name":"공공사업 PMO 지원","status":"진행중","progress":55},
    {"name":"디지털 캠페인 성과분석","status":"완료","progress":100}
]

IDEAS = {
    "연구": "시민행동 데이터 기반 정책제안 모델 개발 — 소규모 파일럿으로 시작",
    "과제수행": "공공기관 대상 PMO 패키지 서비스 제공 — 표준 템플릿과 KPI 대시보드 포함",
    "정치컨설팅": "디지털 유권자 참여 플랫폼 시범 운영 — 지역별 타깃 메시징 검증"
}

DAILY_RESULTS = {
    "summary": "오늘 팀 주요 산출: 정책보고서 1건 제출, 캠페인 데이터 수집 완료, 고객 미팅 2건",
    "next": "내일 준비사항: PMO 자료 보완, 연구 데이터 검증, 클라이언트 제안서 초안 완성"
}


def compose_morning():
    lines = [f"📣 오전 브리핑 — {TODAY} (9:00)", "", "오늘의 회의 일정:"]
    for i, m in enumerate(MEETINGS_TODAY, 1):
        lines.append(f"{i}. {m['time']} - {m['title']} • 참석자: {m['attendees']} — {m['note']}")
    lines.append("")
    lines.append("주요 프로젝트 현황:")
    for p in PROJECT_STATUS:
        lines.append(f"- {p['name']}: {p['status']} (진행 {p['progress']}%)")
    return "\n".join(lines)


def compose_afternoon():
    lines = [f"💡 오후 브리핑 — {TODAY} (13:00)", "", "오늘의 사업 아이디어 (연구/과제/정치컨설팅)", ""]
    lines.append(f"1) 연구: {IDEAS['연구']}")
    lines.append(f"2) 과제수행: {IDEAS['과제수행']}")
    lines.append(f"3) 정치컨설팅: {IDEAS['정치컨설팅']}")
    return "\n".join(lines)


def generate_business_ideas_via_claude():
    """Call Anthropic Claude to generate 3 Korean business ideas relevant to divisions."""
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "YOUR_ANTHROPIC_API_KEY":
        # fallback
        return [IDEAS['연구'], IDEAS['과제수행'], IDEAS['정치컨설팅']]

    prompt = (
        "다음 세 부문(연구, 과제수행, 정치컨설팅)에 대해 각 부문별로 실행 가능한 사업 아이디어를 하나씩, "
        "한국어로 간결하게 3개 항목으로 출력하라. 각 항목은 한 줄로 작성하라."
    )
    body = {
        "model": ANTHROPIC_MODEL,
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.7
    }
    headers = {"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json"}
    try:
        resp = requests.post(ANTHROPIC_URL, json=body, headers=headers, timeout=10)
        if resp.ok:
            data = resp.json()
            # naive extraction
            text = data.get('completion') or data.get('text') or data.get('response') or ''
            if not text and isinstance(data.get('choices'), list):
                text = data['choices'][0].get('text','')
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            return lines[:3] if lines else [IDEAS['연구'], IDEAS['과제수행'], IDEAS['정치컨설팅']]
        else:
            print('Claude API 실패:', resp.status_code, resp.text)
            return [IDEAS['연구'], IDEAS['과제수행'], IDEAS['정치컨설팅']]
    except Exception as e:
        print('Claude 호출 오류:', e)
        return [IDEAS['연구'], IDEAS['과제수행'], IDEAS['정치컨설팅']]


def compose_evening():
    lines = [f"🌙 저녁 브리핑 — {TODAY} (18:00)", "", "오늘의 성과 요약:", DAILY_RESULTS['summary'], "", "내일 준비사항:", DAILY_RESULTS['next']]
    return "\n".join(lines)


def menu():
    print("KS G Bot — 간단 메뉴")
    print("1: 오전 브리핑 전송")
    print("2: 오후 브리핑 전송")
    print("3: 저녁 브리핑 전송")
    print("4: 전체 전송")
    print("0: 종료")
    try:
        choice = input('선택> ').strip()
    except (EOFError, KeyboardInterrupt):
        print('\n종료')
        sys.exit(0)
    return choice


def main():
    while True:
        c = menu()
        if c == '1':
            print('오전 브리핑 전송 중...')
            send_message(compose_morning())
        elif c == '2':
            print('오후 브리핑 전송 중...')
            send_message(compose_afternoon())
        elif c == '3':
            print('저녁 브리핑 전송 중...')
            send_message(compose_evening())
        elif c == '4':
            print('전체 브리핑 전송 중...')
            send_message(compose_morning())
            send_message(compose_afternoon())
            send_message(compose_evening())
        elif c == '0':
            print('종료')
            break
        else:
            print('유효하지 않은 선택입니다.')


def handle_update(update):
    # parse incoming update from Telegram
    msg = update.get('message') or update.get('edited_message')
    if not msg:
        return
    text = msg.get('text','').strip()
    chat = msg.get('chat',{})
    cid = chat.get('id')
    if not text or not cid:
        return
    cmd = text.split()[0].lower()
    if cmd == '/morning':
        send_message(compose_morning(), chat_id=cid)
    elif cmd == '/afternoon':
        send_message(compose_afternoon(), chat_id=cid)
    elif cmd == '/evening':
        send_message(compose_evening(), chat_id=cid)
    elif cmd == '/idea':
        ideas = generate_business_ideas_via_claude()
        body = "💡 새 사업 아이디어:\n" + "\n".join([f"{i+1}. {it}" for i,it in enumerate(ideas)])
        send_message(body, chat_id=cid)
    elif cmd == '/status':
        body = '📊 전체 프로젝트 현황:\n' + "\n".join([f"- {p['name']}: {p['status']} ({p['progress']}%)" for p in PROJECT_STATUS])
        send_message(body, chat_id=cid)
    elif cmd == '/help':
        body = '/morning, /afternoon, /evening, /idea, /status, /help'
        send_message(body, chat_id=cid)
    else:
        send_message('알 수 없는 명령어입니다. /help 로 명령어 목록을 확인하세요.', chat_id=cid)


def start_polling():
    print('봇 리스닝 중... (Ctrl+C로 종료)')
    offset = None
    try:
        while True:
            try:
                params = {'limit': 10}
                if offset is not None:
                    params['offset'] = offset
                r = requests.get(GETUPDATES_URL, params=params, timeout=10)
                if not r.ok:
                    print('getUpdates 실패', r.status_code, r.text)
                else:
                    data = r.json()
                    for upd in data.get('result', []):
                        handle_update(upd)
                        offset = upd['update_id'] + 1
            except Exception as e:
                print('폴링 오류:', e)
            time.sleep(2)
    except KeyboardInterrupt:
        print('\n리스닝 중지 (Ctrl+C)')



def run_command_arg(cmd):
    c = cmd.lower() if cmd else ''
    if c == 'morning':
        send_message(compose_morning())
    elif c == 'afternoon':
        send_message(compose_afternoon())
    elif c == 'evening':
        send_message(compose_evening())
    elif c in ('all','full','전체'):
        send_message(compose_morning())
        send_message(compose_afternoon())
        send_message(compose_evening())
    else:
        print('알 수 없는 인수:', cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KSG Telegram Bot')
    parser.add_argument('--listen', action='store_true', help='Start Telegram polling listener')
    parser.add_argument('cmd', nargs='?', help="Optional command: morning|afternoon|evening|all")
    args = parser.parse_args()

    if args.listen:
        start_polling()
    elif args.cmd:
        run_command_arg(args.cmd)
    else:
        main()
