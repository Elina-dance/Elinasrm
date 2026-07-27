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
- localStorage key: `ocean_crm_v3` (clients), `ocean_last_save` (timestamp), `ocean_bonuses` (bonuses)
- «🎁 Бонусы» tab: standalone loyalty ledger in Firebase `/bonuses` (array of {id,name,qty,spent,reward}); Остаток = qty−spent computed; `loadBonuses`/`saveBonuses`/`renderBonuses` in crm.html
- «🕺 Взрослые» tab: adult pre-signup list in Firebase `/adults` (array of {id,name,contact,notes}); `loadAdults`/`saveAdults`/`renderAdults`; @nick→Telegram / phone→WhatsApp link
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
  - `oceanmove-outbox.json`: delivers admin replies. In «Диалоги бота» a send box (`sendAdminMsg`) appends the message to `/chats/<id>` (history) + sets `paused:true`, and pushes it to Firebase `/outbox`; this workflow polls `/outbox` every minute and sends each via the Telegram node (bot), then deletes the key — so the admin can answer parents "as the bot" from the CRM without the token ever touching the browser
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

---

# Онлайн-клуб «Ты — есть Вселенная» — Контент и скрипты

## Параметры клуба
- Старт потока: 1 августа
- Стоимость: 2 490 ₽/месяц
- Бонус при раннем входе: +2 недели в подарок (1,5 месяца за цену одного)
- Реквизиты: +7 918 018-35-14 (Сбербанк, Т-банк), Элина А
- Бонус за задания: +50 баллов на счёт

## Стиль речи Элины
- Живо, тепло, без клише и признаков ИИ
- Без пафоса («раскрой себя», «стань лучшей версией»)
- Короткие предложения, разговорная интонация
- Смайлы умеренно, как в живом общении

## Структура описания тренировки / медитации / контента клуба

```
**ТРЕНИРОВКА: [Прилагательное]**
*[Короткое описание курсивом — что это, что делаем, 1-2 предложения]*

Длительность: X мин

**Результат тренировки:**
✔️ [результат 1]
✔️ [результат 2]

⭐ **Задание:** сними видео 15 секунд или больше, отправь в чат домашних заданий
(Получи +50 баллов на свой счёт)
```

Названия тренировок — прилагательные. Уже использованы: Раскачивающая, Расслабляющая, Тонизирующая, Энергичная, Расширяющая.

## Холодный скрипт — приглашение в клуб

**СМС 1 — Открытие (всем)**
Имя, привет! Меня зовут Элина.
Наткнулась на тебя в рекомендациях, зашла на страницу) У тебя очень эстетичный профиль ☺️
Тебе интересна тема своего тела, женственности, движения? Или сейчас совсем не об этом?)

**СМС 2 — Переход + общий вопрос** (после любого положительного ответа)
Здорово, что ответила 🤍
Кстати, можем перейти на ты? Мне так теплее общаться)
А ты сама чем занимаешься — работа, творчество? И из какого ты города? Интересно познакомиться поближе)

**СМС 3 — Выявление потребности** (после её ответа)
Как здорово! А для себя что-то делаешь — танцы, растяжка, движение? Был ли вообще танцевальный опыт или это что-то новое для тебя?)

**СМС 4 — Нативное предложение** (после её ответа)
Поняла тебя 🤍 Я веду закрытый онлайн-клуб для девушек — про движение, женственность и уверенность в себе.
Тебе было бы интересно узнать подробнее?

**СМС 5 — Инфо + бонус** (если да)
Клуб называется «Ты — есть Вселенная» 🤍
Каждый месяц внутри:
— авторская хореография
— тренировки по растяжке
— медитации и живые созвоны
— тёплый чат участниц
— моя личная обратная связь
Стоимость — 2 490 ₽ в месяц.
Новый поток стартует 1 августа.
Если присоединяешься сейчас — эти две недели дарю в подарок.
Получается 1,5 месяца по цене одного 🤍
Как тебе?

**СМС 6а — Продажа** (готова вступить)
Рада тебя видеть! 🤍
Переводи 2 490 ₽ на номер:
+7 918 018-35-14 (Сбербанк, Т-банк)
После оплаты пришли скриншот — добавлю тебя сразу)

**СМС 6б — Закрытие возражений** (если нет/сомневается)
А что останавливает, если не секрет? 🤍

— Дорого →
С бонусом выходит 1,5 месяца за 2 490 ₽ — меньше 60 ₽ в день. Но не давлю — это должно быть твоё решение 🤍

— Нет времени →
Всё в записи, в своём темпе — 15-20 минут когда удобно. Многие занимаются поздно вечером или в выходные)

— Подумаю →
Конечно! Только уточню — бонус с двумя неделями в подарок действует сейчас, до старта потока 🤍

**СМС 7 — 3 дня бесплатно** (если всё равно нет)
Хорошо, не давлю 🤍
Могу подарить 3 дня в клубе бесплатно — посмотришь изнутри, попробуешь тренировку, пообщаешься с девочками. Никаких обязательств.
Попробуешь?

**СМС 8 — Тёплое закрытие** (отказ на всё)
Хорошо, всё понимаю 🤍
Если когда-нибудь захочешь — я здесь. Буду рада тебя видеть!
