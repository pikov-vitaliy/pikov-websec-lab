"""Flask application factory and HTTP adapters for the training runtime."""

from __future__ import annotations

import html
import hashlib
import logging
import os
import platform
import secrets
import tempfile
from collections.abc import Callable, Mapping
from functools import wraps
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from flask import (
    Flask,
    Response,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)

from .runtime import EventType, LabMode, LabRun, UploadRejected


LOGGER = logging.getLogger("pikov_websec_lab")
APP_VERSION = "2.1.0"
VULNERABLE_SVG_CSP = (
    "default-src 'none'; script-src 'unsafe-inline'; connect-src 'self'; "
    "img-src 'self' data:; style-src 'unsafe-inline'; "
    "font-src 'self' data:; media-src 'self'; object-src 'none'; "
    "base-uri 'none'; form-action 'self'"
)


def _as_bool(value: object, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _uid_cookie_name(run_id: str) -> str:
    run_fingerprint = hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:16]
    return f"pikov_uid_{run_fingerprint}"


def _default_config() -> dict[str, Any]:
    run_id = os.environ.get("RUN_ID") or f"run-{secrets.token_hex(6)}"
    configured_upload_dir = os.environ.get("UPLOAD_DIR", "").strip()
    upload_dir = configured_upload_dir or str(
        Path(tempfile.gettempdir()) / "pikov-websec-lab" / run_id
    )
    return {
        "LAB_MODE": os.environ.get("LAB_MODE") or LabMode.VULNERABLE.value,
        "RUN_ID": run_id,
        "SCENARIO_ID": os.environ.get("SCENARIO_ID") or "svg-stored-xss",
        "UPLOAD_DIR": upload_dir,
        "MAX_CONTENT_LENGTH": int(
            os.environ.get("MAX_UPLOAD_SIZE") or 2 * 1024 * 1024
        ),
        "SECRET_KEY": os.environ.get("SECRET_KEY") or "",
        "INSTRUCTOR_TOKEN": os.environ.get("INSTRUCTOR_TOKEN") or "",
        "ENABLE_DEBUG_PANEL": _as_bool(
            os.environ.get("ENABLE_DEBUG_PANEL"), default=True
        ),
        "COOKIE_SECURE": _as_bool(os.environ.get("COOKIE_SECURE"), default=False),
    }


def create_app(
    test_config: Mapping[str, Any] | None = None,
    runtime: LabRun | None = None,
) -> Flask:
    """Create an independently configured lab application."""

    repository_root = Path(__file__).resolve().parents[2]
    app = Flask(
        __name__,
        template_folder=str(repository_root / "templates"),
        static_folder=str(repository_root / "static"),
    )
    app.config.from_mapping(_default_config())
    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = secrets.token_urlsafe(48)
    configured_instructor_token = str(
        app.config.get("INSTRUCTOR_TOKEN") or ""
    ).strip()
    generated_instructor_token = not configured_instructor_token
    if generated_instructor_token:
        app.config["INSTRUCTOR_TOKEN"] = secrets.token_urlsafe(32)
    else:
        app.config["INSTRUCTOR_TOKEN"] = configured_instructor_token

    explicit_mode = test_config.get("LAB_MODE") if test_config else None
    configured_mode = LabMode.parse(
        explicit_mode if explicit_mode is not None else app.config["LAB_MODE"]
    )
    if runtime is not None and explicit_mode is not None:
        if runtime.mode is not configured_mode:
            raise ValueError("LAB_MODE does not match injected LabRun")
    if runtime is None:
        runtime = LabRun(
            run_id=str(app.config["RUN_ID"]),
            scenario_id=str(app.config["SCENARIO_ID"]),
            mode=configured_mode,
            upload_dir=app.config["UPLOAD_DIR"],
            max_upload_size=int(app.config["MAX_CONTENT_LENGTH"]),
        )
    else:
        configured_mode = runtime.mode
        app.config["RUN_ID"] = runtime.run_id
        app.config["SCENARIO_ID"] = runtime.scenario_id
        app.config["UPLOAD_DIR"] = str(runtime.upload_dir)
    app.config["LAB_MODE"] = configured_mode.value
    app.config["LAB_UID_COOKIE_NAME"] = _uid_cookie_name(runtime.run_id)
    app.extensions["lab_runtime"] = runtime

    if generated_instructor_token:
        app.logger.warning(
            "LOCAL LAB ONLY: generated ephemeral instructor token: %s",
            app.config["INSTRUCTOR_TOKEN"],
        )
    _register_routes(app, runtime)
    return app


def _register_routes(app: Flask, runtime: LabRun) -> None:
    uid_cookie_name = str(app.config["LAB_UID_COOKIE_NAME"])

    def current_uid() -> int | None:
        raw_uid = request.cookies.get(uid_cookie_name)
        if raw_uid is None:
            return None
        try:
            return int(raw_uid)
        except (TypeError, ValueError):
            return None

    def current_user() -> dict[str, Any] | None:
        return runtime.get_user(current_uid())

    def requests_json() -> bool:
        return (
            request.path.startswith("/api/")
            or request.path.endswith("/api")
            or request.accept_mimetypes.best == "application/json"
        )

    def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            if current_user() is None:
                if requests_json():
                    return jsonify({"error": "authentication_required"}), 401
                return redirect("/")
            return view(*args, **kwargs)

        return decorated

    def supplied_instructor_token() -> str:
        token = request.headers.get("X-Lab-Token") or request.args.get("token")
        if token:
            return token
        if request.form:
            token = request.form.get("token")
            if token:
                return token
        if request.is_json:
            body = request.get_json(silent=True) or {}
            return str(body.get("token") or "")
        return ""

    def instructor_required(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            supplied = supplied_instructor_token()
            expected = str(app.config["INSTRUCTOR_TOKEN"])
            if not supplied or not secrets.compare_digest(supplied, expected):
                if requests_json():
                    return jsonify({"error": "instructor_token_required"}), 403
                return render_template("403.html"), 403
            return view(*args, **kwargs)

        return decorated

    def dashboard_payload() -> dict[str, Any]:
        snapshot = runtime.snapshot()
        summary = runtime.summary()
        attacks = runtime.legacy_attacks()
        return {
            "events": snapshot["events"],
            "attacks": attacks,
            "summary": summary,
            "mode": runtime.mode.value,
            "run_id": runtime.run_id,
            "scenario_id": runtime.scenario_id,
            "message_count": summary["message_count"],
            "user_count": summary["actor_count"],
            "attack_count": len(attacks),
        }

    @app.after_request
    def apply_mode_headers(response: Response) -> Response:
        response.headers["X-Lab-Mode"] = runtime.mode.value
        response.headers["Cache-Control"] = "no-store"
        if runtime.mode is LabMode.HARDENED:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "img-src 'self' data:; object-src 'none'; base-uri 'none'; "
                "frame-ancestors 'none'; form-action 'self'"
            )
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        return response

    @app.get("/")
    def index() -> Any:
        if current_user() is not None:
            return redirect("/chat")
        return render_template(
            "login.html", mode=runtime.mode.value, run_id=runtime.run_id
        )

    @app.post("/login")
    def login() -> Any:
        username = request.form.get("username", "")
        try:
            uid = runtime.login_or_create_user(username)
        except ValueError:
            return redirect("/")
        response = redirect("/chat")
        response.set_cookie(
            uid_cookie_name,
            str(uid),
            httponly=runtime.mode is LabMode.HARDENED,
            secure=_as_bool(app.config.get("COOKIE_SECURE")),
            samesite="Strict" if runtime.mode is LabMode.HARDENED else "Lax",
        )
        return response

    @app.get("/logout")
    def logout() -> Any:
        response = redirect("/")
        response.delete_cookie(uid_cookie_name)
        return response

    @app.get("/chat")
    @login_required
    def chat() -> Any:
        user = current_user()
        summary = runtime.summary()
        debug = {
            "message_count": summary["message_count"],
            "attack_count": summary["event_count"],
            "user_count": summary["actor_count"],
        }
        return render_template(
            "chat.html",
            user=user["name"],
            uid=user["uid"],
            role=user["role"],
            debug=debug if app.config["ENABLE_DEBUG_PANEL"] else {},
            mode=runtime.mode.value,
            run_id=runtime.run_id,
            scenario_id=runtime.scenario_id,
        )

    @app.post("/send_message")
    @login_required
    def send_message() -> Any:
        user = current_user()
        message_text = request.form.get("message", "").strip()
        recipient = request.form.get("recipient") or None
        attachment = request.files.get("attachment")
        content = ""
        upload = None
        try:
            if attachment is not None and attachment.filename:
                upload = runtime.store_upload(
                    original_name=attachment.filename,
                    mimetype=attachment.mimetype or "",
                    content=attachment.read(),
                )
            elif message_text.lower().lstrip().startswith("<svg"):
                upload = runtime.store_upload(
                    original_name="inline.svg",
                    mimetype="image/svg+xml",
                    content=message_text.encode("utf-8"),
                )
        except UploadRejected as exc:
            return (
                jsonify({"error": exc.reason, "payload_id": exc.payload_id}),
                exc.status_code,
            )

        if upload is not None:
            query = urlencode(
                {"payload_id": upload.payload_id, "marker": upload.marker}
            )
            object_url = f"/file/{upload.stored_name}?{query}"
            content = (
                '<object class="svg-embed" '
                f'data="{html.escape(object_url, quote=True)}" '
                'type="image/svg+xml">Your browser does not support SVG</object>'
            )
        elif message_text:
            content = html.escape(message_text, quote=False)
        if not content:
            return redirect("/chat")
        message = runtime.append_message(
            user_uid=user["uid"], content=content, recipient=recipient
        )
        response = (
            jsonify({"success": True, "id": message["id"]})
            if requests_json()
            else redirect("/chat")
        )
        if upload is not None:
            response.headers["X-Lab-Payload-ID"] = upload.payload_id
            response.headers["X-Lab-Event-Marker"] = upload.marker
        return response

    @app.get("/get_messages")
    @login_required
    def get_messages() -> Any:
        since = request.args.get("since", default=0, type=int) or 0
        return jsonify(
            {"messages": runtime.messages_since(since, viewer_uid=current_uid())}
        )

    @app.post("/api/send_message")
    @login_required
    def api_send_message() -> Any:
        user = current_user()
        data = request.get_json(silent=True) or {}
        message_text = str(data.get("text") or data.get("message") or "").strip()
        if not message_text:
            return jsonify({"error": "empty_message"}), 400

        if data.get("lab_event") == EventType.FORGED_ACTION.value:
            payload_id = str(data.get("payload_id") or "")
            marker = str(data.get("marker") or "")
            if user["role"] != "victim":
                return jsonify(
                    {"success": True, "ignored": True, "reason": "wrong_actor"}
                )
            upload = runtime.validate_upload_marker(payload_id, marker)
            if upload is None:
                return jsonify({"error": "invalid_event_marker"}), 403
            if not runtime.has_event(
                EventType.PAYLOAD_EXECUTED,
                payload_id=payload_id,
                actor_uid=user["uid"],
            ):
                return jsonify({"error": "payload_execution_not_observed"}), 409
            if runtime.mode is LabMode.HARDENED:
                _, created = runtime.record_event(
                    EventType.CONTROL_BLOCKED,
                    payload_id=payload_id,
                    actor_uid=user["uid"],
                    dedupe_key=f"{payload_id}:control-blocked:{user['uid']}",
                    details={"result": "blocked", "reason": "hardened_mode"},
                )
                return jsonify({"success": False, "blocked": True, "created": created}), 403

            _, created = runtime.record_event(
                EventType.FORGED_ACTION,
                payload_id=payload_id,
                actor_uid=user["uid"],
                dedupe_key=f"{payload_id}:forged-action:{user['uid']}",
                details={
                    "message": message_text[:160],
                    "source_ip": request.remote_addr,
                    "result": "observed",
                },
            )
            if created:
                runtime.append_message(
                    user_uid=user["uid"], content=html.escape(message_text, quote=False)
                )
            runtime.record_event(
                EventType.CONTROL_ALLOWED,
                payload_id=payload_id,
                actor_uid=user["uid"],
                dedupe_key=f"{payload_id}:control-allowed:{user['uid']}",
                details={"result": "allowed"},
            )
            return jsonify({"success": True, "created": created})

        message = runtime.append_message(
            user_uid=user["uid"], content=html.escape(message_text, quote=False)
        )
        return jsonify({"success": True, "id": message["id"]})

    @app.post("/api/lab-events")
    @login_required
    def lab_events() -> Any:
        user = current_user()
        data = request.get_json(silent=True) or {}
        event_name = data.get("type") or data.get("lab_event")
        if event_name != EventType.PAYLOAD_EXECUTED.value:
            return jsonify({"error": "unsupported_event_type"}), 400
        if user["role"] != "victim":
            return jsonify(
                {"success": True, "ignored": True, "reason": "wrong_actor"}
            )
        payload_id = str(data.get("payload_id") or "")
        marker = str(data.get("marker") or "")
        upload = runtime.validate_upload_marker(payload_id, marker)
        if upload is None:
            return jsonify({"error": "invalid_event_marker"}), 403
        event, created = runtime.record_event(
            EventType.PAYLOAD_EXECUTED,
            payload_id=payload_id,
            actor_uid=user["uid"],
            dedupe_key=f"{payload_id}:payload-executed:{user['uid']}",
            details={"result": "observed"},
        )
        return jsonify(
            {"success": True, "created": created, "event_id": event.event_id}
        )

    @app.post("/clear_chat")
    @login_required
    @instructor_required
    def clear_chat() -> Any:
        result = runtime.reset()
        if requests_json():
            return jsonify({"success": True, "reset": result})
        return redirect("/chat")

    @app.get("/whoami")
    def whoami() -> Any:
        user = current_user()
        if user is None:
            return jsonify({"uid": None, "user": None, "role": None})
        return jsonify(
            {"uid": user["uid"], "user": user["name"], "role": user["role"]}
        )

    @app.get("/file/<path:name>")
    def serve_file(name: str) -> Any:
        upload = runtime.get_upload(name)
        if upload is None or not upload.path.is_file():
            abort(404)
        runtime.record_event(
            EventType.SVG_SERVED,
            payload_id=upload.payload_id,
            actor_uid=current_uid(),
            dedupe_key=f"{upload.payload_id}:svg-served",
            details={"filename": upload.stored_name, "result": "served"},
        )
        response = send_from_directory(
            str(runtime.upload_dir), upload.stored_name, mimetype=upload.mimetype
        )
        if runtime.mode is LabMode.VULNERABLE:
            response.headers["Content-Security-Policy"] = VULNERABLE_SVG_CSP
        return response

    @app.get("/debug/attack-dashboard")
    @instructor_required
    def attack_dashboard() -> Any:
        if not app.config["ENABLE_DEBUG_PANEL"]:
            abort(404)
        payload = dashboard_payload()
        return render_template(
            "dashboard.html",
            **payload,
            messages_count=payload["summary"]["message_count"],
            user=(current_user() or {}).get("name"),
            uid=current_uid(),
        )

    @app.get("/debug/attack-dashboard/api")
    @instructor_required
    def attack_dashboard_api() -> Any:
        if not app.config["ENABLE_DEBUG_PANEL"]:
            abort(404)
        return jsonify(dashboard_payload())

    @app.get("/health")
    def health() -> Any:
        summary = runtime.summary()
        return jsonify(
            {
                "status": "healthy",
                "mode": runtime.mode.value,
                "run_id": runtime.run_id,
                "scenario_id": runtime.scenario_id,
                "message_count": summary["message_count"],
                "event_count": summary["event_count"],
            }
        )

    @app.get("/api/info")
    def api_info() -> Any:
        return jsonify(
            {
                "name": "Pikov Web Security Lab",
                "version": APP_VERSION,
                "purpose": "Educational Web Application Security Platform",
                "mode": runtime.mode.value,
                "run_id": runtime.run_id,
                "scenario_id": runtime.scenario_id,
                "python_version": platform.python_version(),
            }
        )

    @app.get("/api/report")
    @instructor_required
    def report() -> Any:
        response = jsonify(runtime.export_report())
        response.headers["Content-Disposition"] = (
            f'attachment; filename="lab-report-{runtime.run_id}.json"'
        )
        return response

    @app.errorhandler(413)
    def too_large(_: Exception) -> Any:
        return jsonify({"error": "file_too_large"}), 413

    @app.errorhandler(404)
    def not_found(_: Exception) -> Any:
        if request.path.startswith("/api/") or request.path.startswith("/debug/"):
            return jsonify({"error": "not_found"}), 404
        return render_template("404.html"), 404
