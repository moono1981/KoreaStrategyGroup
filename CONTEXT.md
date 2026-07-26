# 코리아전략그룹 프로젝트 컨텍스트

## 프로젝트 위치
- 로컬: D:\Claude_VSCode_20260618\KCG\KoreaStrategyGroup\
- GitHub: https://github.com/moono1981/KoreaStrategyGroup
- 라이브 웹사이트: https://moono1981.github.io/KoreaStrategyGroup/

## 주요 파일 목록
- `dashboard.html`: 직원 50명 대시보드 (직원카드/조직도/프로젝트/인재개발 탭)
- `index.html`: 회사 랜딩페이지
- `operations.html`: 회사 운영 시스템 (회의/평가/사업운영)
- `talent.html`: 인재개발 역량 테이블
- `ksg_bot.py`: 텔레그램 봇 (명령어: /morning /afternoon /evening /idea /status /help)
- `ksg_scheduler.py`: 자동 스케줄러 (09:00/13:00/18:00)
- `ksg_ai_assistant.py`: 텔레그램/스크립트용 AI 비서 (Gemini API 사용, 모델: gemini-3.5-flash)
- `정관_코리아전략그룹.docx`: 회사 정관 Word 문서
- `employees.json`: 직원 50명 데이터
- `projects.json`: 프로젝트 10개 데이터
- `divisions.json`: 3개 부문 데이터
- `company.json`: 회사 정보

## 텔레그램 봇 정보
- Bot: @KSG_Daily_Bot
- Token: 8761693245:AAEXlr4MML2U00gDFGRxOm17vHJ95roP8M4
- Chat ID: 475983619

## 실행 방법
- 봇 리스닝: `python ksg_bot.py --listen`
- 자동 스케줄러: `python ksg_scheduler.py`
- 대시보드 열기: `start dashboard.html`

## 2026-07-26 진행 상황
- `ksg_procurement.py`의 나라장터/심사위원 브리핑 모듈을 활성화하고 `.env`의 `PUBLIC_DATA_API_KEY`를 사용하도록 연결함.
- Gmail SMTP 테스트는 성공했고 실제 발송도 확인됨.
- Judges API 재시험 결과: `fetch_judges()`가 HTTP 500 응답을 반환하여 현재는 실데이터 수신이 실패 중임.
- 내일 재시도 예정: judges API 엔드포인트 상태와 API 키/파라미터 재검증.

## 다음 할 일
1. 텔레그램 AI 비서 기능 (질문하면 Gemini가 답변; `ksg_ai_assistant.py` — 모델: gemini-3.5-flash)
2. 웹사이트 프로젝트 현황 실시간 반영
3. 사업계획서 작성
4. 수메르 경제사 논문 (별도 채팅)

## GitHub 푸시 방법
```
cd D:\Claude_VSCode_20260618\KCG\KoreaStrategyGroup
git add .
git commit -m "업데이트 내용"
git push
```

