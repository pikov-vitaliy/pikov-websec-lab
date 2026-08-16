"""
Evil Sheep Trap 🐑 — Educational Stored XSS Training Platform
=============================================================

A deliberately vulnerable chat application that demonstrates how SVG-based
Stored Cross-Site Scripting attacks work in the wild. Built for cybersecurity
students, CTF participants, and anyone who wants to understand client-side
attacks by *seeing them in action*.

The vulnerability surface:
  - SVG files are embedded via <object> tags -> JavaScript inside SVG
    executes in the victim's browser context.
  - Uploaded SVGs have no sanitization -> arbitrary script execution.
  - API endpoint /api/send_message relies on cookies for auth -> CSRF-adjacent.

See ``docs/vulnerability-analysis.md`` for a deep dive and ``docs/lab-guide.md``
for hands-on exercises.

**WARNING -- FOR EDUCATIONAL USE ONLY.** Do not deploy to the public internet.
"""

from __future__ import annotations

import logging
import os
import platform
import secrets
import sys
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    abort,
    g,
    jsonify,
    redirect,
    request,
    render_template_string,
    send_from_directory,
)

# ==============================================================================
# Configuration
# ==============================================================================

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/data/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_SIZE", 2 * 1024 * 1024))
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DEBUG_MODE = os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8080))
ENABLE_DEBUG_PANEL = os.environ.get("ENABLE_DEBUG_PANEL", "true").lower() in (
    "true",
    "1",
    "yes",
)

# ==============================================================================
# Logging
# ==============================================================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("evil_sheep_trap")

# ==============================================================================
# In-memory data stores
# ==============================================================================

messages: list[dict[str, Any]] = []

users: dict[int, str] = {1: "ЗлойБаран", 2: "ДобраяОвечка"}
next_uid: int = 3

# Track attack events for the student dashboard
attack_log: list[dict[str, Any]] = []

# ==============================================================================
# Flask application
# ==============================================================================

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["SECRET_KEY"] = SECRET_KEY


# ==============================================================================
# Auth helpers
# ==============================================================================


def get_uid() -> int | None:
    """Return numeric uid from cookie, or None."""
    raw = request.cookies.get("uid")
    if raw is None:
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        return None


def get_user() -> str | None:
    """Return display name for the current uid."""
    uid = get_uid()
    if uid is None:
        return None
    return users.get(uid, f"Guest{uid}")


def find_uid_by_name(name: str) -> int | None:
    """Look up uid by username."""
    for uid, uname in users.items():
        if uname == name:
            return uid
    return None


def login_required(f):
    """Decorator -- redirect unauthenticated requests to the login page."""

    @wraps(f)
    def decorated(*args, **kwargs):  # type: ignore[no-untyped-def]
        if get_user() is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated


# ==============================================================================
# Request hooks
# ==============================================================================


@app.before_request
def capture_request_start():
    g.request_start = time.monotonic()


@app.after_request
def add_security_awareness_headers(response):  # type: ignore[no-untyped-def]
    """
    Add headers that *would* mitigate SVG XSS -- commented out so students can
    observe the vulnerability. Uncomment them as a lab exercise!

    See docs/vulnerability-analysis.md for the full explanation.
    """
    # --- Lab exercise: uncomment the lines below to apply mitigations ----------
    # response.headers["Content-Security-Policy"] = (
    #     "default-src 'self'; img-src 'self' data:; "
    #     "script-src 'none'; object-src 'none'"
    # )
    # response.headers["X-Content-Type-Options"] = "nosniff"
    # response.headers["X-Frame-Options"] = "DENY"
    # response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Timing footer (only in debug mode)
    if DEBUG_MODE and hasattr(g, "request_start"):
        elapsed = time.monotonic() - g.request_start
        response.headers["X-Response-Time"] = f"{elapsed * 1000:.1f}ms"

    return response


# ==============================================================================
# Template directory
# ==============================================================================

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _render(name: str, **context):
    """Render a template from the templates/ directory."""
    tpl_path = _TEMPLATE_DIR / name
    if tpl_path.exists():
        return render_template_string(
            tpl_path.read_text(encoding="utf-8"), **context
        )
    abort(404, f"Template {name} not found")


# ==============================================================================
# Routes -- Public
# ==============================================================================


@app.route("/")
def index():
    """Login / landing page."""
    if get_user():
        return redirect("/chat")
    return _render("login.html")


@app.route("/login", methods=["POST"])
def login():
    global next_uid

    username = request.form.get("username", "").strip()[:30]
    if not username:
        return redirect("/")

    uid = find_uid_by_name(username)
    if uid is None:
        uid = next_uid
        users[uid] = username
        next_uid += 1

    resp = redirect("/chat")
    resp.set_cookie("uid", str(uid), httponly=False, samesite="Lax")
    logger.info("Login: %s (uid=%d)", username, uid)
    return resp


@app.route("/logout")
def logout():
    uid = get_uid()
    user = get_user()
    resp = redirect("/")
    resp.delete_cookie("uid")
    if uid:
        logger.info("Logout: %s (uid=%d)", user, uid)
    return resp


# ==============================================================================
# Routes -- Chat
# ==============================================================================


@app.route("/chat")
@login_required
def chat():
    debug_data = {}
    if ENABLE_DEBUG_PANEL:
        debug_data = {
            "message_count": len(messages),
            "attack_count": len(attack_log),
            "user_count": len(users),
        }
    return _render("chat.html", user=get_user(), uid=get_uid(), debug=debug_data)


@app.route("/send_message", methods=["POST"])
@login_required
def send_message():
    user = get_user()
    message_text = request.form.get("message", "").strip()
    attachment = request.files.get("attachment")

    msg_id = len(messages) + 1
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    content = ""

    if attachment and attachment.filename:
        filename = attachment.filename
        safe_filename = f"{msg_id}_{int(time.time())}_{filename}"
        filepath = UPLOAD_DIR / safe_filename
        # INTENTIONALLY VULNERABLE: no file type validation beyond extension
        attachment.save(filepath)

        if filename.lower().endswith(".svg"):
            content = (
                f'<object class="svg-embed" '
                f'data="/file/{safe_filename}" '
                f'type="image/svg+xml">Your browser does not support SVG</object>'
            )
        else:
            content = f'<a href="/file/{safe_filename}" target="_blank">📎 {filename}</a>'
    elif message_text:
        if "<svg" in message_text.lower():
            svg_filename = f"{msg_id}_{int(time.time())}.svg"
            svg_path = UPLOAD_DIR / svg_filename
            svg_path.write_text(message_text, encoding="utf-8")

            content = (
                f'<object class="svg-embed" '
                f'data="/file/{svg_filename}" '
                f'type="image/svg+xml">Your browser does not support SVG</object>'
            )
        else:
            content = message_text.replace("<", "&lt;").replace(">", "&gt;")

    if not content:
        return redirect("/chat")

    messages.append({"id": msg_id, "user": user, "time": timestamp, "content": content})
    logger.info("Message #%d from %s", msg_id, user)
    return redirect("/chat")


@app.route("/get_messages")
def get_messages():
    """Return new messages since the given id (long-polling style)."""
    since = request.args.get("since", 0, type=int)
    new_msgs = [m for m in messages if m["id"] > since]
    return jsonify({"messages": new_msgs})


# ==============================================================================
# Routes -- API (XSS payload target)
# ==============================================================================


@app.route("/api/send_message", methods=["POST"])
@login_required
def api_send_message():
    """
    This endpoint is the *target* of the SVG-based XSS attack.

    Because authentication is cookie-based and there is no CSRF token, a script
    running in the page context can call this endpoint on behalf of the victim.
    """
    user = get_user()
    data = request.get_json(silent=True) or {}
    message_text = data.get("message", "").strip()

    if not message_text:
        return jsonify({"error": "empty message"}), 400

    msg_id = len(messages) + 1
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    content = message_text.replace("<", "&lt;").replace(">", "&gt;")

    messages.append({"id": msg_id, "user": user, "time": timestamp, "content": content})

    # Log the attack for the student dashboard
    attack_log.append(
        {
            "id": len(attack_log) + 1,
            "victim_uid": get_uid(),
            "victim_user": user,
            "message": message_text[:80],
            "timestamp": timestamp,
            "source_ip": request.remote_addr,
        }
    )

    logger.warning("API message #%d from %s (potential XSS vector)", msg_id, user)
    return jsonify({"success": True, "id": msg_id})


# ==============================================================================
# Routes -- Utility
# ==============================================================================


@app.route("/clear_chat", methods=["POST"])
@login_required
def clear_chat():
    messages.clear()
    attack_log.clear()
    for item in UPLOAD_DIR.iterdir():
        if item.is_file():
            try:
                item.unlink()
            except OSError:
                pass
    logger.info("Chat cleared by %s", get_user())
    return redirect("/chat")


@app.route("/whoami")
def whoami():
    """Diagnostic endpoint -- useful for debugging cookie-based auth."""
    return jsonify({"uid": get_uid(), "user": get_user()})


@app.route("/file/<path:name>")
def serve_file(name):
    name = os.path.basename(name)
    path = UPLOAD_DIR / name
    if not path.is_file():
        abort(404)
    return send_from_directory(str(UPLOAD_DIR), name, mimetype="image/svg+xml")


# ==============================================================================
# Routes -- Debug / Student Dashboard
# ==============================================================================


@app.route("/debug/attack-dashboard")
def attack_dashboard():
    """Student-facing dashboard that visualizes captured attack events."""
    if not ENABLE_DEBUG_PANEL:
        abort(404)
    return _render(
        "dashboard.html",
        attacks=attack_log,
        messages_count=len(messages),
        user=get_user(),
        uid=get_uid(),
    )


@app.route("/debug/attack-dashboard/api")
def attack_dashboard_api():
    if not ENABLE_DEBUG_PANEL:
        abort(404)
    return jsonify({
        "attacks": attack_log,
        "message_count": len(messages),
        "user_count": len(users),
    })


@app.route("/health")
def health():
    """Liveness probe for Kubernetes / Docker health checks."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(time.monotonic(), 2),
            "messages_in_memory": len(messages),
            "users_registered": len(users),
        }
    )


@app.route("/api/info")
def api_info():
    """Platform info endpoint."""
    return jsonify(
        {
            "name": "Evil Sheep Trap",
            "version": "2.0.0",
            "purpose": "Educational XSS Training Platform",
            "vulnerability_type": "Stored XSS via SVG Injection (OWASP A03:2021)",
            "python_version": platform.python_version(),
        }
    )


# ==============================================================================
# Error handlers
# ==============================================================================


@app.errorhandler(404)
def not_found(e):  # type: ignore[no-untyped-def]
    if request.path.startswith("/api/") or request.path.startswith("/debug/"):
        return jsonify({"error": "not_found"}), 404
    return _render("404.html"), 404


@app.errorhandler(413)
def too_large(e):  # type: ignore[no-untyped-def]
    return jsonify({"error": "file_too_large"}), 413 if request.wants_json else (_render("404.html"), 413)


@app.errorhandler(500)
def server_error(e):  # type: ignore[no-untyped-def]
    logger.exception("Internal server error")
    if request.wants_json:
        return jsonify({"error": "internal_server_error"}), 500
    return _render("500.html"), 500


# ==============================================================================
# Entry point
# ==============================================================================


if __name__ == "__main__":
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║  🐑  Evil Sheep Trap v2.0                               ║
║  Educational Stored XSS Training Platform               ║
╠══════════════════════════════════════════════════════════╣
║  ⚠️  INTENTIONALLY VULNERABLE — DO NOT EXPOSE TO INTERNET ║
╚══════════════════════════════════════════════════════════╝
    """
    logger.info(banner)
    logger.info("Starting on %s:%d (debug=%s, log_level=%s)", HOST, PORT, DEBUG_MODE, LOG_LEVEL)
    app.run(host=HOST, port=PORT, debug=DEBUG_MODE)
