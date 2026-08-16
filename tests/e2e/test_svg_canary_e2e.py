"""Browser acceptance checks for the local SVG stored-XSS lesson.

The checks deliberately use two browser contexts: browser cookies are not a
security boundary between vulnerable and hardened modes, and a student demo
must make the attacker and victim roles observable as distinct sessions.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen

import pytest
from playwright.sync_api import Browser, Error, Page, expect
from werkzeug.serving import BaseWSGIServer, make_server

from pikov_websec_lab import create_app


ROOT = Path(__file__).resolve().parents[2]
CANARY = ROOT / "labs" / "svg-stored-xss" / "canary.svg"
INSTRUCTOR_TOKEN = "e2e-known-instructor-token"


@dataclass
class LiveLab:
    """A local, independently configured WSGI application for one test."""

    base_url: str
    server: BaseWSGIServer
    thread: threading.Thread

    def dashboard(self) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}/debug/attack-dashboard/api?token="
            f"{quote(INSTRUCTOR_TOKEN)}",
            headers={"Accept": "application/json"},
        )
        with urlopen(request, timeout=3) as response:  # noqa: S310 -- local fixture
            return json.loads(response.read().decode("utf-8"))

    def close(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()


@pytest.fixture
def lab_server_factory(tmp_path: Path):
    """Start isolated vulnerable or hardened lab runs on loopback only."""

    labs: list[LiveLab] = []

    def start(*, mode: str) -> LiveLab:
        run_number = len(labs) + 1
        app = create_app(
            {
                "TESTING": True,
                "LAB_MODE": mode,
                "RUN_ID": f"e2e-{mode}-{run_number}",
                "SCENARIO_ID": "svg-stored-xss",
                "UPLOAD_DIR": str(tmp_path / f"uploads-{mode}-{run_number}"),
                "MAX_CONTENT_LENGTH": 4096,
                "SECRET_KEY": "e2e-test-secret",
                "INSTRUCTOR_TOKEN": INSTRUCTOR_TOKEN,
                "ENABLE_DEBUG_PANEL": True,
                "COOKIE_SECURE": False,
            }
        )
        server = make_server("127.0.0.1", 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        lab = LiveLab(
            base_url=f"http://127.0.0.1:{server.server_port}",
            server=server,
            thread=thread,
        )
        labs.append(lab)

        for _ in range(30):
            try:
                with urlopen(f"{lab.base_url}/health", timeout=1) as response:  # noqa: S310
                    if response.status == 200:
                        return lab
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("Local WSGI lab did not become ready")

    yield start

    for lab in reversed(labs):
        lab.close()


@pytest.fixture
def chromium_browser(playwright) -> Browser:
    """Launch Chromium directly so ordinary pytest runs skip cleanly if absent."""

    try:
        browser = playwright.chromium.launch()
    except Error as exc:
        pytest.skip(f"Chromium is unavailable: {exc}")
    yield browser
    browser.close()


@pytest.fixture
def isolated_pages(chromium_browser: Browser):
    """Return separate attacker and victim pages with independent cookies."""

    attacker_context = chromium_browser.new_context()
    victim_context = chromium_browser.new_context()
    attacker_page = attacker_context.new_page()
    victim_page = victim_context.new_page()
    try:
        yield attacker_page, victim_page
    finally:
        attacker_context.close()
        victim_context.close()


def _login(page: Page, base_url: str, username: str) -> None:
    page.goto(base_url, wait_until="domcontentloaded")
    page.locator("form.stack-form input[name='username']").fill(username)
    page.locator("form.stack-form button[type='submit']").click()
    page.wait_for_url(f"{base_url}/chat")
    page.locator("#messageForm").wait_for(state="visible")


def _attach_local_request_recorder(page: Page) -> list[tuple[str, str, str | None]]:
    requests: list[tuple[str, str, str | None]] = []
    page.on(
        "request",
        lambda request: requests.append(
            (request.url, request.method, request.post_data)
        ),
    )
    return requests


def _assert_local_only(
    requests: list[tuple[str, str, str | None]], base_url: str
) -> None:
    expected_origin = urlparse(base_url).netloc
    remote_urls = [
        url
        for url, _, _ in requests
        if urlparse(url).scheme in {"http", "https"}
        and urlparse(url).netloc != expected_origin
    ]
    assert remote_urls == [], f"unexpected non-local browser requests: {remote_urls}"


def _wait_for_correlated_timeline(
    lab: LiveLab, payload_id: str, expected_types: list[str]
) -> list[dict[str, Any]]:
    deadline = time.monotonic() + 12
    observed: list[dict[str, Any]] = []
    while time.monotonic() < deadline:
        observed = [
            event
            for event in lab.dashboard()["events"]
            if event["payload_id"] == payload_id
        ]
        if [event["type"] for event in observed] == expected_types:
            return observed
        time.sleep(0.1)
    assert [event["type"] for event in observed] == expected_types
    return observed


def _upload_canary(attacker_page: Page) -> None:
    assert CANARY.is_file(), "the student canary must be part of the repository"
    attacker_page.locator("#recipient").select_option("ДобраяОвечка")
    attacker_page.locator("#fileInput").set_input_files(str(CANARY))
    attacker_page.locator("#sendMessage").click()
    attacker_page.locator("#composerStatus[data-state='success']").wait_for(
        state="visible", timeout=10_000
    )


@pytest.mark.e2e
def test_vulnerable_svg_canary_is_local_and_produces_one_correlated_chain(
    lab_server_factory, isolated_pages
) -> None:
    """The provided canary demonstrates impact without data collection."""

    lab = lab_server_factory(mode="vulnerable")
    attacker_page, victim_page = isolated_pages
    attacker_requests = _attach_local_request_recorder(attacker_page)
    victim_requests = _attach_local_request_recorder(victim_page)

    _login(attacker_page, lab.base_url, "ЗлойБаран")
    _upload_canary(attacker_page)

    _login(victim_page, lab.base_url, "ДобраяОвечка")
    canary_object = victim_page.locator("object.svg-embed")
    canary_object.wait_for(state="attached", timeout=10_000)
    object_url = canary_object.get_attribute("data")
    assert object_url is not None
    correlation = parse_qs(urlparse(object_url).query)
    payload_id = correlation["payload_id"][0]
    marker = correlation["marker"][0]

    timeline = _wait_for_correlated_timeline(
        lab,
        payload_id,
        [
            "UPLOAD_ACCEPTED",
            "SVG_SERVED",
            "PAYLOAD_EXECUTED",
            "FORGED_ACTION",
            "CONTROL_ALLOWED",
        ],
    )
    assert len(timeline) == 5
    assert {event["run_id"] for event in timeline} == {"e2e-vulnerable-1"}
    assert {event["scenario_id"] for event in timeline} == {"svg-stored-xss"}
    assert timeline[2]["actor_uid"] == 2

    expect(
        victim_page.get_by_text("Safe canary: forged action demonstrated")
    ).to_be_visible(timeout=10_000)
    report_request = Request(
        f"{lab.base_url}/api/report?token={quote(INSTRUCTOR_TOKEN)}",
        headers={"Accept": "application/json"},
    )
    with urlopen(report_request, timeout=3) as response:  # noqa: S310 -- local fixture
        report = json.loads(response.read().decode("utf-8"))
    assert [message["content"] for message in report["run"]["messages"]].count(
        "🐑 Safe canary: forged action demonstrated"
    ) == 1

    attacker_page.goto(
        f"{lab.base_url}/debug/attack-dashboard?token={quote(INSTRUCTOR_TOKEN)}",
        wait_until="domcontentloaded",
    )
    evidence = attacker_page.locator("#evidenceTimeline")
    expect(evidence).to_contain_text("CONTROL_ALLOWED", timeout=10_000)

    all_requests = attacker_requests + victim_requests
    _assert_local_only(all_requests, lab.base_url)
    telemetry_bodies = [
        json.loads(body)
        for url, method, body in all_requests
        if method == "POST"
        and urlparse(url).path == "/api/lab-events"
        and body is not None
    ]
    forged_bodies = [
        json.loads(body)
        for url, method, body in all_requests
        if method == "POST"
        and urlparse(url).path == "/api/send_message"
        and body is not None
        and '"lab_event":"FORGED_ACTION"' in body
    ]
    assert telemetry_bodies == [
        {"type": "PAYLOAD_EXECUTED", "payload_id": payload_id, "marker": marker}
    ]
    assert forged_bodies == [
        {
            "text": "🐑 Safe canary: forged action demonstrated",
            "payload_id": payload_id,
            "marker": marker,
            "lab_event": "FORGED_ACTION",
        }
    ]


@pytest.mark.e2e
def test_hardened_mode_reports_the_same_svg_as_blocked_without_active_embedding(
    lab_server_factory, isolated_pages
) -> None:
    """The exact student canary is rejected before it can become active content."""

    lab = lab_server_factory(mode="hardened")
    attacker_page, victim_page = isolated_pages
    attacker_requests = _attach_local_request_recorder(attacker_page)
    victim_requests = _attach_local_request_recorder(victim_page)

    _login(attacker_page, lab.base_url, "ЗлойБаран")
    assert CANARY.is_file()
    attacker_page.locator("#recipient").select_option("ДобраяОвечка")
    attacker_page.locator("#fileInput").set_input_files(str(CANARY))
    attacker_page.locator("#sendMessage").click()
    blocked_status = attacker_page.locator("#composerStatus[data-state='error']")
    expect(blocked_status).to_contain_text("active_svg_blocked", timeout=10_000)

    _login(victim_page, lab.base_url, "ДобраяОвечка")
    assert victim_page.locator("object.svg-embed").count() == 0
    dashboard = lab.dashboard()
    assert [event["type"] for event in dashboard["events"]] == ["CONTROL_BLOCKED"]
    assert dashboard["events"][0]["details"]["reason"] == "active_svg_blocked"
    assert dashboard["summary"]["message_count"] == 0

    _assert_local_only(attacker_requests + victim_requests, lab.base_url)
    assert not [
        url
        for url, _, _ in attacker_requests + victim_requests
        if urlparse(url).path == "/api/lab-events"
    ]
