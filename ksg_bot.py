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

# Configuration (provided)
TELEGRAM_TOKEN = "8761693245:AAEXlr4MML2U00gDFGRxOm17vHJ95roP8M4"
CHAT_ID = "475983619"

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def send_message(text):
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(API_URL, json=payload, timeout=10)
        if r.ok:
            print("전송 완료")
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


if __name__ == '__main__':
    main()
