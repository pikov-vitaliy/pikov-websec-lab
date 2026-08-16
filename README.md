# Pikov WebSec Lab: Evil Sheep Trap

Учебный стенд для безопасной демонстрации хранимого XSS через активный SVG,
встроенный в чат с помощью `<object>`. Проект предназначен для занятий по
безопасной разработке, контролируемых демонстраций и самостоятельной практики.

> [!CAUTION]
> Приложение преднамеренно уязвимо. Запускайте его только на `127.0.0.1` либо в
> изолированной учебной сети с явно разрешенными участниками. Не публикуйте порт
> в Интернет, не используйте реальные учетные данные и не направляйте payload'ы
> на внешние адреса или системы без письменного разрешения.

## Происхождение и лицензия

Эта редакция основана на проекте
[nvmediagithub/evil_sheep_trap](https://github.com/nvmediagithub/evil_sheep_trap).
Исходная лицензия MIT и уведомления сохранены в [LICENSE](LICENSE) и
[NOTICE.md](NOTICE.md).

## Что реализовано

- две учебные персоны в отдельных браузерных сессиях;
- загрузка SVG и его отображение как активного документа через `<object>`;
- хранимый XSS-сценарий с безопасным локальным canary-callback;
- неизменяемые на время процесса режимы `vulnerable` и `hardened`;
- instructor-only журнал событий на `/debug/attack-dashboard?token=…`;
- состояние сообщений и пользователей в памяти процесса;
- контейнерный запуск с локальной публикацией порта.

Единственная заявленная законченная лабораторная —
[`svg-stored-xss`](labs/svg-stored-xss/manifest.yaml). Самостоятельные сценарии
CWE-434, CWE-352, CWE-1004/CWE-614 и CWE-639 пока находятся только в
[roadmap](labs/README.md) и не считаются реализованными.

## Быстрый запуск

Требуются Docker Engine и Docker Compose v2.

```bash
git clone https://github.com/pikov-vitaliy/pikov-websec-lab.git
cd pikov-websec-lab
cp .env.example .env
docker compose up --build
```

PowerShell-эквивалент копирования конфигурации:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Для занятия на Windows удобнее запускать изолированный экземпляр на пару:

```powershell
.\scripts\lab.ps1 -Action start -Pair pair-01 -Mode vulnerable -Port 8080
```

Команда проверяет loopback-binding и ограничение контейнера перед запуском. Для
повторного теста остановите этот экземпляр и запустите тот же `Pair` в режиме
`hardened`; после занятия остановите именно созданный проект:

```powershell
.\scripts\lab.ps1 -Action stop -Pair pair-01 -Mode vulnerable -Port 8080
```

Для hardened-экземпляра укажите `-Mode hardened` с тем же `Pair` и `Port`.

Пустые `SECRET_KEY` и `INSTRUCTOR_TOKEN` генерируются для одноразового запуска.
Если преподавателю нужен стабильный reset-token между перезапусками, задайте в
`.env` случайные учебные значения. Не используйте производственные секреты.
Проверьте стенд:

```bash
curl http://127.0.0.1:8080/health
```

Затем откройте <http://127.0.0.1:8080>. Текущая Compose-конфигурация публикует
сервис только на loopback. Именованные Compose profiles не используются.

Для разработки с явным подключением локальных исходников используется отдельный
override:

```bash
docker compose -f docker-compose.yml -f compose.dev.yaml up --build
```

Остановить стенд:

```bash
docker compose down
```

Полный сброс одноразовых данных выполняется командой ниже. Она удаляет только
Compose volumes этого проекта:

```bash
docker compose down --volumes
```

## Первый безопасный сценарий

1. В обычном окне войдите как `ЗлойБаран`.
2. В приватном окне войдите как `ДобраяОвечка`.
3. От имени атакующего выберите получателя `ДобраяОвечка` и загрузите
   [`labs/svg-stored-xss/canary.svg`](labs/svg-stored-xss/canary.svg).
4. Наблюдайте сетевые запросы и чат в сессии жертвы.
5. Преподаватель открывает
   `/debug/attack-dashboard?token=<INSTRUCTOR_TOKEN>` в своём локальном профиле
   и сопоставляет событие с журналом; token не передается слушателям.

Canary обращается только к локальным `/api/lab-events` и `/api/send_message`,
передает фиксированные тип события и текст с одноразовой server correlation и не
читает cookie, клавиатуру, токены или иные данные пользователя.

## Методические материалы

| Документ | Назначение |
|---|---|
| [Student Guide](docs/student-guide.md) | Задание слушателя без ответов |
| [Instructor Guide](docs/instructor-guide.md) | Сценарии на 10/30/60 минут, ответы и диагностика |
| [Assessment Rubric](docs/assessment-rubric.md) | Проверяемые критерии и баллы |
| [Architecture and Security Model](docs/architecture-and-security-model.md) | Потоки данных, границы доверия и изоляция |
| [Vulnerability Analysis](docs/vulnerability-analysis.md) | Точная механика XSS, CSRF и cookie-контролей |
| [Security Policy](SECURITY.md) | Допустимое использование и сообщение о дефектах |

## Классификация лабораторной

- CWE-79: Improper Neutralization of Input During Web Page Generation;
- OWASP Top 10 `A05:2025 Injection` (ранее `A03:2021 Injection`);
- `WSTG-v42-INPV-02`, `WSTG-v42-BUSL-08`, `WSTG-v42-BUSL-09`;
- OWASP ASVS 5.0.0: `1.2.1`, `1.3.1`, `1.3.4`, `5.1.1`, `5.2.1`,
  `5.2.2`, `5.3.1`.

Полная привязка и критерии защищенного поведения находятся в
[manifest.yaml](labs/svg-stored-xss/manifest.yaml).

## Ограничения

Это не production-система, не универсальный CTF и не доказательство наличия
отдельных CSRF, IDOR или unrestricted-upload сценариев. Наличие слабого контроля
рядом с XSS не превращает его автоматически в самостоятельную лабораторную:
эксплуатируемость каждого класса должна быть показана отдельным тестом.

## Участие в разработке

См. [CONTRIBUTING.md](CONTRIBUTING.md). Не добавляйте в репозиторий личные данные,
экспорты переписки, закрытые сообщения, реальные токены или материалы без права
публикации.
