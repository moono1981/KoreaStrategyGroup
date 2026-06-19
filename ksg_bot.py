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
import random
import os

# Configuration (provided)
TELEGRAM_TOKEN = "8761693245:AAEXlr4MML2U00gDFGRxOm17vHJ95roP8M4"
CHAT_ID = "475983619"

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
GETUPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

# Ensure script runs from its directory so scheduled tasks or calls work from any CWD
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    os.chdir(SCRIPT_DIR)
except Exception:
    pass

# (Legacy) Anthropic placeholders kept but not used when using local idea pool
ANTHROPIC_API_KEY = ""
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
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
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    try:
        resp = requests.post(ANTHROPIC_URL, json=body, headers=headers, timeout=15)
        if resp.ok:
            data = resp.json()
            # expected response: data["content"][0]["text"]
            text = ''
            try:
                text = data.get('content', [])[0].get('text','') if isinstance(data.get('content'), list) else ''
            except Exception:
                text = ''
            if not text:
                # fallback to other fields
                text = data.get('completion') or data.get('response') or ''
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


def generate_business_ideas_via_claude():
    """Return 3 randomly sampled Korean business ideas from a local pool.

    This replaces remote API calls and guarantees fresh combinations each time.
    """
    IDEA_POOL = [
        # 연구부문 아이디어 (policy research, data analysis, survey)
        "(연구) 시민행동 기반 정책시뮬레이터 개발 — 정책 선택 효과 예측 파일럿",
        "(연구) 지역사회 복지 수요 조사 및 데이터 시각화 서비스",
        "(연구) 공공 데이터 품질 진단 보고서 서비스",
        "(연구) 교육정책 효과성 장기추적 연구 프로젝트",
        "(연구) 디지털 참여 분석을 통한 시민 의견 분류 연구",
        "(연구) 기후정책 비용편익 분석 모델링 연구",
        "(연구) 사회지표 기반 지역발전 인사이트 리포트",
        "(연구) 공공서비스 이용자 여정 맵핑 및 개선안 제안",
        "(연구) 데이터 거버넌스 설계 및 표준화 연구",
        "(연구) 설문·패널 결합을 통한 정책수혜자 분석",
        "(연구) 빅데이터 기반 정책리스크 조기경보 시스템",
        "(연구) 디지털 시대의 정보확산 영향 평가 연구",
        "(연구) 고령사회 대응 공공서비스 연구 파일럿",
        "(연구) 지역별 고용·산업 변화 분석 프로젝트",
        "(연구) 공공의사결정용 시나리오 모델 개발",
        # 과제수행부문 아이디어 (government projects, PMO)
        "(과제수행) 공공 PMO 표준 템플릿 + KPI 대시보드 패키지",
        "(과제수행) 소규모 지방자치단체 대상 프로젝트 관리 교육 패키지",
        "(과제수행) 예산 집행 모니터링 자동화 서비스",
        "(과제수행) 공공사업 리스크 평가 및 경감 계획 수립",
        "(과제수행) 데이터 기반 사업성과 측정 매뉴얼 개발",
        "(과제수행) 원격 협업 중심의 프로젝트 운영 모델 도입 컨설팅",
        "(과제수행) 참여형 정책 수행을 위한 이해관계자 워크숍 운영",
        "(과제수행) 정부기관 맞춤형 보고서 자동화 도구 개발",
        "(과제수행) 사회성과연계채권(SIB) 타당성 분석 지원",
        "(과제수행) 공공 민관협력(PPP) 프로젝트 구조 설계 지원",
        "(과제수행) 대국민 참여 설계 및 실행 지원 서비스",
        "(과제수행) 데이터 품질 개선 컨설팅 및 교육",
        "(과제수행) 프로젝트 성과 예측 모델 개발 파일럿",
        "(과제수행) 공공 조달 프로세스 최적화 컨설팅",
        "(과제수행) 지역경제 활성화를 위한 사업기획 패키지",
        # 정치컨설팅 아이디어 (election strategy, public opinion, campaign)
        "(정치컨설팅) 지역 맞춤형 유권자 세분화 및 메시지 전략",
        "(정치컨설팅) 디지털 여론 모니터링 및 리스크 대응 플랫폼",
        "(정치컨설팅) 오프라인 지역 네트워크 기반 유세 기획",
        "(정치컨설팅) 정책-감성 결합 메시지 테스트 캠페인",
        "(정치컨설팅) 정치 이슈 영향도 시뮬레이션 리포트",
        "(정치컨설팅) 청년층 타겟 디지털 참여 캠페인 설계",
        "(정치컨설팅) 언론·SNS 통합 모니터링 리포트 서비스",
        "(정치컨설팅) 위기상황 대응 시나리오 및 대변인 훈련",
        "(정치컨설팅) 지역 의제 발굴을 위한 시민 포커스그룹",
        "(정치컨설팅) 캠페인 데이터 분석을 통한 자원배분 최적화",
        "(정치컨설팅) 후보자 공약 효과성 검증 파일럿 연구",
        "(정치컨설팅) 선거 후 여론 관리 및 신뢰 회복 전략",
        "(정치컨설팅) 지역별 커뮤니케이션 채널 최적화 프로젝트",
        "(정치컨설팅) 정책 홍보용 시각화 콘텐츠 제작 패키지",
        "(정치컨설팅) 지역 현안 기반 공감형 스토리텔링 캠페인",
        # additional mixed ideas to reach 50+
        "(연구) 공공데이터 기반 스타트업 인사이트 보고서",
        "(연구) 소외계층 정책수혜 분석 및 개선안 제안",
        "(과제수행) 거버넌스 개선을 위한 조직 역량 진단",
        "(과제수행) 다기관 협업을 위한 통합 커뮤니케이션 플랫폼",
        "(정치컨설팅) 지역별 핵심 이슈 데이터 지도 제작",
        "(연구) 정책실험(랜덤화) 설계 및 효과 분석 지원",
        "(과제수행) 디지털 전환 지원을 위한 역량 강화 교육",
        "(정치컨설팅) 시민참여형 공약 검증 플랫폼 구축",
        "(연구) 이슈 중심 미시경제 분석 프로젝트",
        "(과제수행) 복합 프로젝트 일정 최적화 솔루션",
        "(정치컨설팅) 유권자 신뢰 회복을 위한 커뮤니케이션 로드맵",
        "(연구) 스마트시티 데이터 거버넌스 연구",
        "(과제수행) 대민서비스 개선을 위한 사용자 조사 패키지",
        "(정치컨설팅) 선거 후 정책지지율 추적 리포트",
        "(연구) 공공재정 효율성 분석 프로젝트",
        "(정치컨설팅) 이슈별 옹호 전략 설계 서비스"
    ]

    # pick 3 distinct ideas randomly
    try:
        picks = random.sample(IDEA_POOL, 3)
        return picks
    except Exception:
        # fallback to defaults
        return [IDEAS['연구'], IDEAS['과제수행'], IDEAS['정치컨설팅']]


def start_polling():
    """Start long-polling Telegram getUpdates and dispatch commands."""
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
                        offset = upd.get('update_id', offset) + 1
            except Exception as e:
                print('폴링 오류:', e)
            time.sleep(2)
    except KeyboardInterrupt:
        print('\n리스닝 중지 (Ctrl+C)')


def handle_update(update):
    """Process a single Telegram update dict and respond accordingly."""
    msg = update.get('message') or update.get('edited_message')
    if not msg:
        return
    text = msg.get('text', '')
    if not text:
        return
    chat = msg.get('chat', {})
    cid = chat.get('id')
    if not cid:
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
        body = '💡 새 사업 아이디어:\n' + '\n'.join([f"{i+1}. {it}" for i, it in enumerate(ideas)])
        send_message(body, chat_id=cid)
    elif cmd == '/status':
        body = '📊 전체 프로젝트 현황:\n' + '\n'.join([f"- {p['name']}: {p['status']} ({p['progress']}%)" for p in PROJECT_STATUS])
        send_message(body, chat_id=cid)
    elif cmd == '/help':
        body = '/morning, /afternoon, /evening, /idea, /status, /help'
        send_message(body, chat_id=cid)
    else:
        send_message('알 수 없는 명령어입니다. /help 로 명령어 목록을 확인하세요.', chat_id=cid)


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
