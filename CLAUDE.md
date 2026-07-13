# Движение Океана / OceanMove — CRM Project Context

## Studio Schedule (расписание занятий)

| Группа      | Дни и время                                      |
|-------------|--------------------------------------------------|
| Малыши      | Вт 18:00, Сб 12:00                               |
| Младшие     | Пн 18:00, Ср 18:00, Пт 18:00, Сб 13:00          |
| Средние     | Пт 19:00                                         |
| Подростки   | Ср 19:00, Сб 18:00                               |

**JS weekday mapping**: 0=Вс, 1=Пн, 2=Вт, 3=Ср, 4=Чт, 5=Пт, 6=Сб

This schedule is mirrored in the `MOVE_SCH` and `SCH` constants in `crm.html`.
Any patch, date-alignment, or calendar logic MUST use these slots.

## Tech Stack

- Single-file CRM: `crm.html` (~5100+ lines)
- Hosted on GitHub Pages from branch `claude/crm-card-import-preserve-k1ev6r`
- **Push rule**: always push to BOTH the feature branch AND `main`:
  ```
  git push origin claude/crm-card-import-preserve-k1ev6r
  git push origin claude/crm-card-import-preserve-k1ev6r:main
  ```
- Firebase Realtime DB: `https://ocean-crm-c8bcf-default-rtdb.europe-west1.firebasedatabase.app/crm.json`
- localStorage key: `ocean_crm_v3` (clients), `ocean_last_save` (timestamp)
- `INITIAL_DATA` in HTML = 259 clients (compact JSON, embedded for offline load)

## Client Statuses

| Status     | Meaning                              |
|------------|--------------------------------------|
| `new`      | Just added, not yet contacted        |
| `trial`    | Trial lesson scheduled               |
| `arrived`  | Came to trial, not yet bought        |
| `bought`   | Bought membership                    |
| `callback` | Call back scheduled                  |
| `later`    | Coming back later                    |
| `declined` | Not interested                       |

## Telegram Bot (n8n)

- Bot runs on the user's own **n8n server** — workflows stored in `bot/n8n/`:
  - `oceanmove-daily.json`: morning digest (10:00 MSK) to admin + class-day reminders to parent group chats
  - `oceanmove-commands.json`: replies to `/today`, `/trials`, `/renewals`, `/id`, `/help`
  - `oceanmove-assistant.json`: AI assistant for parents (**YandexGPT** — OpenRouter/foreign LLMs are geo-blocked from RU servers) — chats, consults, captures trial-booking leads. **Polling mode, not webhooks**: the user's n8n runs on plain http, and Telegram Trigger requires HTTPS (`Bad Request: bad webhook: An HTTPS URL must be provided`), so a Schedule Trigger (every minute) → «Проверить сообщения» Code node calls Telegram `getUpdates`; offset stored in Firebase `/bot_offset`; only private chats are answered (bot stays silent in groups). Conversation memory in Firebase `/chats/<chat_id>` (last 16 msgs + `parent`/`updated`/`leadSaved`/`paused`); YandexGPT auth via n8n Header Auth credential (`Authorization: Api-Key <key>`); replies sent via the Telegram node (credential), so the bot token only lives in the getUpdates Code node; lead capture via `#LEAD#{...}` marker parsed + validated (needs child_name+parent_name+10-digit phone) out of the reply, then `Сохранить заявку` calls the save-lead sub-workflow. CRM reads `/chats` in a «💬 Диалоги бота» modal (`openBotChats`); «🙋 Взять на себя» PATCHes `paused:true` so the «Бот на паузе?» IF node keeps the bot silent while the admin handles the chat
  - `oceanmove-save-lead.json`: sub-workflow tool (`save_lead`) — writes each lead to Firebase `/inbox` + a Google Sheet
- **Lead inbox flow**: assistant writes leads to Firebase branch `/inbox` (atomic POST, never overwrites the main `clients` array). CRM reads `INBOX_URL` on load + polls every 60s, shows them in a «📨 Заявки из бота» block atop Reminders; `importBotLead(key)` creates a `new` client (channel «Telegram-бот») and DELETEs the inbox key; `dismissBotLead(key)` just removes it
- Setup instructions: `bot/README.md`
- Bot reads the same Firebase `crm.json` as the CRM; renewal logic mirrors `isAbonementEndToday()` in `crm.html`
- The `SCHEDULE` constant inside both workflow Code nodes mirrors the studio schedule above — update all copies when the schedule changes
- Chat IDs are configured inside the «Собрать сообщения» Code node on the n8n server (not in the repo)

## Patch History

- `patch_fix_schedule_july9_v1` (55s): Aligns future trial dates for `trial`-status clients to valid schedule slots
- `patch_fix_schedule_july9_v2` (57s): Restores original historical trial dates for 7 arrived clients wrongly moved by v1
- `patch_fix_schedule_july9_v3` (2s): Clears `2026-07-07` trial dates for `trial`-status clients (v1 artifacts); fixes Малыши→Средние for Пт 19:00 slots
- `patch_fix_schedule_july9_v4` (2s): Restores original trial dates from `INITIAL_DATA` by client id for all `trial`-status clients — fixes v1 running on July 8 and pushing dates to the "nearest slot" (e.g. July 14) instead of July 9
