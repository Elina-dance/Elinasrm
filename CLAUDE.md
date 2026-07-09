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

## Patch History

- `patch_fix_schedule_july9_v1` (55s): Aligns future trial dates for `trial`-status clients to valid schedule slots
- `patch_fix_schedule_july9_v2` (57s): Restores original historical trial dates for 7 arrived clients wrongly moved by v1
- `patch_fix_schedule_july9_v3` (59s): Clears past trial dates for `trial`-status clients; fixes Малыши→Средние for Пт 19:00 slots
