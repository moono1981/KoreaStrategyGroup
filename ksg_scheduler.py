#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ksg_scheduler.py

Background scheduler for KSG briefings using the `schedule` library.
Run with: python ksg_scheduler.py
Install dependency: pip install schedule
"""
import os
import time

# Ensure we can import local ksg_bot functions reliably
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    os.chdir(SCRIPT_DIR)
except Exception:
    pass

try:
    import schedule
except Exception:
    print("Missing dependency: install with `pip install schedule`")
    raise

# Import briefing/send functions from ksg_bot
from ksg_bot import send_message, compose_morning, compose_afternoon, compose_evening


def job_morning():
    try:
        send_message(compose_morning())
    except Exception as e:
        print("Morning job error:", e)


def job_afternoon():
    try:
        send_message(compose_afternoon())
    except Exception as e:
        print("Afternoon job error:", e)


def job_evening():
    try:
        send_message(compose_evening())
    except Exception as e:
        print("Evening job error:", e)


def main():
    # Schedule daily jobs
    schedule.clear()
    schedule.every().day.at("09:00").do(job_morning)
    schedule.every().day.at("13:00").do(job_afternoon)
    schedule.every().day.at("18:00").do(job_evening)

    print("KSG scheduler started — jobs scheduled for 09:00, 13:00, 18:00")
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("KSG scheduler stopped")


if __name__ == '__main__':
    main()
