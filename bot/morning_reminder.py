#!/usr/bin/env python3
"""
Утреннее напоминание о занятиях в Telegram-группу.
Запускается через GitHub Actions по расписанию (пн, ср в 9:40 МСК).
"""
import os, json, sys, requests
from datetime import datetime, timezone, timedelta

TOKEN   = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

MOSCOW  = timezone(timedelta(hours=3))
now     = datetime.now(MOSCOW)
weekday = now.weekday()  # 0=пн … 6=вс
day_key = ['пн','вт','ср','чт','пт','сб','вс'][weekday]

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, 'schedule.json'), encoding='utf-8') as f:
    schedule = json.load(f)

today = schedule.get(day_key, [])
if not today:
    print(f"Сегодня ({day_key}) занятий нет — ничего не отправляем.")
    sys.exit(0)

lines = ["🌊 <b>Доброе утро!</b> Сегодня занятия:", ""]
for cls in today:
    lines.append(f"🕐 <b>{cls['time']}</b> — {cls['group']}")
lines += ["", "Ждём всех! Берите хорошее настроение 💃✨"]

text = "\n".join(lines)

resp = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
    timeout=15,
)
data = resp.json()
if data.get("ok"):
    print(f"✅ Отправлено! message_id={data['result']['message_id']}")
else:
    print(f"❌ Ошибка Telegram API: {data}")
    sys.exit(1)
