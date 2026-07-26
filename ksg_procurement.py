#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ksg_procurement.py

Procurement briefing and Gmail utility for Korea Strategy Group.

Features:
- Gmail SMTP test and send
- 나라장터 bid briefing (requires PUBLIC_DATA_API_KEY)
- 심사위원 judge announcement briefing
- Daily scheduler support

Usage:
  python ksg_procurement.py --to EMAIL [--subject SUBJECT] [--body BODY] [--send]
  python ksg_procurement.py --briefings              # Run bid/judge briefings
  python ksg_procurement.py --scheduler              # Start daily scheduler (10:00 AM)
"""

import argparse
import datetime
import os
import smtplib
import sys
import time
import uuid
from email.message import EmailMessage

try:
    import requests
except ImportError:
    requests = None

try:
    import schedule
except ImportError:
    schedule = None


def _load_dotenv(path=None):
    """Load environment variables from .env file, tolerating encoding issues."""
    try:
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ[key] = value
    except Exception:
        pass


_load_dotenv()


# Configuration
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
PUBLIC_DATA_API_KEY = os.environ.get("PUBLIC_DATA_API_KEY", "")
PUBLIC_DATA_BASE = os.environ.get("PUBLIC_DATA_BASE", "https://apis.data.go.kr")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")


def build_message(sender, recipient, subject, body):
    """Build an EmailMessage object."""
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


def send_via_gmail(sender, password, msg, dry_run=True):
    """Send email via Gmail SMTP."""
    if dry_run:
        print("Dry run: not sending email. Message preview:\n")
        print(msg.as_string())
        return True

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(sender, password)
            smtp.send_message(msg)
        print("Email sent successfully")
        return True
    except Exception as exc:
        print(f"Failed to send email: {exc}")
        return False


def fetch_bids(keywords, limit=5):
    """Fetch bid announcements from 나라장터 BidPublicInfoService04 API."""
    results = []
    if not requests:
        print("requests library not installed; cannot fetch bids")
        return results
    if not PUBLIC_DATA_API_KEY:
        print("PUBLIC_DATA_API_KEY not set; returning empty bid list")
        return results

    url = PUBLIC_DATA_BASE.rstrip("/") + "/1230000/BidPublicInfoService04/getBidPblancListInfoServc01"
    params = {
        "serviceKey": PUBLIC_DATA_API_KEY,
        "pageNo": 1,
        "numOfRows": limit,
        "_type": "json",
        "srchwrd": " ".join(keywords),
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        if not resp.ok:
            print(f"Bid API request failed: {resp.status_code}")
            return results
        data = resp.json()
        items = []
        try:
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item") or []
        except Exception:
            items = []
        if isinstance(items, dict):
            items = [items]
        for it in items[:limit]:
            title = it.get("bidNtceNm") or it.get("title") or str(it)
            deadline = it.get("ntceEndDt") or it.get("endDt") or it.get("ntceBgnde") or ""
            budget = it.get("estmAmt") or it.get("budget") or it.get("ntceAmt") or ""
            link = it.get("bidNtceUrl") or it.get("url") or ""
            results.append({"title": title, "deadline": deadline, "budget": budget, "link": link})
        return results
    except Exception as e:
        print(f"Error fetching bids: {e}")
        return results


def fetch_judges(regions=("서울", "경기", "인천"), limit=5):
    """Fetch 심사위원 announcements from ScsbidInfoService."""
    results = []
    if not requests:
        print("requests library not installed; cannot fetch judges")
        return results
    if not PUBLIC_DATA_API_KEY:
        print("PUBLIC_DATA_API_KEY not set; returning empty judge list")
        return results

    url = PUBLIC_DATA_BASE.rstrip("/") + "/1230000/ScsbidInfoService/getScsbidListPost"
    params = {
        "serviceKey": PUBLIC_DATA_API_KEY,
        "pageNo": 1,
        "numOfRows": 50,
        "_type": "json",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        if not resp.ok:
            print(f"Judges API request failed: {resp.status_code}")
            return results
        data = resp.json()
        items = []
        try:
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item") or []
        except Exception:
            items = []
        if isinstance(items, dict):
            items = [items]
        for it in items:
            inst = it.get("insttNm") or it.get("agency") or it.get("institution") or ""
            location = it.get("insttAddr") or it.get("addr") or it.get("location") or inst
            if any(r in (inst or "") or r in (location or "") for r in regions):
                title = it.get("title") or it.get("sbjtNm") or str(it)
                deadline = it.get("endDt") or it.get("closeDt") or it.get("openDt") or ""
                link = it.get("url") or it.get("link") or ""
                results.append({"title": title, "institution": inst, "deadline": deadline, "link": link})
                if len(results) >= limit:
                    break
        return results
    except Exception as e:
        print(f"Error fetching judges: {e}")
        return results


def compose_bids_message(items, team_name="TEAM A"):
    """Format bid announcements as a message."""
    lines = [f"📢 {team_name} - 입찰공고 브리핑 ({datetime.date.today()})", ""]
    if not items:
        lines.append("(공고 없음)")
        return "\n".join(lines)
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. {it['title']}")
        if it.get("deadline"):
            lines.append(f"   마감: {it['deadline']}")
        if it.get("budget"):
            lines.append(f"   예산: {it['budget']}")
        if it.get("link"):
            lines.append(f"   링크: {it['link']}")
        lines.append("")
    lines.append("팀: 김민준(팀장), 이서연, 박준호")
    return "\n".join(lines)


def compose_judges_message(items, team_name="TEAM B"):
    """Format judge announcements as a message."""
    lines = [f"📢 {team_name} - 심사위원 공고 브리핑 ({datetime.date.today()})", ""]
    if not items:
        lines.append("(공고 없음)")
        return "\n".join(lines)
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. {it['title']}")
        if it.get("institution"):
            lines.append(f"   기관: {it['institution']}")
        if it.get("deadline"):
            lines.append(f"   마감: {it['deadline']}")
        if it.get("link"):
            lines.append(f"   링크: {it['link']}")
        lines.append("")
    lines.append("팀: 최지원(팀장), 정다은, 한승우")
    return "\n".join(lines)


def send_telegram_message(text):
    """Send message via Telegram if configured."""
    if not requests or not TELEGRAM_TOKEN or not CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception:
        return False


def run_briefings():
    """Run bid and judge briefings, send via email or Telegram."""
    # TEAM A: bid announcements
    keywords = ["에너지", "금융", "산업", "재생에너지", "핀테크", "ESG"]
    bids = fetch_bids(keywords, limit=5)
    bid_msg = compose_bids_message(bids)
    print(bid_msg)
    send_telegram_message(bid_msg)

    print()

    # TEAM B: judge announcements (수도권)
    judges = fetch_judges(regions=("서울", "경기", "인천"), limit=5)
    judge_msg = compose_judges_message(judges)
    print(judge_msg)
    send_telegram_message(judge_msg)


def start_scheduler():
    """Start daily scheduler to run briefings at 10:00 AM."""
    if not schedule:
        print("schedule library not installed; cannot start scheduler")
        return

    schedule.clear()
    schedule.every().day.at("10:00").do(run_briefings)
    print("ksg_procurement scheduler started; running briefings at 10:00 daily")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScheduler stopped")


def main(argv=None):
    parser = argparse.ArgumentParser(description="KSG Procurement: Gmail + Briefings")
    
    # Email mode
    parser.add_argument("--to", help="Send email to recipient")
    parser.add_argument("--subject", default="KSG Procurement Test", help="Email subject")
    parser.add_argument("--body", default="This is a test message from ksg_procurement.", help="Email body")
    parser.add_argument("--send", action="store_true", help="Actually send email (not dry-run)")
    
    # Briefing modes
    parser.add_argument("--briefings", action="store_true", help="Run bid/judge briefings")
    parser.add_argument("--scheduler", action="store_true", help="Start daily scheduler (10:00 AM)")
    
    args = parser.parse_args(argv)

    # Email mode
    if args.to:
        sender = GMAIL_USER
        password = GMAIL_APP_PASSWORD

        if not sender:
            print("Error: GMAIL_USER environment variable not set")
            return 2

        if args.send and not password:
            print("Error: GMAIL_APP_PASSWORD environment variable not set for sending")
            return 2

        msg = build_message(sender, args.to, args.subject, args.body)
        success = send_via_gmail(sender, password, msg, dry_run=not args.send)
        return 0 if success else 1

    # Briefing mode
    if args.briefings:
        run_briefings()
        return 0

    # Scheduler mode
    if args.scheduler:
        start_scheduler()
        return 0

    # No mode specified
    print("Usage:")
    print("  Email:     python ksg_procurement.py --to EMAIL [--subject ...] [--body ...] [--send]")
    print("  Briefings: python ksg_procurement.py --briefings")
    print("  Scheduler: python ksg_procurement.py --scheduler")
    return 1


if __name__ == "__main__":
    sys.exit(main())
