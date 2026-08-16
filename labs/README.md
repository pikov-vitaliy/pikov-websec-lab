# Laboratory Catalog and Roadmap

Статус `implemented` означает, что в репозитории есть безопасный payload,
manifest, Student/Instructor Guides и проверяемые vulnerable/hardened результаты.

## Реализовано

| ID | Тема | Статус |
|---|---|---|
| [`svg-stored-xss`](svg-stored-xss/manifest.yaml) | Active SVG stored XSS, CWE-79 | Implemented |

## Roadmap — не реализовано

| Предлагаемый ID | Тема | CWE | Статус |
|---|---|---|---|
| `unrestricted-upload` | Самостоятельный сценарий небезопасной загрузки | CWE-434 | Planned only |
| `csrf-state-change` | Межсайтовая подделка запроса | CWE-352 | Planned only |
| `cookie-attributes` | HttpOnly/Secure и границы их защиты | CWE-1004, CWE-614 | Planned only |
| `idor-object-access` | Авторизация на уровне объекта | CWE-639 | Planned only |

Упоминание слабого контроля в текущем приложении не означает, что соответствующая
лабораторная реализована. Для перевода roadmap-записи в `implemented` нужны
отдельные доказательства эксплуатируемости, безопасная изоляция, reset, критерии
защищенного поведения и тесты.
