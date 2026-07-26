#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ksg_procurement.py

Procurement briefing, task management, and Gmail utility for Korea Strategy Group.

Features:
- Gmail SMTP test and send
- 나라장터 bid briefing (requires PUBLIC_DATA_API_KEY)
- 심사위원 judge announcement briefing
- Telegram task assignment and tracking
- Telegram email instruction confirmation flow
- Daily scheduler support (10:00 briefing + 18:00 report)

Usage:
  python ksg_procurement.py --to EMAIL [--subject SUBJECT] [--body BODY] [--send]
  python ksg_procurement.py --briefings
  python ksg_procurement.py --scheduler
  python ksg_procurement.py --telegram-listen
"""

import argparse
import datetime
import json
import os
import re
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


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(SCRIPT_DIR, "tasks.json")
PENDING_EMAILS = {}


def _load_dotenv(path=None):
    """Load environment variables from .env file, tolerating encoding issues."""
    try:
        if path is None:
            path = os.path.join(SCRIPT_DIR, ".env")
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


# Task management

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        save_tasks([])
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as handle:
        json.dump(tasks, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def create_task(assignee, task, deadline=None, status="pending"):
    tasks = load_tasks()
    task_id = f"T{datetime.datetime.now().strftime('%y%m%d%H%M%S')}{uuid.uuid4().hex[:4]}"
    task_record = {
        "id": task_id,
        "assignee": assignee,
        "task": task,
        "deadline": deadline,
        "status": status,
        "created_at": datetime.date.today().isoformat(),
        "completed_at": None,
    }
    tasks.append(task_record)
    save_tasks(tasks)
    return task_record


def list_pending_tasks():
    return [task for task in load_tasks() if task.get("status") != "completed"]


def mark_task_done(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.date.today().isoformat()
            save_tasks(tasks)
            return True
    return False


def get_task_status_summary():
    tasks = load_tasks()
    pending = [task for task in tasks if task.get("status") != "completed"]
    completed_today = [task for task in tasks if task.get("status") == "completed" and task.get("completed_at") == datetime.date.today().isoformat()]
    overdue = []
    today = datetime.date.today()
    for task in pending:
        deadline = task.get("deadline")
        if deadline:
            try:
                if datetime.date.fromisoformat(deadline) < today:
                    overdue.append(task)
            except ValueError:
                pass
    return {
        "total": len(tasks),
        "pending": len(pending),
        "completed_today": len(completed_today),
        "overdue": len(overdue),
        "overdue_items": overdue,
        "pending_items": pending,
    }


def compose_task_summary():
    summary = get_task_status_summary()
    lines = [
        f"Task Summary: pending={summary['pending']} completed_today={summary['completed_today']} overdue={summary['overdue']}",
    ]
    if summary["pending_items"]:
        lines.append("Pending tasks:")
        for task in summary["pending_items"][:5]:
            deadline = task.get("deadline") or "-"
            lines.append(f"- {task['id']} | {task['assignee']} | {task['task']} | due:{deadline}")
    else:
        lines.append("No pending tasks.")
    return "\n".join(lines)


def compose_daily_report():
    summary = get_task_status_summary()
    lines = [
        f"📊 Daily Report ({datetime.date.today().isoformat()})",
        f"- Completed today: {summary['completed_today']}",
        f"- Pending: {summary['pending']}",
        f"- Overdue: {summary['overdue']}",
    ]
    if summary["pending_items"]:
        lines.append("Pending tasks:")
        for task in summary["pending_items"][:8]:
            deadline = task.get("deadline") or "-"
            lines.append(f"- {task['id']} | {task['assignee']} | {task['task']} | due:{deadline}")
    else:
        lines.append("- No pending tasks")
    return "\n".join(lines)


# API integrations

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


def send_telegram_message_to_chat(chat_id, text):
    if not requests or not TELEGRAM_TOKEN or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception:
        return False


def handle_telegram_command(text, chat_id):
    if not text:
        return None

    if text.startswith("/assign"):
        tokens = text.split()
        if len(tokens) < 3:
            return "사용법: /assign @teamA 작업내용 deadline:2026-07-30"
        assignee = tokens[1]
        deadline = None
        task_tokens = tokens[2:]
        if task_tokens and task_tokens[-1].startswith("deadline:"):
            deadline = task_tokens[-1].split(":", 1)[1].strip()
            task_tokens = task_tokens[:-1]
        task_text = " ".join(task_tokens).strip()
        if not task_text:
            return "작업 내용을 입력해 주세요."
        task = create_task(assignee, task_text, deadline=deadline)
        return f"Task assigned: {task['id']} | assignee={assignee} | task={task_text} | deadline={deadline or '-'}"

    if text.startswith("/tasks"):
        pending = list_pending_tasks()
        if not pending:
            return "No pending tasks."
        lines = ["Pending tasks:"]
        for task in pending:
            deadline = task.get("deadline") or "-"
            lines.append(f"- {task['id']} | {task['assignee']} | {task['task']} | due:{deadline}")
        return "\n".join(lines)

    if text.startswith("/done"):
        task_id = text.split(maxsplit=1)[1].strip() if len(text.split()) > 1 else ""
        if not task_id:
            return "사용법: /done 태스크ID"
        ok = mark_task_done(task_id)
        return f"Task marked complete: {task_id}" if ok else f"Task not found: {task_id}"

    if text.startswith("/status"):
        return compose_task_summary()

    if text.startswith("/email"):
        match = re.match(r"/email\s+to:(.+?)\s+subject:(.+?)\s+body:(.+)$", text, re.I)
        if not match:
            return "사용법: /email to:받는사람 subject:제목 body:내용"
        recipient, subject, body = match.groups()
        PENDING_EMAILS[chat_id] = {"to": recipient.strip(), "subject": subject.strip(), "body": body.strip()}
        return ("Email preview:\n" f"To: {recipient.strip()}\n" f"Subject: {subject.strip()}\n" f"Body: {body.strip()}\n\n" "Confirm with /confirm or cancel with /cancel")

    if text == "/confirm":
        pending = PENDING_EMAILS.pop(chat_id, None)
        if not pending:
            return "No pending email to confirm."
        sender = GMAIL_USER
        password = GMAIL_APP_PASSWORD
        if not sender:
            return "GMAIL_USER is not configured."
        if not password:
            return "GMAIL_APP_PASSWORD is not configured."
        msg = build_message(sender, pending["to"], pending["subject"], pending["body"])
        success = send_via_gmail(sender, password, msg, dry_run=False)
        return "Email sent successfully" if success else "Email sending failed."

    if text == "/cancel":
        if chat_id in PENDING_EMAILS:
            del PENDING_EMAILS[chat_id]
        return "Email cancelled."

    return None


def poll_telegram_commands(interval=5):
    if not requests or not TELEGRAM_TOKEN:
        print("Telegram token not configured; skipping Telegram polling")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    offset = None
    while True:
        params = {"limit": 20}
        if offset is not None:
            params["offset"] = offset
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            for update in data.get("result", []):
                update_id = update.get("update_id")
                if update_id is not None:
                    offset = update_id + 1
                message = update.get("message") or update.get("edited_message")
                if not message:
                    continue
                text = (message.get("text") or "").strip()
                chat_id = message.get("chat", {}).get("id")
                if not text or not chat_id:
                    continue
                response_text = handle_telegram_command(text, chat_id)
                if response_text:
                    send_telegram_message_to_chat(chat_id, response_text)
        except Exception as exc:
            print(f"Telegram polling error: {exc}")
        time.sleep(interval)


def run_briefings(include_task_summary=True):
    """Run bid and judge briefings and optionally include task summary."""
    keywords = ["에너지", "금융", "산업", "재생에너지", "핀테크", "ESG"]
    bids = fetch_bids(keywords, limit=5)
    bid_msg = compose_bids_message(bids)
    print(bid_msg)
    send_telegram_message(bid_msg)

    print()

    judges = fetch_judges(regions=("서울", "경기", "인천"), limit=5)
    judge_msg = compose_judges_message(judges)
    print(judge_msg)
    send_telegram_message(judge_msg)

    if include_task_summary:
        task_summary = compose_task_summary()
        print("\n" + task_summary)
        send_telegram_message(task_summary)


def send_daily_report():
    report = compose_daily_report()
    print(report)
    send_telegram_message(report)


def start_scheduler():
    """Start daily scheduler (10:00 briefing + 18:00 report)."""
    if not schedule:
        print("schedule library not installed; cannot start scheduler")
        return

    schedule.clear()
    schedule.every().day.at("10:00").do(run_briefings)
    schedule.every().day.at("18:00").do(send_daily_report)
    print("ksg_procurement scheduler started; 10:00 briefing + 18:00 report")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScheduler stopped")


def main(argv=None):
    parser = argparse.ArgumentParser(description="KSG Procurement: Gmail + Briefings + Tasks")

    parser.add_argument("--to", help="Send email to recipient")
    parser.add_argument("--subject", default="KSG Procurement Test", help="Email subject")
    parser.add_argument("--body", default="This is a test message from ksg_procurement.", help="Email body")
    parser.add_argument("--send", action="store_true", help="Actually send email (not dry-run)")

    parser.add_argument("--briefings", action="store_true", help="Run bid/judge briefings")
    parser.add_argument("--scheduler", action="store_true", help="Start daily scheduler")
    parser.add_argument("--telegram-listen", action="store_true", help="Start Telegram command listener")

    args = parser.parse_args(argv)

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

    if args.briefings:
        run_briefings()
        return 0

    if args.scheduler:
        start_scheduler()
        return 0

    if args.telegram_listen:
        poll_telegram_commands()
        return 0

    print("Usage:")
    print("  Email:     python ksg_procurement.py --to EMAIL [--subject ...] [--body ...] [--send]")
    print("  Briefings: python ksg_procurement.py --briefings")
    print("  Scheduler: python ksg_procurement.py --scheduler")
    print("  Telegram:  python ksg_procurement.py --telegram-listen")
    return 1


if __name__ == "__main__":
    sys.exit(main())
