# Lab Guide — Evil Sheep Trap 🐑

Hands-on exercises for understanding Stored XSS via SVG injection.

**Prerequisites:** Docker, a web browser with two profiles (or incognito mode),
and curiosity.

---

## Table of Contents

1. [Setup](#setup)
2. [Exercise 1: The Basics](#exercise-1-the-basics)
3. [Exercise 2: Trigger the Attack](#exercise-2-trigger-the-attack)
4. [Exercise 3: Observe the Dashboard](#exercise-3-observe-the-dashboard)
5. [Exercise 4: Apply Mitigations](#exercise-4-apply-mitigations)
6. [Exercise 5: Craft Your Own Payload](#exercise-5-craft-your-own-payload)
7. [Bonus: Break Out of `<object>`](#bonus-break-out-of-object)

---

## Setup

```bash
# Clone & launch
git clone https://github.com/yourname/evil_sheep_trap.git
cd evil_sheep_trap
docker compose up --build

# Verify it's running
curl http://localhost:8080/health
```

Open `http://localhost:8080` in your browser.

---

## Exercise 1: The Basics

**Goal:** Understand the chat flow and authentication model.

![Exercise 1 — Login in two browsers](../screenshots/login.svg)

1. Open `http://localhost:8080` in a normal window → click "ЗлойБаран".
2. Open the same URL in an **incognito/private** window → click "ДобраяОвечка".
3. Send a message from ЗлойБаран — observe it appear in ДобраяОвечка's window
   within 2 seconds (polling interval).
4. Check your browser DevTools → Application tab → Cookies. Note the `uid` cookie:
   - ЗлойБаран → `uid=1`
   - ДобраяОвечка → `uid=2`

> **🖼️ Что ты видишь:** Glassmorphism карточка входа с анимированными блобами,
> градиентными кнопками и quick-login для двух персон. Language toggle в правом верхнем углу.
>
> **What you see:** A glass-effect login card with animated gradient blobs,
> gradient buttons, and quick-login persona shortcuts. RU/EN toggle in the top-right corner.

**🔑 Key insight:** Authentication is purely cookie-based. Whoever controls
`uid` controls the identity.

---

## Exercise 2: Trigger the Attack

**Goal:** Execute the SVG-based XSS attack and observe the payload in action.

![Exercise 2 — Chat showing XSS attack in progress](../screenshots/chat.svg)

1. As **ЗлойБаран**, upload `payloads/example-evil.svg` via the paperclip button
   (or paste the contents of the SVG directly into the message textarea).
2. Observe the cute sheep image appear in the chat ✅
3. Switch to the **ДобраяОвечка** (incognito) window and refresh.
4. Watch what happens:
   - An `alert()` popup appears with XSS details 🚨
   - A message is automatically posted from ДобраяОвечка's account
   - Check Console tab — you'll see `[SVG XSS]` log messages

> **🖼️ Визуальный результат:** После загрузки SVG, в чате появляется красное сообщение
> "🚨 SVG INJECTION!" — это доказательство что JavaScript из SVG выполнился
> в контексте жертвы.
>
> **Visual result:** After the SVG upload, a red "🚨 SVG INJECTION!" message appears
> in chat — proof that JavaScript inside the SVG executed in the victim's context.

**🔑 Key insight:** The SVG script runs in the _viewer's_ context, not the
_uploader's_. This is what makes stored XSS so dangerous.

---

## Exercise 3: Observe the Dashboard

**Goal:** Use the attack dashboard to monitor exploit activity.

![Exercise 3 — Attack Dashboard with dark neon theme](../screenshots/dashboard.svg)

1. Navigate to `http://localhost:8080/debug/attack-dashboard`
2. You should see at least one captured attack event in the table.
3. Examine the fields:
   - **Victim UID:** confirms whose identity was hijacked
   - **Message:** the forged message content (truncated)
   - **Source IP:** `172.x.x.x` (Docker network) or `127.0.0.1`

> **🖼️ Что ты видишь:** Тёмная тема с неоновыми KPI тайлами (атаки, сообщения, UID),
> таблицей захваченных атак и живым терминальным лог-окном. Автообновление каждые 3 секунды.
>
> **What you see:** Dark neon-themed dashboard with glowing KPI tiles (attacks, messages, UID),
> captured attack table, and live terminal-style log box. Auto-refreshes every 3 seconds.

**💡 Try it:** Trigger the attack again and watch the dashboard update in
real-time (auto-refreshes every 3 seconds).

---

## Exercise 4: Apply Mitigations

**Goal:** Fix the vulnerability using progressively stronger defenses.

### Step A: Uncomment CSP Headers (5 minutes)

Edit `app.py`, find the `add_security_awareness_headers()` function, and
uncomment the header lines:

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; img-src 'self' data:; "
    "script-src 'none'; object-src 'none'"
)
```

Restart the container and re-attempt Exercise 2. Check browser Console — you
should see CSP violations blocking script execution.

**🤔 Question:** Did the alert() still fire? Why or why not?

### Step B: Replace `<object>` with `<img>` (10 minutes)

In `app.py`, find the lines that build the SVG embed content and change
`<object ...>` to `<img src="...">`. Test again — SVG should display but
scripts should NOT execute.

### Step C: Add SVG Sanitization (15 minutes)

Write a `sanitize_svg()` function that strips `<script>` tags before saving.
Apply it in the `send_message()` route. Verify the attack no longer works.

---

## Exercise 5: Craft Your Own Payload

**Goal:** Write an SVG payload that does something creative.

### Challenge A: Cookie Stealer (Easy)

Create an SVG that sends `document.cookie` to `http://localhost:9999/collect`
(you can run `nc -l 9999` in another terminal).

### Challenge B: Keylogger (Medium)

Write an SVG payload that logs keystrokes from the chat textarea and sends them
periodically via `fetch()` to the API.

### Challenge C: Persistent Backdoor (Hard)

Create a payload that writes itself into localStorage and re-injects on page
load, surviving chat clears.

**Hint:** The SVG `<script>` has full DOM access. You can modify any element
on the page, including the message textarea and send button.

---

## Bonus: Break Out of `<object>`

The `<object>` tag creates a nested browsing context. Research whether the SVG
script can access `window.parent.document`. If so, what additional attacks
become possible?

Write up your findings in 2-3 sentences and add them as a comment in your
payload file.

---

## Answers & Hints

<details>
<summary>Exercise 4A: Why does CSP block the alert?</summary>

CSP with `script-src 'none'` prevents ANY script execution on the page,
including scripts inside embedded SVGs served via `<object>`. The browser's
CSP enforcement applies to the entire document tree.
</details>

<details>
<summary>Exercise 4B: Why does <img> help?</summary>

The `<img>` tag treats SVG as an image format — it rasterizes the graphic but
does NOT execute any embedded scripts. It's a fundamentally safer embed method
for untrusted SVG content.
</details>

---

## Further Reading

- [PortSwigger Academy: Stored XSS](https://portswigger.net/web-security/cross-site-scripting/stored)
- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [SVG Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
