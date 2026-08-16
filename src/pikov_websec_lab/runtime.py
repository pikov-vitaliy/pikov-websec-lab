"""Thread-safe domain state for one isolated web-security lab run."""

from __future__ import annotations

import re
import secrets
import shutil
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Mapping


class LabMode(str, Enum):
    """Immutable execution profile selected when a lab run is created."""

    VULNERABLE = "vulnerable"
    HARDENED = "hardened"

    @classmethod
    def parse(cls, value: str | LabMode) -> LabMode:
        try:
            return cls(value)
        except ValueError as exc:
            allowed = ", ".join(mode.value for mode in cls)
            raise ValueError(f"LAB_MODE must be one of: {allowed}") from exc


class EventType(str, Enum):
    """Observable stages in the SVG stored-XSS teaching scenario."""

    UPLOAD_ACCEPTED = "UPLOAD_ACCEPTED"
    SVG_SERVED = "SVG_SERVED"
    PAYLOAD_EXECUTED = "PAYLOAD_EXECUTED"
    FORGED_ACTION = "FORGED_ACTION"
    CONTROL_ALLOWED = "CONTROL_ALLOWED"
    CONTROL_BLOCKED = "CONTROL_BLOCKED"


@dataclass(frozen=True, slots=True)
class LabEvent:
    id: int
    event_id: str
    event_type: EventType
    run_id: str
    scenario_id: str
    timestamp: str
    payload_id: str | None = None
    actor_uid: int | None = None
    actor_name: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        details = dict(self.details)
        result = details.get("result") or details.get("outcome")
        message = details.get("message") or details.get("reason")
        return {
            "id": self.id,
            "event_id": self.event_id,
            "type": self.event_type.value,
            "kind": self.event_type.value,
            "stage": self.event_type.value,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "payload_id": self.payload_id,
            "actor_uid": self.actor_uid,
            "actor": self.actor_name,
            "user": self.actor_name,
            "victim_user": self.actor_name,
            "timestamp": self.timestamp,
            "time": self.timestamp[11:19],
            "result": result,
            "outcome": result,
            "status": result,
            "message": message,
            "details": details,
        }


@dataclass(frozen=True, slots=True)
class StoredUpload:
    payload_id: str
    marker: str
    original_name: str
    stored_name: str
    mimetype: str
    size: int
    path: Path
    active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "payload_id": self.payload_id,
            "original_name": self.original_name,
            "stored_name": self.stored_name,
            "mimetype": self.mimetype,
            "size": self.size,
            "active": self.active,
        }


@dataclass(frozen=True, slots=True)
class CanaryClaim:
    """A validated canary callback: a marker-authenticated upload and its ids."""

    payload_id: str
    marker: str
    upload: StoredUpload


class UploadRejected(ValueError):
    """A policy rejection with an HTTP-compatible status and correlation id."""

    def __init__(self, reason: str, status_code: int, payload_id: str) -> None:
        super().__init__(reason)
        self.reason = reason
        self.status_code = status_code
        self.payload_id = payload_id


class LabRun:
    """Own all mutable state and evidence for one isolated classroom run."""

    _SEEDED_USERS = {
        1: {"name": "ЗлойБаран", "role": "attacker"},
        2: {"name": "ДобраяОвечка", "role": "victim"},
    }

    def __init__(
        self,
        *,
        run_id: str,
        scenario_id: str,
        mode: str | LabMode,
        upload_dir: str | Path,
        max_upload_size: int = 2 * 1024 * 1024,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.run_id = run_id
        self.scenario_id = scenario_id
        self._mode = LabMode.parse(mode)
        self.upload_dir = Path(upload_dir).resolve()
        self.max_upload_size = int(max_upload_size)
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._lock = RLock()
        self._messages: list[dict[str, Any]] = []
        self._events: list[LabEvent] = []
        self._events_by_dedupe_key: dict[str, LabEvent] = {}
        self._uploads: dict[str, StoredUpload] = {}
        self._uploads_by_payload_id: dict[str, StoredUpload] = {}
        self._users: dict[int, dict[str, str]] = {}
        self._next_message_id = 1
        self._next_event_id = 1
        self._next_upload_id = 1
        self._next_uid = 3
        self._seed_users()
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @property
    def mode(self) -> LabMode:
        return self._mode

    def _seed_users(self) -> None:
        self._users = {
            uid: dict(attributes) for uid, attributes in self._SEEDED_USERS.items()
        }

    def _timestamp(self) -> str:
        current = self._clock()
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        return current.astimezone(timezone.utc).isoformat()

    def get_user(self, uid: int | None) -> dict[str, Any] | None:
        if uid is None:
            return None
        with self._lock:
            user = self._users.get(uid)
            if user is None:
                return None
            return {"uid": uid, **user}

    def find_uid_by_name(self, name: str) -> int | None:
        with self._lock:
            return next(
                (uid for uid, user in self._users.items() if user["name"] == name),
                None,
            )

    def login_or_create_user(self, name: str) -> int:
        normalized = name.strip()[:30]
        if not normalized:
            raise ValueError("username_required")
        with self._lock:
            existing = next(
                (
                    uid
                    for uid, user in self._users.items()
                    if user["name"] == normalized
                ),
                None,
            )
            if existing is not None:
                return existing
            uid = self._next_uid
            self._next_uid += 1
            self._users[uid] = {"name": normalized, "role": "learner"}
            return uid

    def append_message(
        self,
        *,
        user_uid: int,
        content: str,
        recipient: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            user = self._users.get(user_uid)
            if user is None:
                raise ValueError("unknown_user")
            message = {
                "id": self._next_message_id,
                "user": user["name"],
                "time": self._timestamp()[11:19],
                "content": content,
            }
            if recipient:
                message["recipient"] = recipient
            self._next_message_id += 1
            self._messages.append(message)
            return dict(message)

    def messages_since(
        self, message_id: int, *, viewer_uid: int | None = None
    ) -> list[dict[str, Any]]:
        with self._lock:
            viewer = self._users.get(viewer_uid) if viewer_uid is not None else None

            def visible_to_viewer(message: Mapping[str, Any]) -> bool:
                if viewer_uid is None:
                    return True
                if viewer is None:
                    return False
                recipient = str(message.get("recipient") or "all").strip()
                if recipient.casefold() in {"", "all", "*"}:
                    return True
                allowed_recipients = {
                    str(viewer_uid).casefold(),
                    viewer["name"].casefold(),
                    viewer["role"].casefold(),
                }
                return recipient.casefold() in allowed_recipients

            return [
                dict(message)
                for message in self._messages
                if message["id"] > message_id and visible_to_viewer(message)
            ]

    def record_event(
        self,
        event_type: EventType | str,
        *,
        payload_id: str | None = None,
        actor_uid: int | None = None,
        dedupe_key: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> tuple[LabEvent, bool]:
        normalized_type = EventType(event_type)
        with self._lock:
            if dedupe_key and dedupe_key in self._events_by_dedupe_key:
                return self._events_by_dedupe_key[dedupe_key], False
            actor = self._users.get(actor_uid) if actor_uid is not None else None
            event_number = self._next_event_id
            self._next_event_id += 1
            event = LabEvent(
                id=event_number,
                event_id=f"{self.run_id}:event:{event_number}",
                event_type=normalized_type,
                run_id=self.run_id,
                scenario_id=self.scenario_id,
                timestamp=self._timestamp(),
                payload_id=payload_id,
                actor_uid=actor_uid,
                actor_name=actor["name"] if actor else None,
                details=dict(details or {}),
            )
            self._events.append(event)
            if dedupe_key:
                self._events_by_dedupe_key[dedupe_key] = event
            return event, True

    def events(self) -> list[LabEvent]:
        with self._lock:
            return list(self._events)

    def _allocate_payload_id(self) -> str:
        payload_id = f"payload-{self._next_upload_id:06d}"
        self._next_upload_id += 1
        return payload_id

    @staticmethod
    def _safe_basename(original_name: str) -> str:
        basename = original_name.replace("\\", "/").rsplit("/", 1)[-1]
        ascii_name = (
            unicodedata.normalize("NFKD", basename)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", ascii_name).strip("._")
        return safe_name or "upload.svg"

    def _reject_upload(
        self,
        *,
        reason: str,
        status_code: int,
        payload_id: str,
        original_name: str,
    ) -> None:
        self.record_event(
            EventType.CONTROL_BLOCKED,
            payload_id=payload_id,
            dedupe_key=f"{payload_id}:blocked:{reason}",
            details={"reason": reason, "result": "blocked", "filename": original_name},
        )
        raise UploadRejected(reason, status_code, payload_id)

    def store_upload(
        self,
        *,
        original_name: str,
        mimetype: str,
        content: bytes,
    ) -> StoredUpload:
        with self._lock:
            payload_id = self._allocate_payload_id()
            normalized_mimetype = mimetype.partition(";")[0].strip().lower()
            basename = original_name.replace("\\", "/").rsplit("/", 1)[-1]
            if len(content) > self.max_upload_size:
                self._reject_upload(
                    reason="file_too_large",
                    status_code=413,
                    payload_id=payload_id,
                    original_name=original_name,
                )
            if not basename.lower().endswith(".svg"):
                self._reject_upload(
                    reason="invalid_extension",
                    status_code=415,
                    payload_id=payload_id,
                    original_name=original_name,
                )
            if normalized_mimetype != "image/svg+xml":
                self._reject_upload(
                    reason="invalid_mimetype",
                    status_code=415,
                    payload_id=payload_id,
                    original_name=original_name,
                )
            svg_prefix = content.lstrip(b"\xef\xbb\xbf\x00\t\r\n ")[:512].lower()
            if b"<svg" not in svg_prefix:
                self._reject_upload(
                    reason="invalid_svg",
                    status_code=400,
                    payload_id=payload_id,
                    original_name=original_name,
                )
            if self.mode is LabMode.HARDENED:
                self._reject_upload(
                    reason="active_svg_blocked",
                    status_code=415,
                    payload_id=payload_id,
                    original_name=original_name,
                )

            stored_name = f"{payload_id}_{self._safe_basename(original_name)}"
            path = (self.upload_dir / stored_name).resolve()
            if path.parent != self.upload_dir:
                self._reject_upload(
                    reason="unsafe_filename",
                    status_code=400,
                    payload_id=payload_id,
                    original_name=original_name,
                )
            path.write_bytes(content)
            upload = StoredUpload(
                payload_id=payload_id,
                marker=secrets.token_urlsafe(24),
                original_name=original_name,
                stored_name=stored_name,
                mimetype=normalized_mimetype,
                size=len(content),
                path=path,
                active=True,
            )
            self._uploads[stored_name] = upload
            self._uploads_by_payload_id[payload_id] = upload
            self.record_event(
                EventType.UPLOAD_ACCEPTED,
                payload_id=payload_id,
                dedupe_key=f"{payload_id}:upload-accepted",
                details={
                    "filename": stored_name,
                    "mimetype": normalized_mimetype,
                    "size": len(content),
                    "result": "accepted",
                },
            )
            return upload

    def get_upload(self, stored_name: str) -> StoredUpload | None:
        with self._lock:
            return self._uploads.get(stored_name)

    def validate_upload_marker(
        self, payload_id: str, marker: str
    ) -> StoredUpload | None:
        with self._lock:
            upload = self._uploads_by_payload_id.get(payload_id)
            if upload is None or not secrets.compare_digest(upload.marker, marker):
                return None
            return upload

    def has_event(
        self,
        event_type: EventType | str,
        *,
        payload_id: str,
        actor_uid: int | None = None,
    ) -> bool:
        normalized_type = EventType(event_type)
        with self._lock:
            return any(
                event.event_type is normalized_type
                and event.payload_id == payload_id
                and (actor_uid is None or event.actor_uid == actor_uid)
                for event in self._events
            )

    def reset(self) -> dict[str, int]:
        with self._lock:
            result = {
                "messages_removed": len(self._messages),
                "events_removed": len(self._events),
                "uploads_removed": len(self._uploads),
            }
            for upload in self._uploads.values():
                upload.path.unlink(missing_ok=True)
            for child in self.upload_dir.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink(missing_ok=True)
            self._messages.clear()
            self._events.clear()
            self._events_by_dedupe_key.clear()
            self._uploads.clear()
            self._uploads_by_payload_id.clear()
            self._seed_users()
            self._next_message_id = 1
            self._next_event_id = 1
            self._next_upload_id = 1
            self._next_uid = 3
            return result

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            users = [
                {"uid": uid, **user}
                for uid, user in sorted(self._users.items(), key=lambda item: item[0])
            ]
            return {
                "run_id": self.run_id,
                "scenario_id": self.scenario_id,
                "mode": self.mode.value,
                "users": users,
                "messages": [dict(message) for message in self._messages],
                "events": [event.to_dict() for event in self._events],
                "uploads": [upload.to_dict() for upload in self._uploads.values()],
            }

    def summary(self) -> dict[str, int]:
        with self._lock:
            return {
                "event_count": len(self._events),
                "message_count": len(self._messages),
                "actor_count": len(self._users),
            }

    def legacy_attacks(self) -> list[dict[str, Any]]:
        with self._lock:
            attacks: list[dict[str, Any]] = []
            for event in self._events:
                if event.event_type is not EventType.FORGED_ACTION:
                    continue
                details = dict(event.details)
                attacks.append(
                    {
                        "id": len(attacks) + 1,
                        "event_id": event.event_id,
                        "victim_uid": event.actor_uid,
                        "victim_user": event.actor_name,
                        "message": details.get("message", ""),
                        "timestamp": event.timestamp[11:19],
                        "source_ip": details.get("source_ip"),
                        "payload_id": event.payload_id,
                    }
                )
            return attacks

    def export_report(self) -> dict[str, Any]:
        snapshot = self.snapshot()
        event_counts = Counter(event["type"] for event in snapshot["events"])
        return {
            "schema_version": "1.0",
            "generated_at": self._timestamp(),
            "run": snapshot,
            "summary": {
                "event_count": len(snapshot["events"]),
                "message_count": len(snapshot["messages"]),
                "actor_count": len(snapshot["users"]),
                "events_by_type": dict(event_counts),
            },
        }
