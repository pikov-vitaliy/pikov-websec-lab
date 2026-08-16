from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from pikov_websec_lab.runtime import EventType, LabMode, LabRun, UploadRejected


def make_run(tmp_path, *, name: str = "run-one", mode: str = "vulnerable") -> LabRun:
    return LabRun(
        run_id=name,
        scenario_id="svg-stored-xss",
        mode=mode,
        upload_dir=tmp_path / name,
        max_upload_size=1024,
    )


def test_mode_is_validated_and_immutable(tmp_path):
    run = make_run(tmp_path)

    assert run.mode is LabMode.VULNERABLE
    with pytest.raises(AttributeError):
        run.mode = LabMode.HARDENED
    with pytest.raises(ValueError, match="LAB_MODE"):
        make_run(tmp_path, name="invalid", mode="training")


def test_lab_run_starts_with_two_seeded_roles(tmp_path):
    snapshot = make_run(tmp_path).snapshot()

    assert snapshot["run_id"] == "run-one"
    assert snapshot["scenario_id"] == "svg-stored-xss"
    assert snapshot["mode"] == "vulnerable"
    assert snapshot["users"] == [
        {"uid": 1, "name": "ЗлойБаран", "role": "attacker"},
        {"uid": 2, "name": "ДобраяОвечка", "role": "victim"},
    ]


def test_lab_run_instances_do_not_share_messages_or_users(tmp_path):
    first = make_run(tmp_path, name="first")
    second = make_run(tmp_path, name="second")

    first.append_message(user_uid=1, content="only first")
    first.login_or_create_user("Student")

    assert [message["content"] for message in first.messages_since(0)] == ["only first"]
    assert second.messages_since(0) == []
    assert second.find_uid_by_name("Student") is None


def test_message_ids_are_atomic_under_concurrency(tmp_path):
    run = make_run(tmp_path)

    with ThreadPoolExecutor(max_workers=8) as pool:
        messages = list(
            pool.map(
                lambda number: run.append_message(user_uid=1, content=f"message-{number}"),
                range(100),
            )
        )

    assert sorted(message["id"] for message in messages) == list(range(1, 101))
    assert len(run.messages_since(0)) == 100


def test_targeted_messages_are_visible_only_to_the_recipient(tmp_path):
    run = make_run(tmp_path)
    run.append_message(
        user_uid=1,
        content="victim only",
        recipient="ДобраяОвечка",
    )
    run.append_message(user_uid=1, content="everyone", recipient="all")

    assert [
        message["content"] for message in run.messages_since(0, viewer_uid=1)
    ] == ["everyone"]
    assert [
        message["content"] for message in run.messages_since(0, viewer_uid=2)
    ] == ["victim only", "everyone"]
    assert len(run.messages_since(0)) == 2


def test_correlated_events_are_typed_and_deduplicated(tmp_path):
    run = make_run(tmp_path)

    first, first_created = run.record_event(
        EventType.PAYLOAD_EXECUTED,
        payload_id="payload-1",
        actor_uid=2,
        dedupe_key="payload-1:executed",
        details={"marker": "canary-1"},
    )
    duplicate, duplicate_created = run.record_event(
        EventType.PAYLOAD_EXECUTED,
        payload_id="payload-1",
        actor_uid=2,
        dedupe_key="payload-1:executed",
        details={"marker": "canary-1"},
    )

    assert first_created is True
    assert duplicate_created is False
    assert duplicate.event_id == first.event_id
    assert first.event_type is EventType.PAYLOAD_EXECUTED
    assert first.run_id == "run-one"
    assert first.scenario_id == "svg-stored-xss"
    assert first.payload_id == "payload-1"
    assert first.actor_uid == 2
    assert len(run.events()) == 1


def test_vulnerable_upload_is_safely_named_and_records_acceptance(tmp_path):
    run = make_run(tmp_path)

    upload = run.store_upload(
        original_name="../../evil sheep.svg",
        mimetype="image/svg+xml",
        content=b"<svg xmlns='http://www.w3.org/2000/svg'><script/></svg>",
    )

    assert upload.stored_name.endswith("_evil_sheep.svg")
    assert "/" not in upload.stored_name
    assert "\\" not in upload.stored_name
    assert ".." not in upload.stored_name
    assert upload.path.parent == (tmp_path / "run-one").resolve()
    assert upload.path.read_bytes().startswith(b"<svg")
    assert [event.event_type for event in run.events()] == [EventType.UPLOAD_ACCEPTED]


def test_hardened_mode_rejects_active_svg_and_records_control_blocked(tmp_path):
    run = make_run(tmp_path, mode="hardened")

    with pytest.raises(UploadRejected) as raised:
        run.store_upload(
            original_name="attack.svg",
            mimetype="image/svg+xml",
            content=b"<svg xmlns='http://www.w3.org/2000/svg'><script/></svg>",
        )

    assert raised.value.status_code == 415
    assert raised.value.reason == "active_svg_blocked"
    assert list((tmp_path / "run-one").glob("*")) == []
    assert [event.event_type for event in run.events()] == [EventType.CONTROL_BLOCKED]


@pytest.mark.parametrize(
    ("name", "mimetype", "content", "reason"),
    [
        ("attack.txt", "image/svg+xml", b"<svg/>", "invalid_extension"),
        ("attack.svg", "text/plain", b"<svg/>", "invalid_mimetype"),
        ("attack.svg", "image/svg+xml", b"not svg", "invalid_svg"),
        ("attack.svg", "image/svg+xml", b"<svg>" + b"x" * 1024, "file_too_large"),
    ],
)
def test_upload_validation_rejects_unsafe_input(tmp_path, name, mimetype, content, reason):
    run = make_run(tmp_path)

    with pytest.raises(UploadRejected, match=reason) as raised:
        run.store_upload(original_name=name, mimetype=mimetype, content=content)

    assert raised.value.reason == reason


def test_reset_is_idempotent_and_restores_the_seed(tmp_path):
    run = make_run(tmp_path)
    run.login_or_create_user("Student")
    run.append_message(user_uid=1, content="message")
    upload = run.store_upload(
        original_name="attack.svg",
        mimetype="image/svg+xml",
        content=b"<svg/>",
    )

    first_result = run.reset()
    first_snapshot = run.snapshot()
    second_result = run.reset()

    assert first_result == {"messages_removed": 1, "events_removed": 1, "uploads_removed": 1}
    assert second_result == {"messages_removed": 0, "events_removed": 0, "uploads_removed": 0}
    assert not upload.path.exists()
    assert first_snapshot == run.snapshot()
    assert run.append_message(user_uid=1, content="after reset")["id"] == 1


def test_report_is_json_serializable_and_contains_event_summary(tmp_path):
    run = make_run(tmp_path)
    run.record_event(
        EventType.PAYLOAD_EXECUTED,
        payload_id="payload-1",
        actor_uid=2,
        dedupe_key="payload-1:executed",
    )

    report = run.export_report()

    assert report["schema_version"] == "1.0"
    assert report["summary"]["event_count"] == 1
    assert report["summary"]["events_by_type"] == {"PAYLOAD_EXECUTED": 1}
    json.dumps(report)
