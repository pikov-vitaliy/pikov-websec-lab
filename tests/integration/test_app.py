from __future__ import annotations

import html
import io
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from pikov_websec_lab.runtime import LabRun


SVG_PAYLOAD = b"""<svg xmlns="http://www.w3.org/2000/svg"><script>/* canary */</script></svg>"""
INSTRUCTOR_TOKEN = "known-instructor-token"


def build_app(tmp_path: Path, *, mode: str = "vulnerable", **overrides):
    from pikov_websec_lab import create_app

    config = {
        "TESTING": True,
        "LAB_MODE": mode,
        "RUN_ID": f"test-{mode}",
        "SCENARIO_ID": "svg-stored-xss",
        "UPLOAD_DIR": str(tmp_path / mode),
        "MAX_CONTENT_LENGTH": 4096,
        "SECRET_KEY": "known-test-secret",
        "INSTRUCTOR_TOKEN": INSTRUCTOR_TOKEN,
        "ENABLE_DEBUG_PANEL": True,
    }
    config.update(overrides)
    return create_app(config)


def login(client, username: str):
    response = client.post("/login", data={"username": username})
    assert response.status_code == 302
    return response


def upload_svg(client, filename: str = "../../attack sheep.svg"):
    return client.post(
        "/send_message",
        data={
            "attachment": (io.BytesIO(SVG_PAYLOAD), filename, "image/svg+xml"),
            "recipient": "victim",
        },
        content_type="multipart/form-data",
    )


def extract_canary(client) -> tuple[str, str, str]:
    messages = client.get("/get_messages?since=0").get_json()["messages"]
    assert len(messages) == 1
    content = html.unescape(messages[0]["content"])
    match = re.search(
        r'data="(?P<url>/file/(?P<stored>[^?\"]+)\?payload_id=(?P<payload>[^&]+)&marker=(?P<marker>[^\"]+))"',
        content,
    )
    assert match is not None
    return match.group("url"), match.group("payload"), match.group("marker")


def dashboard_api(client):
    return client.get(
        "/debug/attack-dashboard/api",
        headers={"X-Lab-Token": INSTRUCTOR_TOKEN},
    )


def test_create_app_contract_is_available(tmp_path):
    from pikov_websec_lab import create_app

    assert callable(create_app)
    assert build_app(tmp_path).testing is True


def test_importing_package_and_wrapper_has_no_upload_directory_side_effect(tmp_path):
    unexpected = tmp_path / "must-not-exist"
    environment = os.environ.copy()
    environment["UPLOAD_DIR"] = str(unexpected)

    completed = subprocess.run(
        [sys.executable, "-c", "import app; import pikov_websec_lab"],
        cwd=Path(__file__).resolve().parents[2],
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert not unexpected.exists()


def test_create_app_rejects_unknown_mode(tmp_path):
    from pikov_websec_lab import create_app

    with pytest.raises(ValueError, match="LAB_MODE"):
        create_app({"TESTING": True, "LAB_MODE": "mixed", "UPLOAD_DIR": tmp_path})


def test_empty_secrets_generate_and_log_one_ephemeral_local_lab_token(
    tmp_path, caplog
):
    app = build_app(
        tmp_path,
        SECRET_KEY="",
        INSTRUCTOR_TOKEN="",
    )

    assert len(app.config["SECRET_KEY"]) >= 32
    assert len(app.config["INSTRUCTOR_TOKEN"]) >= 32
    assert app.config["SECRET_KEY"] != app.config["INSTRUCTOR_TOKEN"]
    token_records = [
        record
        for record in caplog.records
        if "ephemeral instructor token" in record.message.lower()
    ]
    assert len(token_records) == 1
    assert app.config["INSTRUCTOR_TOKEN"] in token_records[0].message
    assert "LOCAL LAB ONLY" in token_records[0].message
    assert app.config["SECRET_KEY"] not in caplog.text


def test_configured_instructor_token_is_never_logged(tmp_path, caplog):
    build_app(tmp_path, INSTRUCTOR_TOKEN="configured-private-token")

    assert "configured-private-token" not in caplog.text
    assert not [
        record
        for record in caplog.records
        if "ephemeral instructor token" in record.message.lower()
    ]


def test_dashboard_html_and_api_require_instructor_token(tmp_path):
    client = build_app(tmp_path).test_client()

    denied_html = client.get("/debug/attack-dashboard")
    denied_api = client.get("/debug/attack-dashboard/api")
    wrong_api = client.get("/debug/attack-dashboard/api?token=wrong")
    allowed_html = client.get(
        f"/debug/attack-dashboard?token={INSTRUCTOR_TOKEN}"
    )
    allowed_api_query = client.get(
        f"/debug/attack-dashboard/api?token={INSTRUCTOR_TOKEN}"
    )
    allowed_api_header = dashboard_api(client)

    assert denied_html.status_code == 403
    assert denied_html.mimetype == "text/html"
    assert 'data-page="error"' in denied_html.get_data(as_text=True)
    assert denied_html.get_json(silent=True) is None
    assert denied_api.status_code == 403
    assert denied_api.get_json() == {"error": "instructor_token_required"}
    assert wrong_api.status_code == 403
    assert allowed_html.status_code == 200
    assert allowed_api_query.status_code == 200
    assert allowed_api_header.status_code == 200


def test_health_and_info_identify_run_without_disclosing_secrets(tmp_path):
    client = build_app(tmp_path).test_client()

    health = client.get("/health")
    info = client.get("/api/info")

    assert health.status_code == 200
    assert health.get_json() == {
        "status": "healthy",
        "mode": "vulnerable",
        "run_id": "test-vulnerable",
        "scenario_id": "svg-stored-xss",
        "message_count": 0,
        "event_count": 0,
    }
    assert info.status_code == 200
    assert info.get_json()["version"] == "2.1.0"
    assert info.get_json()["mode"] == "vulnerable"
    assert info.get_json()["run_id"] == "test-vulnerable"
    serialized = info.get_data(as_text=True)
    assert INSTRUCTOR_TOKEN not in serialized
    assert "known-test-secret" not in serialized


def test_login_exposes_seeded_role_and_mode_aware_cookie(tmp_path):
    vulnerable_client = build_app(tmp_path, mode="vulnerable").test_client()
    vulnerable_login = login(vulnerable_client, "ЗлойБаран")

    assert vulnerable_client.get("/whoami").get_json() == {
        "uid": 1,
        "user": "ЗлойБаран",
        "role": "attacker",
    }
    vulnerable_cookie = vulnerable_login.headers["Set-Cookie"]
    assert "HttpOnly" not in vulnerable_cookie
    assert "SameSite=Lax" in vulnerable_cookie

    hardened_client = build_app(tmp_path, mode="hardened").test_client()
    hardened_login = login(hardened_client, "ДобраяОвечка")
    hardened_cookie = hardened_login.headers["Set-Cookie"]
    assert "HttpOnly" in hardened_cookie
    assert "SameSite=Strict" in hardened_cookie


def test_uid_cookie_is_deterministic_per_run_and_cannot_cross_authenticate_ports(
    tmp_path,
):
    first_app = build_app(
        tmp_path,
        mode="vulnerable",
        RUN_ID="class-run-a",
        UPLOAD_DIR=str(tmp_path / "run-a"),
    )
    second_app = build_app(
        tmp_path,
        mode="hardened",
        RUN_ID="class-run-b",
        UPLOAD_DIR=str(tmp_path / "run-b"),
    )
    same_run_app = build_app(
        tmp_path,
        mode="vulnerable",
        RUN_ID="class-run-a",
        UPLOAD_DIR=str(tmp_path / "run-a-copy"),
    )
    first_client = first_app.test_client()
    second_client = second_app.test_client()
    same_run_client = same_run_app.test_client()

    first_login = first_client.post(
        "/login",
        data={"username": "ЗлойБаран"},
        base_url="http://127.0.0.1:8080",
    )
    first_cookie = first_login.headers["Set-Cookie"].split(";", 1)[0]
    first_cookie_name, first_cookie_value = first_cookie.split("=", 1)
    same_run_login = same_run_client.post(
        "/login",
        data={"username": "ЗлойБаран"},
        base_url="http://127.0.0.1:8090",
    )
    same_run_cookie_name = same_run_login.headers["Set-Cookie"].split("=", 1)[0]

    assert re.fullmatch(r"pikov_uid_[0-9a-f]{16}", first_cookie_name)
    assert same_run_cookie_name == first_cookie_name

    second_client.set_cookie(
        first_cookie_name,
        first_cookie_value,
        domain="127.0.0.1",
    )
    foreign_identity = second_client.get(
        "/whoami", base_url="http://127.0.0.1:8081"
    )
    assert foreign_identity.get_json() == {"uid": None, "user": None, "role": None}

    second_login = second_client.post(
        "/login",
        data={"username": "ДобраяОвечка"},
        base_url="http://127.0.0.1:8081",
    )
    second_cookie_name = second_login.headers["Set-Cookie"].split("=", 1)[0]
    assert second_cookie_name != first_cookie_name
    assert second_client.get(
        "/whoami", base_url="http://127.0.0.1:8081"
    ).get_json()["uid"] == 2

    logout = second_client.get("/logout", base_url="http://127.0.0.1:8081")
    assert logout.headers["Set-Cookie"].startswith(f"{second_cookie_name}=;")
    assert second_client.get(
        "/whoami", base_url="http://127.0.0.1:8081"
    ).get_json() == {"uid": None, "user": None, "role": None}


def test_normal_api_message_is_not_classified_as_an_attack(tmp_path):
    client = build_app(tmp_path).test_client()
    login(client, "ДобраяОвечка")

    response = client.post("/api/send_message", json={"text": "ordinary message"})

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    dashboard = dashboard_api(client).get_json()
    assert dashboard["events"] == []
    assert dashboard["attacks"] == []
    assert dashboard["summary"]["message_count"] == 1


def test_form_message_returns_json_when_frontend_requests_it(tmp_path):
    client = build_app(tmp_path).test_client()
    login(client, "ЗлойБаран")

    response = client.post(
        "/send_message",
        data={"message": "baseline", "recipient": "all"},
        headers={"Accept": "application/json"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"success": True, "id": 1}


def test_recipient_filtering_prevents_attacker_from_rendering_victim_payload(
    tmp_path,
):
    app = build_app(tmp_path)
    attacker = app.test_client()
    victim = app.test_client()
    login(attacker, "ЗлойБаран")
    login(victim, "ДобраяОвечка")

    response = attacker.post(
        "/send_message",
        data={"message": "private", "recipient": "ДобраяОвечка"},
        headers={"Accept": "application/json"},
    )

    assert response.status_code == 200
    assert attacker.get("/get_messages").get_json()["messages"] == []
    victim_messages = victim.get("/get_messages").get_json()["messages"]
    assert [message["content"] for message in victim_messages] == ["private"]


def test_vulnerable_svg_response_allows_canary_but_blocks_external_callbacks(
    tmp_path,
):
    app = build_app(tmp_path)
    attacker = app.test_client()
    victim = app.test_client()
    login(attacker, "ЗлойБаран")
    login(victim, "ДобраяОвечка")
    assert upload_svg(attacker).status_code == 302
    file_url, _, _ = extract_canary(victim)

    served = victim.get(file_url)

    assert served.status_code == 200
    assert served.headers["Content-Security-Policy"] == (
        "default-src 'none'; script-src 'unsafe-inline'; connect-src 'self'; "
        "img-src 'self' data:; style-src 'unsafe-inline'; "
        "font-src 'self' data:; media-src 'self'; object-src 'none'; "
        "base-uri 'none'; form-action 'self'"
    )
    assert "Content-Security-Policy" not in victim.get("/health").headers


def test_vulnerable_canary_produces_exact_correlated_timeline(tmp_path):
    app = build_app(tmp_path)
    attacker = app.test_client()
    victim = app.test_client()
    login(attacker, "ЗлойБаран")
    login(victim, "ДобраяОвечка")

    upload_response = upload_svg(attacker)
    assert upload_response.status_code == 302
    file_url, payload_id, marker = extract_canary(victim)

    served = victim.get(file_url)
    assert served.status_code == 200
    assert served.mimetype == "image/svg+xml"

    ignored_callback = attacker.post(
        "/api/lab-events",
        json={
            "type": "PAYLOAD_EXECUTED",
            "payload_id": payload_id,
            "marker": marker,
        },
    )
    assert ignored_callback.get_json() == {
        "success": True,
        "ignored": True,
        "reason": "wrong_actor",
    }

    callback = victim.post(
        "/api/lab-events",
        json={
            "type": "PAYLOAD_EXECUTED",
            "payload_id": payload_id,
            "marker": marker,
        },
    )
    duplicate_callback = victim.post(
        "/api/lab-events",
        json={
            "type": "PAYLOAD_EXECUTED",
            "payload_id": payload_id,
            "marker": marker,
        },
    )
    assert callback.status_code == 200
    assert callback.get_json()["created"] is True
    assert duplicate_callback.get_json()["created"] is False

    forged = {
        "text": "forged by the canary",
        "payload_id": payload_id,
        "marker": marker,
        "lab_event": "FORGED_ACTION",
    }
    first_action = victim.post("/api/send_message", json=forged)
    duplicate_action = victim.post("/api/send_message", json=forged)
    assert first_action.status_code == 200
    assert first_action.get_json()["created"] is True
    assert duplicate_action.get_json()["created"] is False

    dashboard = dashboard_api(victim).get_json()
    assert [event["type"] for event in dashboard["events"]] == [
        "UPLOAD_ACCEPTED",
        "SVG_SERVED",
        "PAYLOAD_EXECUTED",
        "FORGED_ACTION",
        "CONTROL_ALLOWED",
    ]
    assert {event["payload_id"] for event in dashboard["events"]} == {payload_id}
    assert dashboard["events"][2]["actor_uid"] == 2
    assert dashboard["summary"]["event_count"] == 5
    assert [
        message["content"] for message in victim.get("/get_messages").get_json()["messages"]
    ].count("forged by the canary") == 1


def test_canary_rejects_unknown_marker_without_recording_an_event(tmp_path):
    app = build_app(tmp_path)
    attacker = app.test_client()
    victim = app.test_client()
    login(attacker, "ЗлойБаран")
    login(victim, "ДобраяОвечка")
    upload_svg(attacker)
    _, payload_id, _ = extract_canary(victim)

    response = victim.post(
        "/api/lab-events",
        json={
            "type": "PAYLOAD_EXECUTED",
            "payload_id": payload_id,
            "marker": "wrong",
        },
    )

    assert response.status_code == 403
    types = [
        event["type"]
        for event in dashboard_api(victim).get_json()["events"]
    ]
    assert types == ["UPLOAD_ACCEPTED"]


def test_hardened_mode_rejects_same_svg_and_sets_security_headers(tmp_path):
    client = build_app(tmp_path, mode="hardened").test_client()
    login(client, "ЗлойБаран")

    response = upload_svg(client, "attack.svg")

    assert response.status_code == 415
    assert response.get_json()["error"] == "active_svg_blocked"
    dashboard = dashboard_api(client).get_json()
    assert [event["type"] for event in dashboard["events"]] == ["CONTROL_BLOCKED"]
    assert dashboard["summary"]["message_count"] == 0
    assert list((tmp_path / "hardened").glob("*")) == []
    policy = response.headers["Content-Security-Policy"]
    assert "script-src 'self'" in policy
    assert "object-src 'none'" in policy
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Lab-Mode"] == "hardened"


@pytest.mark.parametrize(
    ("filename", "mimetype", "expected_error"),
    [
        ("attack.txt", "image/svg+xml", "invalid_extension"),
        ("attack.svg", "text/plain", "invalid_mimetype"),
    ],
)
def test_upload_route_enforces_filename_and_mimetype(
    tmp_path, filename, mimetype, expected_error
):
    client = build_app(tmp_path).test_client()
    login(client, "ЗлойБаран")

    response = client.post(
        "/send_message",
        data={"attachment": (io.BytesIO(SVG_PAYLOAD), filename, mimetype)},
        content_type="multipart/form-data",
    )

    assert response.status_code == 415
    assert response.get_json()["error"] == expected_error


def test_oversized_upload_returns_413_json(tmp_path):
    client = build_app(tmp_path, MAX_CONTENT_LENGTH=512).test_client()
    login(client, "ЗлойБаран")

    response = client.post(
        "/send_message",
        data={
            "attachment": (
                io.BytesIO(b"<svg>" + b"x" * 2048),
                "large.svg",
                "image/svg+xml",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert response.get_json() == {"error": "file_too_large"}


def test_reset_requires_login_and_instructor_token_and_is_idempotent(tmp_path):
    app = build_app(tmp_path)
    anonymous = app.test_client()
    client = app.test_client()
    login(client, "ЗлойБаран")
    client.post("/api/send_message", json={"text": "message"})

    unauthorized = anonymous.post(
        "/clear_chat",
        headers={"Accept": "application/json", "X-Lab-Token": INSTRUCTOR_TOKEN},
    )
    missing_token = client.post("/clear_chat", headers={"Accept": "application/json"})
    wrong_token = client.post(
        "/clear_chat",
        headers={"Accept": "application/json", "X-Lab-Token": "wrong"},
    )
    first = client.post(
        "/clear_chat",
        headers={"Accept": "application/json", "X-Lab-Token": INSTRUCTOR_TOKEN},
    )
    second = client.post(
        "/clear_chat",
        headers={"Accept": "application/json", "X-Lab-Token": INSTRUCTOR_TOKEN},
    )

    assert unauthorized.status_code == 401
    assert missing_token.status_code == 403
    assert wrong_token.status_code == 403
    assert first.get_json()["reset"] == {
        "messages_removed": 1,
        "events_removed": 0,
        "uploads_removed": 0,
    }
    assert second.get_json()["reset"] == {
        "messages_removed": 0,
        "events_removed": 0,
        "uploads_removed": 0,
    }


def test_report_export_requires_instructor_token(tmp_path):
    client = build_app(tmp_path).test_client()

    denied = client.get("/api/report")
    allowed = client.get(f"/api/report?token={INSTRUCTOR_TOKEN}")

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.get_json()["schema_version"] == "1.0"
    assert "attachment" in allowed.headers["Content-Disposition"]


def test_injected_runtimes_keep_two_apps_isolated(tmp_path):
    from pikov_websec_lab import create_app

    first_runtime = LabRun(
        run_id="first",
        scenario_id="svg-stored-xss",
        mode="vulnerable",
        upload_dir=tmp_path / "first",
    )
    second_runtime = LabRun(
        run_id="second",
        scenario_id="svg-stored-xss",
        mode="vulnerable",
        upload_dir=tmp_path / "second",
    )
    config = {
        "TESTING": True,
        "SECRET_KEY": "secret",
        "INSTRUCTOR_TOKEN": INSTRUCTOR_TOKEN,
    }
    first = create_app(config, runtime=first_runtime).test_client()
    second = create_app(config, runtime=second_runtime).test_client()
    login(first, "ЗлойБаран")
    login(second, "ЗлойБаран")

    first.post("/api/send_message", json={"text": "first only"})

    assert len(first.get("/get_messages").get_json()["messages"]) == 1
    assert second.get("/get_messages").get_json()["messages"] == []
