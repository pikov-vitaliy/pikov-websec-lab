"use strict";

(() => {
  const I18N = {
    ru: {
      "a11y.skip": "К основному содержанию",
      "brand.subtitle": "Evil Sheep Trap · полигон Stored XSS",
      "brand.localOnly": "только локальный стенд",
      "locale.label": "Язык интерфейса",
      "common.role": "Роль",
      "common.mode": "Режим",
      "common.run": "Запуск",
      "common.logout": "Выйти",
      "common.cancel": "Отмена",
      "common.unknown": "не определено",
      "mode.vulnerable": "уязвимый режим",
      "mode.hardened": "защищённый режим",
      "mode.unknown": "режим не определён",
      "role.attacker": "атакующий · UID 1",
      "role.victim": "жертва · UID 2",
      "role.attackerShort": "атакующий",
      "role.victimShort": "жертва",
      "role.studentShort": "участник",
      "role.instructorShort": "преподаватель",
      "role.student": "участник",
      "role.instructor": "преподаватель",
      "status.connecting": "подключение…",
      "status.online": "соединение установлено",
      "status.offline": "нет связи с сервером",
      "status.paused": "обновление приостановлено",
      "status.sent": "Сообщение отправлено в учебную сессию.",
      "status.sending": "Отправляем сообщение…",
      "status.uploadBlocked": "Сервер отклонил вложение. Проверьте режим, тип файла и указанный лимит.",
      "status.tooLarge": "Файл превышает разрешённый сервером размер.",
      "status.requestFailed": "Сервер не выполнил запрос. Повторите действие или сообщите преподавателю.",
      "status.fileSelected": "Выбран файл: {name}",
      "status.noFile": "Файл не выбран",
      "status.exportReady": "Отчёт JSON подготовлен.",
      "status.resetDone": "Текущий запуск сброшен.",
      "status.resetFailed": "Не удалось сбросить запуск. Проверьте instructor token.",
      "meta.login": "Pikov WebSec Lab — Вход",
      "meta.chat": "Pikov WebSec Lab — Учебная сессия",
      "meta.dashboard": "Pikov WebSec Lab — Панель доказательств",
      "meta.forbidden": "Pikov WebSec Lab — Требуется ссылка преподавателя",
      "meta.notFound": "Pikov WebSec Lab — Страница не найдена",
      "meta.serverError": "Pikov WebSec Lab — Ошибка сервера",
      "login.eyebrow": "Лаборатория · CWE-79 · OWASP A05:2025 (ранее A03:2021)",
      "login.title": "Увидеть цепочку Stored XSS целиком",
      "login.lede": "Две роли, один безопасный canary-файл и наблюдаемое доказательство атаки — от загрузки SVG до блокировки защитой.",
      "login.routeLabel": "Маршрут лаборатории",
      "login.route.observe": "Воспроизвести контролируемое воздействие",
      "login.route.explain": "Связать событие с причиной и CWE-79",
      "login.route.verify": "Повторить тест в защищённом режиме",
      "login.sessionKicker": "Вход в учебную сессию",
      "login.chooseRole": "Выберите роль",
      "login.localTitle": "Работайте только на локальном стенде",
      "login.localBody": "Не вводите реальные учётные данные и не загружайте собственные активные payload-файлы.",
      "login.personasLabel": "Готовые учебные роли",
      "login.openRole": "Открыть роль",
      "login.customDivider": "или отдельная учебная роль",
      "login.usernameLabel": "Имя участника",
      "login.usernameHelp": "Используйте вымышленное имя без персональных данных.",
      "login.usernamePlaceholder": "Например, Аналитик-3",
      "login.enter": "Войти в лабораторию",
      "login.previewTitle": "Что произойдёт в лаборатории",
      "login.previewOne": "Атакующий отправит выданный преподавателем SVG-canary.",
      "login.previewTwo": "Жертва откроет чат и создаст безопасное событие телеметрии.",
      "login.previewThree": "Панель доказательств покажет цепочку и результат повторного теста.",
      "chat.eyebrow": "Практикум · Stored XSS через SVG",
      "chat.title": "Учебная сессия",
      "chat.lede": "Пройдите 7 шагов и сравните один и тот же canary в двух режимах.",
      "chat.openDashboard": "Панель доказательств",
      "chat.runContext": "Контекст запуска",
      "chat.guideKicker": "Маршрут занятия",
      "chat.guideTitle": "7 шагов лаборатории",
      "chat.step1.title": "Проверьте роль",
      "chat.step1.body": "Откройте атакующего и жертву в разных профилях браузера.",
      "chat.step2.title": "Создайте baseline",
      "chat.step2.body": "Отправьте обычное сообщение и убедитесь, что обмен работает.",
      "chat.step3.title": "Выберите canary",
      "chat.step3.body": "Используйте только файл, выданный преподавателем.",
      "chat.step4.title": "Загрузите SVG",
      "chat.step4.body": "Отправьте canary от роли атакующего выбранному получателю.",
      "chat.step5.title": "Наблюдайте как жертва",
      "chat.step5.body": "Откройте чат жертвы и отметьте видимый результат.",
      "chat.step6.title": "Соберите доказательства",
      "chat.step6.body": "Сопоставьте события на временной шкале с CWE-79.",
      "chat.step7.title": "Повторите после защиты",
      "chat.step7.body": "Запустите тот же тест и объясните причину блокировки.",
      "chat.resetProgress": "Сбросить отметки",
      "chat.warning.title": "Сейчас включён преднамеренно уязвимый режим",
      "chat.warning.body": "Не вводите пароли, токены, персональные данные и не используйте стенд вне разрешённой локальной среды.",
      "chat.hardened.title": "Сейчас включён защищённый режим",
      "chat.hardened.body": "Повторите тот же canary-тест и зафиксируйте, какой контроль заблокировал выполнение.",
      "chat.canary.title": "Безопасный canary вместо кражи данных",
      "chat.canary.body": "Разрешённый учебный SVG отправляет только фиксированную отметку в telemetry endpoint. Он не читает cookie, поля ввода или содержимое страницы.",
      "chat.channelKicker": "Общий учебный канал",
      "chat.channelTitle": "Сообщения сессии",
      "chat.polling": "обновляется автоматически",
      "chat.logLabel": "Сообщения чата",
      "chat.emptyTitle": "Сообщений пока нет",
      "chat.emptyBody": "Начните с обычного сообщения, чтобы зафиксировать baseline.",
      "chat.recipientLabel": "Получатель",
      "chat.recipientAll": "Вся сессия",
      "chat.recipientVictim": "ДобраяОвечка · жертва",
      "chat.recipientAttacker": "ЗлойБаран · атакующий",
      "chat.messageLabel": "Сообщение",
      "chat.messagePlaceholder": "Напишите обычное сообщение или добавьте выданный SVG-canary",
      "chat.fileLabel": "SVG-вложение",
      "chat.fileHelp": "Только canary-файл из комплекта преподавателя. Лимит задаёт сервер.",
      "chat.noFile": "Файл не выбран",
      "chat.send": "Отправить в сессию",
      "chat.messageFrom": "{user}, {time}",
      "dashboard.back": "Вернуться в лабораторию",
      "dashboard.eyebrow": "Наблюдение · доказательства · повторный тест",
      "dashboard.title": "Панель доказательств",
      "dashboard.lede": "Следите за цепочкой событий, не открывая DevTools во время демонстрации.",
      "dashboard.controlsLabel": "Управление панелью",
      "dashboard.pause": "Приостановить",
      "dashboard.resume": "Возобновить",
      "dashboard.projector": "Режим проектора",
      "dashboard.exitProjector": "Выйти из режима проектора",
      "dashboard.export": "Экспорт JSON",
      "dashboard.reset": "Сбросить запуск",
      "dashboard.connectionLabel": "Состояние подключения",
      "dashboard.tokenNotice": "Экспорт открыт по instructor token; сброс дополнительно требует вход преподавателя (сессию).",
      "dashboard.updated": "Обновлено",
      "dashboard.summaryLabel": "Сводка запуска",
      "dashboard.kpiEvents": "событий доказательства",
      "dashboard.kpiMessages": "сообщений в сессии",
      "dashboard.kpiActors": "наблюдаемых ролей",
      "dashboard.kpiControl": "результат контроля",
      "dashboard.awaiting": "ожидание",
      "dashboard.blocked": "заблокировано",
      "dashboard.executed": "выполнено",
      "dashboard.detected": "обнаружено",
      "dashboard.timelineKicker": "Цепочка атаки",
      "dashboard.timelineTitle": "Временная шкала доказательств",
      "dashboard.live": "в реальном времени",
      "dashboard.emptyTimelineTitle": "Ожидаем первое событие",
      "dashboard.emptyTimelineBody": "Начните с baseline-сообщения, затем отправьте безопасный SVG-canary.",
      "dashboard.explainKicker": "Подсказка преподавателю",
      "dashboard.explainTitle": "Что объяснять по цепочке",
      "dashboard.explain1Title": "Источник",
      "dashboard.explain1Body": "Как активный SVG попал в хранилище.",
      "dashboard.explain2Title": "Интерпретация",
      "dashboard.explain2Body": "Почему браузер создал активный SVG-документ.",
      "dashboard.explain3Title": "Воздействие",
      "dashboard.explain3Body": "Как действие выполнилось в контексте жертвы.",
      "dashboard.explain4Title": "Контроль",
      "dashboard.explain4Body": "Какой барьер остановил повторный тест.",
      "dashboard.cweNote": "Ненадлежащая нейтрализация ввода при формировании веб-страницы",
      "dashboard.tableKicker": "Журнал запуска",
      "dashboard.tableTitle": "Проверяемые события",
      "dashboard.tableHelp": "Общий payload_id связывает этапы одного теста; номер в столбце ID у каждого события свой.",
      "dashboard.tableCaption": "События текущего лабораторного запуска",
      "dashboard.colId": "ID",
      "dashboard.colPayload": "payload_id",
      "dashboard.colStage": "Этап",
      "dashboard.colType": "Тип события",
      "dashboard.colActor": "Роль",
      "dashboard.colResult": "Результат",
      "dashboard.colTime": "Время",
      "dashboard.emptyTable": "События появятся после начала сценария.",
      "dashboard.resetTitle": "Сбросить текущий запуск?",
      "dashboard.resetBody": "Будут удалены сообщения, вложения и доказательства этой учебной сессии.",
      "dashboard.confirmReset": "Сбросить запуск",
      "event.stage.upload": "загрузка",
      "event.stage.storage": "хранение",
      "event.stage.fetch": "получение",
      "event.stage.execution": "выполнение",
      "event.stage.action": "действие",
      "event.stage.control": "контроль",
      "event.stage.unknown": "событие",
      "event.result.blocked": "✓ заблокировано",
      "event.result.executed": "⚠ выполнено",
      "event.result.vulnerable": "⚠ уязвимо",
      "event.result.detected": "◎ обнаружено",
      "event.result.success": "✓ успешно",
      "event.result.unknown": "— не определено",
      "error.forbiddenKicker": "Граница преподавательского доступа",
      "error.forbiddenTitle": "Требуется ссылка преподавателя",
      "error.forbiddenBody": "Откройте полную локальную ссылку на панель, полученную от преподавателя. Не публикуйте и не пересылайте instructor token.",
      "error.notFoundKicker": "Маршрут не входит в сценарий",
      "error.notFoundTitle": "Овечка ушла с учебной тропы",
      "error.notFoundBody": "Проверьте адрес или вернитесь на стартовую страницу лаборатории.",
      "error.backHome": "На стартовую страницу",
      "error.serverKicker": "Сервер не завершил шаг",
      "error.serverTitle": "Сценарий временно остановлен",
      "error.serverBody": "Вернитесь в лабораторию. Если ошибка повторится, покажите преподавателю время и выполненный шаг.",
      "error.backLab": "Вернуться в лабораторию",
      "error.checkHealth": "Проверить состояние"
    },
    en: {
      "a11y.skip": "Skip to main content",
      "brand.subtitle": "Evil Sheep Trap · Stored XSS training range",
      "brand.localOnly": "local lab only",
      "locale.label": "Interface language",
      "common.role": "Role",
      "common.mode": "Mode",
      "common.run": "Run",
      "common.logout": "Sign out",
      "common.cancel": "Cancel",
      "common.unknown": "not available",
      "mode.vulnerable": "vulnerable mode",
      "mode.hardened": "hardened mode",
      "mode.unknown": "mode unavailable",
      "role.attacker": "attacker · UID 1",
      "role.victim": "victim · UID 2",
      "role.attackerShort": "attacker",
      "role.victimShort": "victim",
      "role.studentShort": "participant",
      "role.instructorShort": "instructor",
      "role.student": "participant",
      "role.instructor": "instructor",
      "status.connecting": "connecting…",
      "status.online": "connection established",
      "status.offline": "server connection lost",
      "status.paused": "updates paused",
      "status.sent": "Message sent to the lab session.",
      "status.sending": "Sending message…",
      "status.uploadBlocked": "The server rejected the attachment. Check the mode, file type, and configured limit.",
      "status.tooLarge": "The file exceeds the size allowed by the server.",
      "status.requestFailed": "The server did not complete the request. Try again or tell the instructor.",
      "status.fileSelected": "Selected file: {name}",
      "status.noFile": "No file selected",
      "status.exportReady": "The JSON report is ready.",
      "status.resetDone": "The current run was reset.",
      "status.resetFailed": "The run could not be reset. Check the instructor token.",
      "meta.login": "Pikov WebSec Lab — Sign in",
      "meta.chat": "Pikov WebSec Lab — Lab session",
      "meta.dashboard": "Pikov WebSec Lab — Evidence dashboard",
      "meta.forbidden": "Pikov WebSec Lab — Instructor link required",
      "meta.notFound": "Pikov WebSec Lab — Page not found",
      "meta.serverError": "Pikov WebSec Lab — Server error",
      "login.eyebrow": "Lab · CWE-79 · OWASP A05:2025 (formerly A03:2021)",
      "login.title": "See the complete Stored XSS chain",
      "login.lede": "Two roles, one safe canary file, and observable evidence—from SVG upload to control verification.",
      "login.routeLabel": "Lab route",
      "login.route.observe": "Reproduce a controlled impact",
      "login.route.explain": "Connect the event to its root cause and CWE-79",
      "login.route.verify": "Repeat the test in hardened mode",
      "login.sessionKicker": "Enter the lab session",
      "login.chooseRole": "Choose a role",
      "login.localTitle": "Use the lab only in the local environment",
      "login.localBody": "Do not enter real credentials or upload your own active payload files.",
      "login.personasLabel": "Prepared training roles",
      "login.openRole": "Open role",
      "login.customDivider": "or use a separate training role",
      "login.usernameLabel": "Participant name",
      "login.usernameHelp": "Use a fictional name without personal data.",
      "login.usernamePlaceholder": "For example, Analyst-3",
      "login.enter": "Enter the lab",
      "login.previewTitle": "What happens in this lab",
      "login.previewOne": "The attacker sends the instructor-provided SVG canary.",
      "login.previewTwo": "The victim opens chat and produces a safe telemetry event.",
      "login.previewThree": "The evidence dashboard shows the chain and the retest result.",
      "chat.eyebrow": "Hands-on · Stored XSS through SVG",
      "chat.title": "Lab session",
      "chat.lede": "Complete 7 steps and compare the same canary in both modes.",
      "chat.openDashboard": "Evidence dashboard",
      "chat.runContext": "Run context",
      "chat.guideKicker": "Exercise route",
      "chat.guideTitle": "7 lab steps",
      "chat.step1.title": "Confirm the role",
      "chat.step1.body": "Open attacker and victim in separate browser profiles.",
      "chat.step2.title": "Create a baseline",
      "chat.step2.body": "Send a normal message and verify that delivery works.",
      "chat.step3.title": "Select the canary",
      "chat.step3.body": "Use only the file supplied by the instructor.",
      "chat.step4.title": "Upload the SVG",
      "chat.step4.body": "Send the canary from the attacker to the selected recipient.",
      "chat.step5.title": "Observe as the victim",
      "chat.step5.body": "Open victim chat and note the visible result.",
      "chat.step6.title": "Collect evidence",
      "chat.step6.body": "Map timeline events to CWE-79.",
      "chat.step7.title": "Retest after hardening",
      "chat.step7.body": "Run the same test and explain why it was blocked.",
      "chat.resetProgress": "Reset checkmarks",
      "chat.warning.title": "The intentionally vulnerable mode is active",
      "chat.warning.body": "Do not enter passwords, tokens, or personal data, and do not use this lab outside the approved local environment.",
      "chat.hardened.title": "Hardened mode is active",
      "chat.hardened.body": "Repeat the same canary test and identify the control that blocked execution.",
      "chat.canary.title": "A safe canary instead of data theft",
      "chat.canary.body": "The approved training SVG sends only a fixed marker to the telemetry endpoint. It does not read cookies, inputs, or page content.",
      "chat.channelKicker": "Shared training channel",
      "chat.channelTitle": "Session messages",
      "chat.polling": "updates automatically",
      "chat.logLabel": "Chat messages",
      "chat.emptyTitle": "No messages yet",
      "chat.emptyBody": "Start with a normal message to establish a baseline.",
      "chat.recipientLabel": "Recipient",
      "chat.recipientAll": "Entire session",
      "chat.recipientVictim": "KindSheep · victim",
      "chat.recipientAttacker": "EvilRam · attacker",
      "chat.messageLabel": "Message",
      "chat.messagePlaceholder": "Write a normal message or attach the instructor-provided SVG canary",
      "chat.fileLabel": "SVG attachment",
      "chat.fileHelp": "Use only the instructor canary. The server sets the size limit.",
      "chat.noFile": "No file selected",
      "chat.send": "Send to session",
      "chat.messageFrom": "{user}, {time}",
      "dashboard.back": "Return to the lab",
      "dashboard.eyebrow": "Observe · evidence · retest",
      "dashboard.title": "Evidence dashboard",
      "dashboard.lede": "Follow the event chain without opening DevTools during the demonstration.",
      "dashboard.controlsLabel": "Dashboard controls",
      "dashboard.pause": "Pause",
      "dashboard.resume": "Resume",
      "dashboard.projector": "Projector mode",
      "dashboard.exitProjector": "Exit projector mode",
      "dashboard.export": "Export JSON",
      "dashboard.reset": "Reset run",
      "dashboard.connectionLabel": "Connection status",
      "dashboard.tokenNotice": "Export needs the instructor token; reset additionally requires an instructor login (session).",
      "dashboard.updated": "Updated",
      "dashboard.summaryLabel": "Run summary",
      "dashboard.kpiEvents": "evidence events",
      "dashboard.kpiMessages": "session messages",
      "dashboard.kpiActors": "observed roles",
      "dashboard.kpiControl": "control result",
      "dashboard.awaiting": "waiting",
      "dashboard.blocked": "blocked",
      "dashboard.executed": "executed",
      "dashboard.detected": "detected",
      "dashboard.timelineKicker": "Attack chain",
      "dashboard.timelineTitle": "Evidence timeline",
      "dashboard.live": "live",
      "dashboard.emptyTimelineTitle": "Waiting for the first event",
      "dashboard.emptyTimelineBody": "Start with a baseline message, then send the safe SVG canary.",
      "dashboard.explainKicker": "Instructor prompt",
      "dashboard.explainTitle": "What to explain along the chain",
      "dashboard.explain1Title": "Source",
      "dashboard.explain1Body": "How the active SVG entered storage.",
      "dashboard.explain2Title": "Interpretation",
      "dashboard.explain2Body": "Why the browser created an active SVG document.",
      "dashboard.explain3Title": "Impact",
      "dashboard.explain3Body": "How the action ran in the victim context.",
      "dashboard.explain4Title": "Control",
      "dashboard.explain4Body": "Which barrier stopped the retest.",
      "dashboard.cweNote": "Improper neutralization of input during web page generation",
      "dashboard.tableKicker": "Run log",
      "dashboard.tableTitle": "Verifiable events",
      "dashboard.tableHelp": "A shared payload_id links the stages of one test; the ID column is unique per event.",
      "dashboard.tableCaption": "Events in the current lab run",
      "dashboard.colId": "ID",
      "dashboard.colPayload": "payload_id",
      "dashboard.colStage": "Stage",
      "dashboard.colType": "Event type",
      "dashboard.colActor": "Role",
      "dashboard.colResult": "Result",
      "dashboard.colTime": "Time",
      "dashboard.emptyTable": "Events appear after the scenario starts.",
      "dashboard.resetTitle": "Reset the current run?",
      "dashboard.resetBody": "Messages, attachments, and evidence for this lab session will be removed.",
      "dashboard.confirmReset": "Reset run",
      "event.stage.upload": "upload",
      "event.stage.storage": "storage",
      "event.stage.fetch": "fetch",
      "event.stage.execution": "execution",
      "event.stage.action": "action",
      "event.stage.control": "control",
      "event.stage.unknown": "event",
      "event.result.blocked": "✓ blocked",
      "event.result.executed": "⚠ executed",
      "event.result.vulnerable": "⚠ vulnerable",
      "event.result.detected": "◎ detected",
      "event.result.success": "✓ successful",
      "event.result.unknown": "— not available",
      "error.forbiddenKicker": "Instructor access boundary",
      "error.forbiddenTitle": "Instructor link required",
      "error.forbiddenBody": "Open the complete local dashboard link supplied by the instructor. Do not publish or forward the instructor token.",
      "error.notFoundKicker": "This route is outside the scenario",
      "error.notFoundTitle": "The sheep left the training trail",
      "error.notFoundBody": "Check the address or return to the lab start page.",
      "error.backHome": "Go to the start page",
      "error.serverKicker": "The server did not complete this step",
      "error.serverTitle": "The scenario has paused",
      "error.serverBody": "Return to the lab. If the error repeats, show the instructor the time and completed step.",
      "error.backLab": "Return to the lab",
      "error.checkHealth": "Check service health"
    }
  };

  const pageRoot = document.querySelector("[data-page]");
  let locale = readStorage("est-locale") === "en" ? "en" : "ru";

  function readStorage(key) {
    try {
      return localStorage.getItem(key);
    } catch (_error) {
      return null;
    }
  }

  function writeStorage(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (_error) {
      // Private browsing can disable storage; the current page still works.
    }
  }

  function translate(key, values = {}) {
    const catalog = I18N[locale] || I18N.ru;
    const fallback = I18N.ru[key] || key;
    return String(catalog[key] || fallback).replace(/\{(\w+)\}/g, (_match, name) => String(values[name] ?? ""));
  }

  function applyLocale(nextLocale) {
    locale = nextLocale === "en" ? "en" : "ru";
    document.documentElement.lang = locale;
    document.documentElement.dataset.locale = locale;
    writeStorage("est-locale", locale);

    document.querySelectorAll("[data-i18n]").forEach((element) => {
      element.textContent = translate(element.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      element.setAttribute("placeholder", translate(element.dataset.i18nPlaceholder));
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
      element.setAttribute("aria-label", translate(element.dataset.i18nAriaLabel));
    });
    document.querySelectorAll("[data-i18n-title]").forEach((element) => {
      element.setAttribute("title", translate(element.dataset.i18nTitle));
    });
    document.querySelectorAll("[data-locale-value]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.localeValue === locale));
    });

    if (pageRoot?.dataset.titleKey) {
      document.title = translate(pageRoot.dataset.titleKey);
    }
    document.dispatchEvent(new CustomEvent("lab:locale", { detail: { locale } }));
  }

  function bindLocaleControls() {
    document.querySelectorAll("[data-locale-value]").forEach((button) => {
      button.addEventListener("click", () => applyLocale(button.dataset.localeValue));
    });
    applyLocale(locale);
  }

  function setGlobalStatus(message) {
    const target = document.getElementById("globalStatus");
    if (target) target.textContent = message;
  }

  class HttpError extends Error {
    constructor(message, status) {
      super(message);
      this.name = "HttpError";
      this.status = status;
    }
  }

  async function readResponse(response) {
    const contentType = response.headers.get("content-type") || "";
    let payload = null;
    if (contentType.includes("json")) {
      payload = await response.json();
    } else {
      const text = await response.text();
      payload = text ? { message: text } : {};
    }
    if (!response.ok) {
      const message = payload?.error || payload?.message || payload?.detail || translate("status.requestFailed");
      throw new HttpError(String(message), response.status);
    }
    return payload || {};
  }

  async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: { Accept: "application/json", ...(options.headers || {}) },
      ...options
    });
    return readResponse(response);
  }

  function friendlyError(error) {
    if (error?.status === 413) return translate("status.tooLarge");
    if (error?.status === 400 || error?.status === 403 || error?.status === 415) {
      return error.message || translate("status.uploadBlocked");
    }
    return error?.message && error.message.length < 240 ? error.message : translate("status.requestFailed");
  }

  function normalizedMode(value) {
    const mode = String(value || "").toLowerCase();
    if (["hardened", "secure", "fixed", "protected"].includes(mode)) return "hardened";
    if (["vulnerable", "unsafe", "training"].includes(mode)) return "vulnerable";
    return "unknown";
  }

  function modeLabel(mode) {
    return translate(`mode.${normalizedMode(mode)}`);
  }

  function roleFrom(identity) {
    const explicit = String(identity?.role || "").toLowerCase();
    if (explicit.includes("attack")) return "attacker";
    if (explicit.includes("victim")) return "victim";
    if (explicit.includes("instructor")) return "instructor";
    if (Number(identity?.uid) === 1 || String(identity?.user || "").includes("Баран")) return "attacker";
    if (Number(identity?.uid) === 2 || String(identity?.user || "").includes("Овеч")) return "victim";
    return "student";
  }

  function roleLabel(identity) {
    return translate(`role.${roleFrom(identity)}Short`) || translate("role.student");
  }

  function setConnection(element, state, key) {
    if (!element) return;
    element.dataset.state = state;
    const symbol = element.querySelector(".status-symbol");
    const label = element.querySelector("span:last-child");
    if (symbol) symbol.textContent = state === "online" ? "✓" : state === "offline" ? "×" : state === "paused" ? "Ⅱ" : "◌";
    if (label) {
      label.dataset.i18n = key;
      label.textContent = translate(key);
    }
  }

  async function initializeLogin() {
    const badge = document.querySelector("[data-mode-badge]");
    if (!badge) return;
    try {
      const info = await fetchJson("/api/info");
      const mode = normalizedMode(info.mode || info.lab_mode || badge.dataset.initialMode);
      badge.classList.toggle("mode-hardened", mode === "hardened");
      const text = badge.querySelector("span:last-child");
      if (text) {
        text.dataset.i18n = `mode.${mode}`;
        text.textContent = modeLabel(mode);
      }
    } catch (_error) {
      // Login remains functional when optional lab metadata is unavailable.
    }
  }

  let lastMessageId = 0;
  let chatPollTimer = null;
  let chatStopped = false;
  let chatIdentity = {};
  let chatInfo = {};

  function avatarFor(name, role) {
    if (role === "attacker" || /Баран|Ram/i.test(name)) return "🐏";
    if (role === "victim" || /Овеч|Sheep/i.test(name)) return "🐑";
    return "♙";
  }

  function renderMessage(message) {
    const chatBox = document.getElementById("chatBox");
    if (!chatBox) return;
    document.getElementById("emptyState")?.remove();

    const article = document.createElement("article");
    const mine = String(message.user || "") === String(chatIdentity.user || pageRoot?.dataset.currentUser || "");
    article.className = `message${mine ? " mine" : ""}`;
    article.dataset.messageId = String(message.id || "");

    const avatar = document.createElement("span");
    avatar.className = "message-avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = avatarFor(String(message.user || ""), String(message.role || ""));

    const body = document.createElement("div");
    body.className = "message-body";
    const meta = document.createElement("p");
    meta.className = "message-meta";
    meta.textContent = translate("chat.messageFrom", { user: message.user || translate("common.unknown"), time: message.time || "—" });
    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    // The server intentionally returns formatted lab content here. Vulnerable and
    // hardened behavior is controlled server-side so the same UI supports retest.
    bubble.innerHTML = String(message.content || message.message || "");

    body.append(meta, bubble);
    article.append(avatar, body);
    chatBox.append(article);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function pollMessages() {
    if (chatStopped) return;
    const connection = document.getElementById("chatConnection");
    try {
      const data = await fetchJson(`/get_messages?since=${encodeURIComponent(lastMessageId)}`);
      const messages = Array.isArray(data.messages) ? data.messages : [];
      messages.forEach((message) => {
        renderMessage(message);
        const numericId = Number(message.id);
        if (Number.isFinite(numericId)) lastMessageId = Math.max(lastMessageId, numericId);
      });
      setConnection(connection, "online", "status.online");
    } catch (_error) {
      setConnection(connection, "offline", "status.offline");
    } finally {
      if (!chatStopped) chatPollTimer = window.setTimeout(pollMessages, 2000);
    }
  }

  function updateChatContext() {
    const identity = {
      user: chatIdentity.user || pageRoot?.dataset.currentUser,
      uid: chatIdentity.uid || pageRoot?.dataset.currentUid,
      role: chatIdentity.role
    };
    const mode = normalizedMode(chatInfo.mode || chatInfo.lab_mode || pageRoot?.dataset.initialMode);
    const run = chatInfo.run_id || chatInfo.runId || pageRoot?.dataset.initialRun || "—";
    const roleBadge = document.querySelector("[data-role-badge]");
    const modeBadge = document.querySelector("[data-mode-badge]");
    const runBadge = document.querySelector("[data-run-badge]");
    if (roleBadge) roleBadge.textContent = `${roleLabel(identity)} · ${identity.user || translate("common.unknown")}`;
    if (modeBadge) modeBadge.textContent = modeLabel(mode);
    if (runBadge) runBadge.textContent = String(run);

    const warning = document.getElementById("vulnerableWarning");
    if (warning) {
      warning.dataset.mode = mode;
      const title = warning.querySelector("strong");
      const body = warning.querySelector("p");
      const prefix = mode === "hardened" ? "chat.hardened" : "chat.warning";
      if (title) {
        title.dataset.i18n = `${prefix}.title`;
        title.textContent = translate(`${prefix}.title`);
      }
      if (body) {
        body.dataset.i18n = `${prefix}.body`;
        body.textContent = translate(`${prefix}.body`);
      }
    }

    const token = chatInfo.dashboard_token || chatInfo.token || pageRoot?.dataset.dashboardToken || "";
    const dashboardLink = document.getElementById("dashboardLink");
    if (dashboardLink) {
      const url = new URL("/debug/attack-dashboard", window.location.origin);
      if (token) url.searchParams.set("token", token);
      dashboardLink.href = `${url.pathname}${url.search}`;
    }
    initializeStepProgress(String(run));
  }

  let progressRun = "default";

  function initializeStepProgress(runId) {
    progressRun = runId && runId !== "—" ? runId : "default";
    const saved = new Set((readStorage(`est-progress:${progressRun}`) || "").split(",").filter(Boolean));
    document.querySelectorAll("[data-step-check]").forEach((checkbox) => {
      checkbox.checked = saved.has(checkbox.id);
    });
    updateStepProgress();
  }

  function updateStepProgress() {
    const checks = [...document.querySelectorAll("[data-step-check]")];
    const completed = checks.filter((checkbox) => checkbox.checked);
    const count = document.getElementById("stepProgress");
    if (count) count.textContent = `${completed.length} / ${checks.length}`;
    writeStorage(`est-progress:${progressRun}`, completed.map((checkbox) => checkbox.id).join(","));
  }

  async function submitMessage(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const status = document.getElementById("composerStatus");
    const button = document.getElementById("sendMessage");
    if (status) {
      status.dataset.state = "pending";
      status.textContent = translate("status.sending");
    }
    if (button) button.disabled = true;

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        credentials: "same-origin",
        headers: { Accept: "application/json" }
      });
      await readResponse(response);
      const messageInput = document.getElementById("msgInput");
      const fileInput = document.getElementById("fileInput");
      if (messageInput) messageInput.value = "";
      if (fileInput) fileInput.value = "";
      updateFileName();
      if (status) {
        status.dataset.state = "success";
        status.textContent = translate("status.sent");
      }
      if (chatPollTimer) window.clearTimeout(chatPollTimer);
      await pollMessages();
    } catch (error) {
      if (status) {
        status.dataset.state = "error";
        status.textContent = friendlyError(error);
      }
    } finally {
      if (button) button.disabled = false;
    }
  }

  function updateFileName() {
    const input = document.getElementById("fileInput");
    const target = document.getElementById("fileName");
    if (!target) return;
    const file = input?.files?.[0];
    target.textContent = file ? translate("status.fileSelected", { name: file.name }) : translate("status.noFile");
  }

  async function initializeChat() {
    const results = await Promise.allSettled([fetchJson("/whoami"), fetchJson("/api/info")]);
    if (results[0].status === "fulfilled") chatIdentity = results[0].value;
    if (results[1].status === "fulfilled") chatInfo = results[1].value;
    updateChatContext();

    document.getElementById("messageForm")?.addEventListener("submit", submitMessage);
    document.getElementById("fileInput")?.addEventListener("change", updateFileName);
    document.querySelectorAll("[data-step-check]").forEach((checkbox) => checkbox.addEventListener("change", updateStepProgress));
    document.getElementById("resetProgress")?.addEventListener("click", () => {
      document.querySelectorAll("[data-step-check]").forEach((checkbox) => { checkbox.checked = false; });
      updateStepProgress();
    });
    document.addEventListener("lab:locale", updateChatContext);
    window.addEventListener("pagehide", () => {
      chatStopped = true;
      if (chatPollTimer) window.clearTimeout(chatPollTimer);
    });
    updateFileName();
    pollMessages();
  }

  let lastEventId = 0;
  let dashboardPollTimer = null;
  let dashboardPaused = false;
  let dashboardSnapshot = { events: [], summary: {} };
  const eventStore = new Map();

  function dashboardToken() {
    return pageRoot?.dataset.token || "";
  }

  function dashboardUrl(path, includeCursor = false) {
    const url = new URL(path, window.location.origin);
    const token = dashboardToken();
    if (token) url.searchParams.set("token", token);
    if (includeCursor && lastEventId) url.searchParams.set("since", String(lastEventId));
    return `${url.pathname}${url.search}`;
  }

  function normalizeEvent(raw, index) {
    const id = raw.id ?? raw.event_id ?? raw.sequence ?? `event-${index}`;
    const type = raw.type || raw.kind || raw.event || raw.name || "lab_event";
    const stageValue = String(raw.stage || raw.phase || type).toLowerCase();
    const knownStages = new Set(["upload", "storage", "fetch", "execution", "action", "control"]);
    const stage = knownStages.has(stageValue) ? stageValue : inferStage(stageValue);
    const actor = raw.actor || raw.user || raw.victim_user || raw.role || "—";
    const result = normalizeResult(raw.result || raw.outcome || raw.status, type);
    const timestamp = raw.timestamp || raw.time || raw.created_at || "—";
    const detailValue = raw.message || raw.description || raw.detail || raw.details?.message || raw.details?.reason || raw.details?.filename || "";
    const detail = typeof detailValue === "string" ? detailValue : JSON.stringify(detailValue);
    const payloadId = String(raw.payload_id ?? raw.payloadId ?? "—");
    return { id: String(id), payloadId, type: String(type), stage, actor: String(actor), result, timestamp: String(timestamp), detail };
  }

  function inferStage(type) {
    const value = String(type).toLowerCase();
    if (value.includes("upload")) return "upload";
    if (value.includes("stor")) return "storage";
    if (value.includes("fetch") || value.includes("load") || value.includes("served") || value.includes("deliver")) return "fetch";
    if (value.includes("execut") || value.includes("canary")) return "execution";
    if (value.includes("block") || value.includes("control") || value.includes("csp")) return "control";
    if (value.includes("message") || value.includes("action") || value.includes("forged")) return "action";
    return "unknown";
  }

  function normalizeResult(result, type) {
    const value = String(result || "").toLowerCase();
    const aliases = ["accepted", "served", "observed", "allowed"];
    if (!aliases.includes(value)) return value || inferResult(type);
    if (value === "accepted" || value === "served") return "success";
    if (value === "allowed") return "vulnerable";
    return inferResult(type) === "executed" ? "executed" : "detected";
  }

  function inferResult(type) {
    const value = String(type).toLowerCase();
    if (value.includes("block") || value.includes("reject")) return "blocked";
    if (value.includes("execut") || value.includes("canary")) return "executed";
    return "detected";
  }

  function stageLabel(stage) {
    const normalized = ["upload", "storage", "fetch", "execution", "action", "control"].includes(stage) ? stage : "unknown";
    return translate(`event.stage.${normalized}`);
  }

  function resultLabel(result) {
    const normalized = ["blocked", "executed", "vulnerable", "detected", "success"].includes(result) ? result : "unknown";
    return translate(`event.result.${normalized}`);
  }

  function sortedEvents() {
    return [...eventStore.values()].sort((a, b) => {
      const aNumber = Number(a.id);
      const bNumber = Number(b.id);
      if (Number.isFinite(aNumber) && Number.isFinite(bNumber)) return aNumber - bNumber;
      return a.timestamp.localeCompare(b.timestamp);
    });
  }

  function renderTimeline(events) {
    const timeline = document.getElementById("evidenceTimeline");
    if (!timeline) return;
    timeline.replaceChildren();
    if (!events.length) {
      const empty = document.createElement("li");
      empty.className = "timeline-empty";
      const art = document.createElement("span");
      art.className = "empty-illustration";
      art.setAttribute("aria-hidden", "true");
      art.textContent = "◇ ··· ◇";
      const title = document.createElement("strong");
      title.textContent = translate("dashboard.emptyTimelineTitle");
      const body = document.createElement("p");
      body.textContent = translate("dashboard.emptyTimelineBody");
      empty.append(art, title, body);
      timeline.append(empty);
      return;
    }

    events.forEach((event, index) => {
      const item = document.createElement("li");
      item.className = "timeline-event";
      item.dataset.result = event.result;
      const marker = document.createElement("span");
      marker.className = "event-marker";
      marker.setAttribute("aria-hidden", "true");
      marker.textContent = String(index + 1);
      const card = document.createElement("div");
      card.className = "event-card";
      const title = document.createElement("strong");
      title.textContent = `${stageLabel(event.stage)} · ${event.type}`;
      const meta = document.createElement("div");
      meta.className = "event-meta";
      const result = document.createElement("span");
      result.textContent = resultLabel(event.result);
      const actor = document.createElement("span");
      actor.textContent = event.actor;
      const time = document.createElement("time");
      time.textContent = event.timestamp;
      meta.append(result, actor, time);
      card.append(title, meta);
      if (event.detail) {
        const detail = document.createElement("p");
        detail.className = "event-detail";
        detail.textContent = event.detail;
        card.append(detail);
      }
      item.append(marker, card);
      timeline.append(item);
    });
  }

  function renderEventTable(events) {
    const body = document.getElementById("eventTableBody");
    if (!body) return;
    body.replaceChildren();
    if (!events.length) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = 7;
      cell.className = "empty-cell";
      cell.textContent = translate("dashboard.emptyTable");
      row.append(cell);
      body.append(row);
      return;
    }

    events.forEach((event) => {
      const row = document.createElement("tr");
      const values = [event.id, event.payloadId, stageLabel(event.stage), event.type, event.actor];
      values.forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
      });
      const resultCell = document.createElement("td");
      const result = document.createElement("span");
      result.className = "event-result";
      result.textContent = resultLabel(event.result);
      resultCell.append(result);
      const timeCell = document.createElement("td");
      timeCell.textContent = event.timestamp;
      row.append(resultCell, timeCell);
      body.append(row);
    });
  }

  function valueFromSummary(payload, names, fallback) {
    const summary = payload.summary || {};
    for (const name of names) {
      if (summary[name] !== undefined) return summary[name];
      if (payload[name] !== undefined) return payload[name];
    }
    return fallback;
  }

  function renderDashboard(payload) {
    const rawEvents = Array.isArray(payload.events) ? payload.events : Array.isArray(payload.attacks) ? payload.attacks : [];
    dashboardSnapshot = {
      ...dashboardSnapshot,
      ...payload,
      summary: { ...(dashboardSnapshot.summary || {}), ...(payload.summary || {}) },
      events: [],
      attacks: []
    };
    rawEvents.forEach((raw, index) => {
      const event = normalizeEvent(raw, index);
      eventStore.set(event.id, event);
      const numericId = Number(event.id);
      if (Number.isFinite(numericId)) lastEventId = Math.max(lastEventId, numericId);
    });
    const events = sortedEvents();
    renderTimeline(events);
    renderEventTable(events);

    const eventCount = valueFromSummary(payload, ["event_count", "events_count", "attack_count"], events.length);
    const messageCount = valueFromSummary(payload, ["message_count", "messages_count"], 0);
    const actorCount = valueFromSummary(payload, ["actor_count", "user_count", "users_count"], new Set(events.map((event) => event.actor).filter((actor) => actor !== "—")).size);
    document.getElementById("eventCount").textContent = String(eventCount);
    document.getElementById("messageCount").textContent = String(messageCount);
    document.getElementById("actorCount").textContent = String(actorCount);

    const mode = normalizedMode(payload.mode || payload.lab_mode || pageRoot?.dataset.initialMode);
    const run = payload.run_id || payload.runId || pageRoot?.dataset.initialRun || "—";
    document.getElementById("dashboardMode").textContent = modeLabel(mode);
    document.getElementById("dashboardRun").textContent = String(run);
    document.getElementById("lastUpdated").textContent = new Intl.DateTimeFormat(locale, { timeStyle: "medium" }).format(new Date());

    const lastControl = [...events].reverse().find((event) => event.stage === "control" || ["blocked", "executed", "vulnerable"].includes(event.result));
    const control = document.getElementById("controlState");
    if (control) {
      const key = lastControl?.result === "blocked" ? "dashboard.blocked" : ["executed", "vulnerable"].includes(lastControl?.result) ? "dashboard.executed" : "dashboard.awaiting";
      control.dataset.i18n = key;
      control.textContent = translate(key);
    }
  }

  async function pollDashboard() {
    if (dashboardPaused) return;
    const connection = document.getElementById("connectionStatus");
    try {
      const headers = dashboardToken() ? { "X-Lab-Token": dashboardToken() } : {};
      const payload = await fetchJson(dashboardUrl("/debug/attack-dashboard/api", true), { headers });
      renderDashboard(payload);
      setConnection(connection, "online", "status.online");
    } catch (_error) {
      setConnection(connection, "offline", "status.offline");
    } finally {
      if (!dashboardPaused) dashboardPollTimer = window.setTimeout(pollDashboard, 3000);
    }
  }

  function toggleDashboardPause() {
    dashboardPaused = !dashboardPaused;
    const button = document.getElementById("pauseDashboard");
    const label = button?.querySelector("span:last-child");
    button?.setAttribute("aria-pressed", String(dashboardPaused));
    if (label) {
      label.dataset.i18n = dashboardPaused ? "dashboard.resume" : "dashboard.pause";
      label.textContent = translate(label.dataset.i18n);
    }
    if (dashboardPaused) {
      if (dashboardPollTimer) window.clearTimeout(dashboardPollTimer);
      setConnection(document.getElementById("connectionStatus"), "paused", "status.paused");
    } else {
      pollDashboard();
    }
  }

  function toggleProjectorMode() {
    const enabled = !document.body.classList.contains("projector-mode");
    document.body.classList.toggle("projector-mode", enabled);
    const button = document.getElementById("projectorMode");
    const label = button?.querySelector("span:last-child");
    button?.setAttribute("aria-pressed", String(enabled));
    if (label) {
      label.dataset.i18n = enabled ? "dashboard.exitProjector" : "dashboard.projector";
      label.textContent = translate(label.dataset.i18n);
    }
  }

  async function exportReport() {
    const button = document.getElementById("exportReport");
    if (button) button.disabled = true;
    try {
      const headers = dashboardToken() ? { Accept: "application/json", "X-Lab-Token": dashboardToken() } : { Accept: "application/json" };
      const response = await fetch(dashboardUrl("/api/report"), { credentials: "same-origin", headers });
      if (!response.ok) throw new HttpError(translate("status.requestFailed"), response.status);
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = `evil-sheep-trap-${pageRoot?.dataset.initialRun || "report"}.json`;
      document.body.append(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(objectUrl);
      setGlobalStatus(translate("status.exportReady"));
    } catch (error) {
      setGlobalStatus(friendlyError(error));
    } finally {
      if (button) button.disabled = false;
    }
  }

  async function resetLab(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const status = document.getElementById("resetStatus");
    const token = dashboardToken();
    try {
      const headers = { Accept: "application/json" };
      if (token) headers["X-Lab-Token"] = token;
      const response = await fetch("/clear_chat", { method: "POST", body: new FormData(form), credentials: "same-origin", headers });
      await readResponse(response);
      eventStore.clear();
      lastEventId = 0;
      renderDashboard({ events: [], summary: { event_count: 0, message_count: 0, actor_count: 0 } });
      if (status) {
        status.dataset.state = "success";
        status.textContent = translate("status.resetDone");
      }
      setGlobalStatus(translate("status.resetDone"));
      window.setTimeout(() => document.getElementById("resetDialog")?.close(), 700);
    } catch (_error) {
      if (status) {
        status.dataset.state = "error";
        status.textContent = translate("status.resetFailed");
      }
    }
  }

  function initializeDashboard() {
    if (!dashboardToken()) {
      const accessNotice = document.getElementById("instructorAccessNotice");
      if (accessNotice) accessNotice.hidden = false;
      for (const id of ["exportReport", "resetLab"]) {
        const control = document.getElementById(id);
        if (control) {
          control.disabled = true;
          control.setAttribute("aria-describedby", "instructorAccessNotice");
        }
      }
    }
    document.getElementById("pauseDashboard")?.addEventListener("click", toggleDashboardPause);
    document.getElementById("projectorMode")?.addEventListener("click", toggleProjectorMode);
    document.getElementById("exportReport")?.addEventListener("click", exportReport);
    document.getElementById("resetLab")?.addEventListener("click", () => document.getElementById("resetDialog")?.showModal());
    document.getElementById("cancelReset")?.addEventListener("click", () => document.getElementById("resetDialog")?.close());
    document.getElementById("resetForm")?.addEventListener("submit", resetLab);
    document.getElementById("resetDialog")?.addEventListener("click", (event) => {
      if (event.target === event.currentTarget) event.currentTarget.close();
    });
    document.addEventListener("lab:locale", () => renderDashboard(dashboardSnapshot));
    window.addEventListener("pagehide", () => {
      dashboardPaused = true;
      if (dashboardPollTimer) window.clearTimeout(dashboardPollTimer);
    });
    pollDashboard();
  }

  bindLocaleControls();
  if (pageRoot?.dataset.page === "login") initializeLogin();
  if (pageRoot?.dataset.page === "chat") initializeChat();
  if (pageRoot?.dataset.page === "dashboard") initializeDashboard();
})();
