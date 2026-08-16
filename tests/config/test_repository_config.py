"""Repository-level safety and reproducibility contracts."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def test_compose_is_safe_by_default() -> None:
    """The one-command demo must stay local and constrain the vulnerable process."""
    env = {
        **os.environ,
        "SECRET_KEY": "config-test-secret-key",
        "INSTRUCTOR_TOKEN": "config-test-instructor-token",
    }
    result = subprocess.run(
        ["docker", "compose", "config", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    config = json.loads(result.stdout)
    service = config["services"]["svg-chat"]
    gateway = config["services"]["gateway"]

    assert gateway["ports"][0]["host_ip"] == "127.0.0.1"
    assert "ports" not in service
    assert service["networks"] == {"isolated-lab": None}
    assert config["networks"]["isolated-lab"]["internal"] is True
    for constrained_service in (service, gateway):
        assert constrained_service["restart"] == "no"
        assert constrained_service["read_only"] is True
        assert "ALL" in constrained_service["cap_drop"]
        assert "no-new-privileges:true" in constrained_service["security_opt"]
        assert constrained_service["pids_limit"] <= 128
    assert service["environment"]["DEBUG"] == "false"


def test_development_overrides_are_explicit() -> None:
    assert not (ROOT / "docker-compose.override.yml").exists()
    assert (ROOT / "compose.dev.yaml").is_file()


def test_container_base_and_actions_are_immutable() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert re.search(r"^# syntax=docker/dockerfile:[^\s]+@sha256:[0-9a-f]{64}", dockerfile, re.MULTILINE)
    assert re.search(r"^FROM\s+python:[^\s]+@sha256:[0-9a-f]{64}", dockerfile, re.MULTILINE)

    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    action_refs = re.findall(r"^\s*uses:\s*[^#\n]+@([^\s#]+)", workflow, re.MULTILINE)
    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)

    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert re.search(r"nginxinc/nginx-unprivileged:[^\s]+@sha256:[0-9a-f]{64}", compose)


def test_runtime_dependencies_are_hash_locked() -> None:
    lockfile = ROOT / "requirements.lock"
    assert lockfile.is_file()
    locked = lockfile.read_text(encoding="utf-8")
    assert "--hash=sha256:" in locked
    assert ">=" not in locked


def test_environment_example_is_safe_by_default() -> None:
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "DEBUG=false" in example
    assert "HOST=127.0.0.1" in example
    assert "LAB_MODE=vulnerable" in example
    assert "change-me" not in example


def test_operator_script_keeps_each_pair_local_and_explicit() -> None:
    script = (ROOT / "scripts" / "lab.ps1").read_text(encoding="utf-8")
    assert "ValidateSet(\"vulnerable\", \"hardened\")" in script
    assert "docker compose" in script
    assert "config --format json" in script
    assert "127.0.0.1" in script
    assert "-p" in script


def test_distributed_svg_examples_do_not_collect_browser_data() -> None:
    payloads = [
        *ROOT.glob("*.svg"),
        *(ROOT / "payloads").glob("*.svg"),
        *(ROOT / "labs").rglob("*.svg"),
    ]
    assert payloads
    forbidden = (
        "document.cookie",
        "localstorage",
        "sessionstorage",
        "navigator.clipboard",
        "addEventListener('keydown'",
        'addEventListener("keydown"',
    )
    for payload in payloads:
        content = payload.read_text(encoding="utf-8").lower()
        executable = "\n".join(
            re.findall(r"<script[^>]*>(.*?)</script>", content, flags=re.DOTALL)
        )
        assert not any(token in executable for token in forbidden), payload
        external_urls = re.findall(r"https?://[^\"'\s)]+", content)
        assert all(url.startswith("http://www.w3.org/") for url in external_urls), payload


def test_attribution_and_upstream_link_are_present() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    notice = (ROOT / "NOTICE.md").read_text(encoding="utf-8")
    upstream = "https://github.com/nvmediagithub/evil_sheep_trap"
    assert upstream in readme
    assert upstream in notice
    assert "MIT" in notice


def test_local_markdown_links_resolve() -> None:
    link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    broken: list[str] = []

    for document in ROOT.rglob("*.md"):
        if ".git" in document.parts or ".venv" in document.parts:
            continue
        for target in link_pattern.findall(document.read_text(encoding="utf-8")):
            destination = target.strip().split(maxsplit=1)[0].strip("<>")
            if not destination or destination.startswith(("#", "http://", "https://", "mailto:")):
                continue
            path_text = destination.split("#", 1)[0]
            candidate = (document.parent / path_text).resolve()
            if not candidate.exists():
                broken.append(f"{document.relative_to(ROOT)} -> {destination}")

    assert not broken, "Broken local Markdown links:\n" + "\n".join(broken)
