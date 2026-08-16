"""Source-level contracts for the offline training interface.

These tests intentionally use only the Python standard library so contributors
can run them before installing the Flask application dependencies.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class FrontendContractTests(unittest.TestCase):
    def test_primary_brand_and_current_owasp_category(self) -> None:
        base = read(TEMPLATES / "base.html")
        login = read(TEMPLATES / "login.html")
        catalog = read(STATIC / "js" / "app.js")

        self.assertIn("<strong>Pikov WebSec Lab</strong>", base)
        self.assertIn('aria-label="Pikov WebSec Lab"', base)
        self.assertIn("Evil Sheep Trap", base)
        self.assertIn("OWASP A05:2025", login)
        self.assertIn("A03:2021", login)

        combined = "\n".join([base, login, catalog, *[read(path) for path in TEMPLATES.glob("*.html")]])
        self.assertNotIn("Evil Sheep Trap —", combined)
        self.assertNotIn("OWASP A03", combined)

    def test_shared_offline_assets_exist(self) -> None:
        self.assertTrue((TEMPLATES / "base.html").is_file())
        self.assertTrue((STATIC / "css" / "app.css").is_file())
        self.assertTrue((STATIC / "js" / "app.js").is_file())
        self.assertTrue((STATIC / "favicon.svg").is_file())
        self.assertIn('/static/favicon.svg', read(TEMPLATES / "base.html"))

    def test_pages_use_shared_assets_without_inline_handlers(self) -> None:
        for name in ("login.html", "chat.html", "dashboard.html", "403.html", "404.html", "500.html"):
            with self.subTest(template=name):
                source = read(TEMPLATES / name)
                self.assertIn('{% extends "base.html" %}', source)
                self.assertNotRegex(source, r"<style\b")
                self.assertNotRegex(source, r"<script(?![^>]+src=)")
                self.assertNotRegex(source, r"\son[a-z]+\s*=")

        base = read(TEMPLATES / "base.html")
        self.assertIn("/static/css/app.css", base)
        self.assertIn("/static/js/app.js", base)
        self.assertIn('class="skip-link"', base)
        self.assertIn('id="main-content"', base)

    def test_forbidden_page_explains_instructor_link(self) -> None:
        source = read(TEMPLATES / "403.html")
        self.assertIn('data-title-key="meta.forbidden"', source)
        self.assertIn('data-i18n="error.forbiddenTitle"', source)
        self.assertIn('data-i18n="error.forbiddenBody"', source)
        self.assertNotIn('name="token"', source)

    def test_chat_exposes_seven_guided_steps_and_safe_composer(self) -> None:
        source = read(TEMPLATES / "chat.html")
        self.assertEqual(7, len(re.findall(r'data-step="[1-7]"', source)))
        for marker in (
            'data-role-badge',
            'data-mode-badge',
            'data-run-badge',
            'name="message"',
            'name="attachment"',
            'name="recipient"',
            'aria-live="polite"',
            'role="log"',
            'data-i18n="chat.canary.title"',
            'data-i18n="chat.warning.title"',
        ):
            self.assertIn(marker, source)

    def test_dashboard_has_evidence_and_instructor_controls(self) -> None:
        source = read(TEMPLATES / "dashboard.html")
        for marker in (
            'id="connectionStatus"',
            'id="instructorAccessNotice"',
            'id="evidenceTimeline"',
            'id="pauseDashboard"',
            'id="resetLab"',
            'id="exportReport"',
            'id="projectorMode"',
            '<caption',
            'scope="col"',
            'aria-live="polite"',
        ):
            self.assertIn(marker, source)

        styles = read(STATIC / "css" / "app.css")
        self.assertIn('class="dashboard-heading-copy"', source)
        self.assertIn("body.projector-mode .dashboard-heading-copy", styles)
        self.assertNotIn("body.projector-mode .dashboard-heading > div", styles)
        self.assertIn(".dashboard-access-note[hidden]", styles)

        behavior = read(STATIC / "js" / "app.js")
        self.assertIn("if (!dashboardToken())", behavior)
        self.assertEqual(2, behavior.count('"dashboard.tokenNotice"'))
        self.assertIn('setGlobalStatus(translate("status.resetDone"))', behavior)

    def test_catalog_is_bilingual_and_updates_document_language(self) -> None:
        source = read(STATIC / "js" / "app.js")
        self.assertRegex(source, r"\bru\s*:\s*\{")
        self.assertRegex(source, r"\ben\s*:\s*\{")
        self.assertIn("document.documentElement.lang", source)
        self.assertIn("localStorage.setItem", source)
        self.assertIn("aria-pressed", source)

        for template in TEMPLATES.glob("*.html"):
            with self.subTest(template=template.name):
                self.assertNotRegex(read(template), r">\s*(Dashboard|Logout|Clear|Your UID|Auto-refresh)\s*<")

        dynamic_keys = ("role.studentShort", "role.instructorShort")
        for key in dynamic_keys:
            with self.subTest(dynamic_key=key):
                self.assertEqual(2, source.count(f'"{key}"'))

    def test_locale_change_preserves_dashboard_snapshot(self) -> None:
        source = read(STATIC / "js" / "app.js")
        self.assertIn("let dashboardSnapshot", source)
        self.assertIn("renderDashboard(dashboardSnapshot)", source)

    def test_dashboard_normalizes_backend_event_shape(self) -> None:
        source = read(STATIC / "js" / "app.js")
        self.assertIn("const stage = knownStages.has(stageValue) ? stageValue : inferStage(stageValue)", source)
        self.assertIn("raw.details?.message", source)
        self.assertIn("raw.details?.filename", source)
        self.assertNotIn("const detail = raw.details ||", source)
        self.assertIn('["accepted", "served", "observed", "allowed"]', source)

    def test_login_keeps_declared_mode_when_metadata_is_incomplete(self) -> None:
        template = read(TEMPLATES / "login.html")
        source = read(STATIC / "js" / "app.js")
        self.assertIn('data-initial-mode="vulnerable"', template)
        self.assertIn("info.mode || info.lab_mode || badge.dataset.initialMode", source)

    def test_polling_uses_single_cursor_and_expected_routes(self) -> None:
        source = read(STATIC / "js" / "app.js")
        for route in (
            "/get_messages",
            "/whoami",
            "/api/info",
            "/debug/attack-dashboard/api",
            "/api/report",
            "/clear_chat",
        ):
            self.assertIn(route, source)
        self.assertIn("lastMessageId", source)
        self.assertIn("lastEventId", source)
        self.assertNotIn("setInterval(", source)

    def test_accessibility_css_and_offline_fonts(self) -> None:
        source = read(STATIC / "css" / "app.css")
        self.assertIn(":focus-visible", source)
        self.assertIn("prefers-reduced-motion", source)
        self.assertIn("forced-colors", source)
        self.assertNotIn("@import", source)
        self.assertNotIn("fonts.googleapis.com", source)
        self.assertRegex(source, r"font-family:\s*(?:ui-|system-ui|-apple-system)")

    def test_frontend_contains_no_attack_collection_code(self) -> None:
        combined = "\n".join(
            read(path)
            for path in [*TEMPLATES.glob("*.html"), *(STATIC / "js").glob("*.js")]
        ).lower()
        for forbidden in ("document.cookie", "keylogger", "collect keystrokes", "executeattack"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
