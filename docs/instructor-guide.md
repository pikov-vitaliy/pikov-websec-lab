# Instructor Guide: SVG Stored XSS

Этот документ содержит ответы и предназначен для преподавателя. Слушателям
выдается только [Student Guide](student-guide.md).

## Методическая основа

Занятие следует циклу «объяснение → действие → исправление → повторный тест»,
аналогичному официальной модели
[OWASP WebGoat](https://owasp.org/www-project-webgoat/). Разделение подсказок,
прогресса и Find/Fix-этапов опирается на практику
[OWASP Juice Shop](https://owasp.org/www-project-juice-shop/).

Измеримые цели и проверка результата соответствуют подходу NIST SSDF
[`PO.2.2`](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-218.pdf)
к ролевому обучению и оценке proficiency; NICE Framework рекомендует связывать
задания с практическими знаниями и навыками
([NICE Framework Resource Center](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center)).
Это методическая привязка, а не заявление о сертификации стенда.

Во время демонстрации сохраняйте доступность интерфейса по WCAG 2.2: управление
с клавиатуры (`2.1.1`), видимый фокус (`2.4.7`), достаточный контраст (`1.4.3`),
понятные labels и errors (`3.3.1`, `3.3.2`). Результат нельзя обозначать только
цветом. Нормативный текст: [WCAG 2.2](https://www.w3.org/TR/WCAG22/).

## Перед занятием

### Безопасность и область

- Получите разрешение владельца оборудования и объявите точную область занятия.
- Выделите один контейнер на слушателя или пару.
- Каноническая жертва — встроенная `ДобраяОвечка` (uid=2). Слушатель, вошедший
  под своим именем (роль `learner`), тоже может выступить жертвой, если атакующий
  адресует canary «Вся сессия» (broadcast). Инициировать canary-события
  (`PAYLOAD_EXECUTED`/`FORGED_ACTION`) не может только атакующий (`ЗлойБаран`) —
  это защита от самоатаки. Один экземпляр по-прежнему рассчитан на одну пару
  (атакующий + одна жертва), а не на индивидуальный вход всей группы. При
  broadcast SVG-документ рендерится и у атакующего: событие `SVG_SERVED` может
  быть отнесено к его загрузке (дедуплицируется по `payload_id`), тогда как
  `PAYLOAD_EXECUTED`/`FORGED_ACTION` несут настоящую жертву.
- Подготовьте и проверьте image заранее в доверенной сети. На время упражнения
  отключите внешний egress либо используйте отдельную частную учебную сеть;
  runtime-контейнер не должен получать Интернет ради повторной сборки.
- Запретите реальные учетные данные, публичные callback'и, туннели и произвольные
  payload'ы.
- Используйте только [`canary.svg`](../labs/svg-stored-xss/canary.svg).

### Preflight

1. Скопируйте `.env.example` в `.env`. Задайте случайные `SECRET_KEY` и
   `INSTRUCTOR_TOKEN` либо получите сгенерированный token из локального startup-
   лога. Не демонстрируйте token слушателям.
2. Установите `LAB_MODE=vulnerable`.
3. Выполните `docker compose config` и подтвердите `host_ip: 127.0.0.1`,
   `cap_drop: ALL`, `no-new-privileges`, read-only filesystem, resource limits и
   internal network.
4. Запустите `docker compose up --build` и проверьте
   `http://127.0.0.1:8080/health`.
5. Создайте две независимые сессии браузера и отправьте baseline-сообщение.
6. Выберите получателя `ДобраяОвечка` и загрузите canary как атакующий. Убедитесь,
   что атакующий не получает адресное сообщение, а dashboard показывает
   цепочку `UPLOAD_ACCEPTED → SVG_SERVED → PAYLOAD_EXECUTED(uid=2) →
   FORGED_ACTION(uid=2) → CONTROL_ALLOWED`, а чат — только фиксированный текст.
   Прямая попытка передать canary-событие из сессии атакующего должна быть
   проигнорирована как `wrong_actor` и не добавлять событие.
   Откройте dashboard только в преподавательском профиле как
   `/debug/attack-dashboard?token=<INSTRUCTOR_TOKEN>`; не демонстрируйте
   token на экране и не передавайте его слушателям.
7. Выполните reset и подтвердите отсутствие сообщений, событий и uploads.
8. Измените `LAB_MODE=hardened` в `.env` и пересоздайте процесс:
   `docker compose up --build --force-recreate`. Загрузка должна завершиться
   HTTP 415 с `active_svg_blocked`, timeline — событием `CONTROL_BLOCKED` без
   callback, а CSP должна содержать `object-src 'none'`.

Если какой-либо пункт не выполнен, не начинайте демонстрацию.

Для короткой демонстрации можно заранее поднять второй loopback-экземпляр на
другом порту. Создайте игнорируемый Git файл `.env.hardened.local` из примера,
задайте в нем `LAB_MODE=hardened`, `LAB_PORT=8081` и отдельные случайные секреты:

```bash
docker compose -p pikov-websec-lab-hardened \
  --env-file .env.hardened.local up --build -d
```

Не используйте один upload/state volume для vulnerable и hardened экземпляров.
Cookie не ограничиваются номером порта: для параллельного сравнения используйте
отдельные browser profiles/contexts. Каждый экземпляр также использует свой
run-specific cookie name.

## Сценарий на 10 минут

| Время | Действие |
|---:|---|
| 0–2 | Область, legal scope, две роли и цель CWE-79 |
| 2–4 | Baseline-сообщение и путь polling |
| 4–6 | Upload canary от атакующего, открытие чата жертвы |
| 6–8 | Timeline: upload → object → SVG document → local events |
| 8–9 | Переключение на заранее запущенный hardened-экземпляр и повтор |
| 9–10 | Вывод: остановить выполнение, а не только чтение cookie |

Не открывайте исходный payload до наблюдения: сначала попросите аудиторию
предсказать результат.

## Сценарий на 30 минут

| Время | Действие |
|---:|---|
| 0–5 | Правила, цели, pre-test из трех вопросов |
| 5–10 | Две сессии, baseline, Network и DOM |
| 10–16 | Canary и корреляция dashboard/Network |
| 16–21 | Active SVG, nested browsing context и same-origin |
| 21–25 | XSS против CSRF; HttpOnly против request authority |
| 25–28 | Hardened repeat: rejection, отсутствие object, `object-src 'none'` |
| 28–30 | Exit ticket и reset |

## Практикум на 60 минут

| Время | Действие |
|---:|---|
| 0–7 | Разрешенная область, выдача экземпляров, pre-test |
| 7–15 | Самостоятельный baseline и фиксация маршрутов |
| 15–27 | Canary, HTTP/DOM/evidence dashboard |
| 27–37 | Работа в парах над первопричиной и trust boundaries |
| 37–45 | Обсуждение XSS/CSRF и cookie flags |
| 45–53 | Hardened repeat тем же файлом и сбор негативных доказательств |
| 53–58 | Мини-отчет по [rubric](assessment-rubric.md) |
| 58–60 | Exit ticket, reset и уничтожение данных |

## Ответы преподавателя

### Почему canary безопаснее демонстрационного «стилера»

Сервер помещает одноразовые `payload_id` и `marker` в query URL самого объекта.
Canary читает только собственный `location.search`, отправляет фиксированные
`PAYLOAD_EXECUTED` и `FORGED_ACTION` на относительные маршруты и не обращается к
cookie, полям, storage или внешней сети. Backend доверяет actor только по своей
сессии, принимает эти события от любой не-attacker роли (канонически — seeded
victim `uid=2`) и дедуплицирует их.
Адресная доставка не отдает SVG отправителю, поэтому штатно script запускается
только при получении сообщения жертвой.

### Почему это stored XSS

Недоверенный SVG сохраняется, а ссылка на него остается в сообщениях до reset.
Последующий зритель загружает активный документ; исходный upload-запрос уже
завершен. Первопричина — выполнение недоверенного script при формировании
пользовательского представления, то есть CWE-79.

### Где выполняется script

`<object type="image/svg+xml">` создает отдельный SVG document и browsing context,
а не вставляет SVG-элементы прямо в DOM чата. Файл выдан с того же scheme/host/port,
поэтому same-origin policy допускает запросы к приложению и потенциальный доступ
к parent document.

### Почему forged action не равен CSRF

Canary уже выполняется внутри origin приложения вследствие XSS. Его POST — эффект
полномочий same-origin script. Классический CSRF начинается с внешнего origin и
требует отдельной проверки метода, content type, CORS/preflight, `SameSite` и
anti-CSRF token. Текущий опыт этого не доказывает.

CORS в основном ограничивает чтение ответа, а preflight — часть non-simple
запросов; обычную межсайтовую HTML-форму он сам по себе не блокирует. Поэтому
CORS нельзя выдавать за основной CSRF-контроль.

### Что дает HttpOnly

`HttpOnly` закрывает `document.cookie`, но браузер по-прежнему прикладывает cookie
к разрешенным same-origin запросам. Поэтому XSS может действовать от имени
пользователя, не зная значения cookie. `Secure` решает транспортную задачу, а
`SameSite` — часть межсайтовой, не same-origin модели.

### Почему regex недостаточен

SVG имеет множество активных конструкций помимо буквального `<script>`; XML-
парсинг, namespaces и encoding создают обходы. Regex-strip-script — полезный
урок обхода, но исправление требует отказа от active SVG, rasterization или
строгого parser-based allowlist.

### Какие контроли ожидаются

Основной барьер — не принимать или деактивировать недоверенный SVG. Независимый
барьер — не создавать active `<object>` и применить CSP `object-src 'none'`.
Session flags и безопасная выдача — defense in depth, а не замена первичного
исправления.

## Прогрессивные подсказки

Выдавайте следующую подсказку только после фиксации попытки:

1. Найдите запрос, после которого браузер получает `image/svg+xml`.
2. Проверьте не только DOM родительской страницы, но и тип вложенного элемента.
3. Сравните origin адресной строки и URL в `data` элемента.
4. Ищите два события с одним `payload_id` (столбец `payload_id` в таблице панели,
   а также Network и экспорт JSON), но не ищите украденный cookie — canary его не
   читает.
5. Для повторного теста сравните прием файла, DOM и CSP, а не только чат.

## Troubleshooting

### `/health` недоступен

- Выполните `docker compose ps` и `docker compose logs svg-chat`.
- Проверьте, что `LAB_PORT` свободен и обращение идет к `127.0.0.1`.
- Не заменяйте loopback на `0.0.0.0` ради быстрого обхода проблемы.

### Роли совпали

Окна используют общее cookie-хранилище. Примените разные browser profiles или
обычное и приватное окно, затем выполните logout/login.

### SVG виден, но событий нет

- Проверьте `LAB_MODE` и Network-запрос `GET /file/<name>`.
- Убедитесь, что использован штатный `svg-canary-v1`.
- Проверьте адресата сообщения. Если canary адресован только `ДобраяОвечка`, а
  жертва вошла под своим именем (роль `learner`), она сообщение не получит —
  адресуйте canary «Вся сессия». Ответ `wrong_actor` (HTTP 200, в статусе SVG
  «Canary ignored: open the intended victim session») теперь возвращается только
  для сессии атакующего (`ЗлойБаран`).
- Проверьте ответы `POST /api/lab-events` и `POST /api/send_message`.
- Наличие `object-src 'none'` означает ожидаемую блокировку hardened-режима.

### События повторяются

Каждая повторная загрузка активного SVG-документа может снова отправить HTTP-
callback, но backend дедуплицирует принятую пару `payload_id/event/actor`.
Повторные строки timeline до reset означают дефект дедупликации; повторный Network-
запрос сам по себе ожидаем. Сбросьте сессию перед новым показом.

### Reset возвращает 403

Передайте тот же `INSTRUCTOR_TOKEN`, который использует процесс, через скрытое
поле формы dashboard либо заголовок `X-Lab-Token`. Для UI скрытое поле заполняется
из `?token=...` в URL dashboard; используйте это только в локальном профиле
преподавателя и очистите историю. Для CLI предпочтителен заголовок. Не вставляйте
token в скриншоты или Student Guide.

В отличие от просмотра панели и экспорта (нужен только token), reset дополнительно
требует авторизованную сессию: `/clear_chat` защищён и `login_required`, и
`instructor_required`. Поэтому запрос без сессии возвращает `401`
(`authentication_required`) ещё до проверки token, а запрос с сессией, но без
верного token — `403` (`instructor_token_required`). Если видите `401`, сначала
войдите (см. раздел «Reset»), затем повторите с token.

## Reset

Мягкий reset требует синтетическую авторизованную сессию и instructor token.
Пример с отдельным cookie jar:

```bash
curl -s -c .lab-session.cookie -o /dev/null \
  -X POST -d "username=Instructor" \
  http://127.0.0.1:8080/login
curl -X POST \
  -b .lab-session.cookie \
  -H "X-Lab-Token: $INSTRUCTOR_TOKEN" \
  http://127.0.0.1:8080/clear_chat
rm .lab-session.cookie
```

PowerShell:

```powershell
Invoke-WebRequest -Method Post `
  -SessionVariable labWebSession `
  -Body @{ username = 'Instructor' } `
  -Uri 'http://127.0.0.1:8080/login' | Out-Null
Invoke-RestMethod -Method Post `
  -WebSession $labWebSession `
  -Headers @{ 'X-Lab-Token' = $env:INSTRUCTOR_TOKEN } `
  -Uri 'http://127.0.0.1:8080/clear_chat'
```

Оба примера используют только вымышленную локальную identity. Cookie jar из
bash-примера удаляется сразу после reset.

Полный reset:

```bash
docker compose down --volumes
docker compose up --build
```

Полный reset уничтожает только одноразовое состояние Compose-проекта. После
занятия также удалите обезличенные локальные exports dashboard, если они больше
не нужны.

Если использовался отдельный hardened-проект, остановите и его:

```bash
docker compose -p pikov-websec-lab-hardened \
  --env-file .env.hardened.local down --volumes
```

## Exit ticket

Попросите каждого слушателя одной фразой ответить на три вопроса:

1. Какой именно browser sink сделал SVG активным?
2. Почему `HttpOnly` не останавливает same-origin действие XSS?
3. Какие два независимых доказательства показывают, что hardened-режим блокирует
   выполнение, а не скрывает результат?
