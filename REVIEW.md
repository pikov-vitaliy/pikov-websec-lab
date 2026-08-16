# Отчёт о проверке и предложения по улучшению

Ревизия базы: `fd28e1e` (`main`) · Стенд: Pikov WebSec Lab — Evil Sheep Trap

Документ отражает проверку самоотчёта разработчика и работу, выполненную в этом
ревью. Часть предложений уже **внесена** (с тестами), часть осознанно **оставлена
предложением**.

## Итог

Форк — зрелый управляемый учебный стенд: изолированная топология, режимы
`vulnerable`/`hardened`, безопасный canary вместо cookie-стилера, полный набор
методических материалов и рабочий CI. Самоотчёт разработчика в целом точен: три
несоответствия подтверждены, тесты и покрытие соответствуют заявленным.
Единственное устаревшее утверждение — про «старый бренд в имени экспортируемого
отчёта».

По вашему выбору внесены изменения кода **P1-1, P1-2, P2-1 (текст UI) и P3-1**;
дублирование проверки (P2-2) и типизация моделей оставлены предложениями. Полный
набор тестов и линт зелёные.

## Что проверено фактически

- База (`fd28e1e`), команда как в CI: `pytest -m "not e2e" --cov=pikov_websec_lab
  --cov-branch --cov-fail-under=85` → **58 passed + 19 subtests, покрытие 87.76%**
  (`factory.py` 83%, `runtime.py` 94%). Совпадает с заявленным «60 тестов + 19
  subtests, 87,76%».
- e2e (Chromium) локально: **2 passed** — цепочка canary → callback → dashboard в
  реальном браузере.
- Изоляция контейнеров (`test_compose_is_safe_by_default`, `docker compose config`)
  — проходит: gateway только на `127.0.0.1`, Flask без host-порта, `cap_drop: ALL`,
  read-only FS.
- **После правок этого ревью:** flake8 чистый, **60 passed non-e2e + 2 e2e + 19
  subtests**, покрытие **87.88%**.

## Проверка заявлений разработчика

| Заявление | Вердикт | Доказательство |
|---|---|---|
| Canary читает только server-issued `payload_id`/`marker`, API только относительные | Подтверждено | `labs/svg-stored-xss/canary.svg:34-46`; `connect-src 'self'` в `factory.py:37` |
| Два режима; hardened → HTTP 415 `active_svg_blocked`, CSP `object-src 'none'` | Подтверждено | `runtime.py:364-370`; `factory.py:217-226` |
| Только loopback gateway, tmpfs, non-root, read-only, `cap_drop: ALL` | Подтверждено | `tests/config/test_repository_config.py:15-44` |
| 60 тестов + 19 subtests, покрытие 87.76% | Подтверждено запуском | см. «Что проверено» |
| Имя экспортируемого отчёта содержит старый бренд `evil-sheep-trap-*` | **Устарело/неверно** | `factory.py:526` → `lab-report-<run_id>.json`; бренд остался только как обязательная атрибуция |
| Тех. долг: крупные `factory.py`/`app.js`, `dict[str, Any]`, дублирование `payload_id`+`marker`+`victim` | Подтверждено | `factory.py` ~540 строк, `app.js` 1080; проверка дублируется в `api_send_message` и `lab_events` |

## Подтверждённые несоответствия

### 1. «event ID» против `payload_id` — исправлено (P1-1)

Этапы одного теста связывает `payload_id`, а не «event ID»: каждое событие
получает уникальный `id`/`event_id` (`runtime.py:271-273`), а `payload_id`
общий. Раньше подсказка панели утверждала обратное, а `payload_id` бэкенд отдавал
(`runtime.py:69`), но в таблице не выводил — из-за чего инструкции гайда и manifest
были выполнимы только через Network/экспорт.

**Внесено:** в таблицу панели добавлена колонка `payload_id`, подсказка переписана,
документы приведены в соответствие. Теперь корреляция видна прямо на панели.

### 2. Авторизация reset: два фактора — это намеренный контроль (P2-1)

`/debug/attack-dashboard` и `/api/report` защищены только token (`factory.py:474,523`),
а `/clear_chat` — token **и** сессия (`factory.py:437-438`). Это **не дефект**:
двухфакторный reset закреплён тестом
`test_reset_requires_login_and_instructor_token_and_is_idempotent`
(`tests/integration/test_app.py:517`) — без сессии `401`, без/с неверным token
`403`. Ослаблять destructive-операцию в security-стенде не следует. Вводило в
заблуждение только уведомление на панели (`dashboard.tokenNotice`), которое
подразумевало token-only и для reset.

**Внесено:** текст `dashboard.tokenNotice` (ru/en + шаблон) уточнён — экспорт по
token, reset дополнительно требует сессию; в инструкторском гайде добавлено
различие `401`/`403`.

### 3. Роль жертвы — расширена (P1-2)

Раньше новые пользователи получали роль `learner` (`runtime.py:202`), а canary
принимался только от `role == "victim"` — жертвой мог быть только seeded uid=2. В
группе, где все входят под своими именами, никто не мог отыграть жертву.

**Внесено:** гейт заменён на «блокировать только атакующего», поэтому любой
не-attacker (seeded victim или self-named learner) может завершить половину
жертвы; атакующий по-прежнему получает `wrong_actor` (защита от самоатаки).
Слушатель под своим именем становится жертвой, если canary адресован «Вся сессия».
Добавлен тест `test_self_named_learner_can_act_as_victim_for_broadcast_canary`.

## Изменения кода (внесены в этом ревью)

- **P1-1 — `payload_id` на панели.** `normalizeEvent` пробрасывает `payload_id`;
  в таблицу добавлена колонка `payload_id` (`static/js/app.js`, `templates/dashboard.html`,
  i18n ru/en `dashboard.colPayload`, colspan 6→7); подсказка `dashboard.tableHelp`
  (ru/en + шаблон) переписана на «общий `payload_id` связывает этапы».
- **P1-2 — любой не-attacker может быть жертвой.** Гейт `role != "victim"` заменён
  на `role == "attacker"` в `api_send_message` и `lab_events` (`factory.py`).
- **P2-1 — уточнён текст `dashboard.tokenNotice`** (ru/en + шаблон). Авторизация
  reset намеренно двухфакторная и не менялась (см. несоответствие #2).
- **P3-1 — `@app.errorhandler(500)`** отдаёт JSON для `/api/` и `/debug/` и
  `templates/500.html` для страниц (`factory.py`). Покрыт тестом
  `test_internal_error_returns_json_for_api_and_template_for_pages`.

Все правки прошли flake8 и полный набор (60 non-e2e + 2 e2e, покрытие 87.88%).

## Остаётся предложением (не внесено — ваше решение)

- **P2-2 — убрать дублирование.** Вынести `role`-проверку + `validate_upload_marker`
  из `api_send_message` и `lab_events` в общий helper
  (`resolve_victim_claim(...) -> CanaryClaim | error`). Совпадает с вашим планом на
  типизированный `CanaryClaim`; логичнее делать вместе с типизацией моделей.
- **Тех. долг.** Типизированные модели сообщений/событий вместо `dict[str, Any]`;
  разнесение route/UI-модулей; уменьшение `factory.py`/`app.js`.

## Изменения документации (внесены)

- `docs/student-guide.md` — корреляция через `payload_id` (столбец панели +
  Network) вместо «event ID».
- `docs/instructor-guide.md` — жертвой может быть и self-named `learner` через
  broadcast; troubleshooting `wrong_actor` только для атакующего; различие `401`/`403`
  для reset; `payload_id` виден в столбце панели.
- `labs/svg-stored-xss/manifest.yaml` — `accepted_actor` = любой не-attacker.

## Что НЕ трогать

Строки `evil_sheep` / `Evil Sheep Trap` в `README.md`, `NOTICE.md`, `base.html` —
обязательная атрибуция upstream, закреплённая тестами
`tests/config/test_repository_config.py:116` и
`tests/ui_static/test_frontend_contract.py:24-37`. Удаление сломает CI и отменит
смысл коммита `fd28e1e` («thank upstream author»).
