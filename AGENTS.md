# Repository Guidelines

## Project Structure & Module Organization

The Flask entry point is `app.py`; application code belongs in `src/pikov_websec_lab/`. Keep HTTP adapters in `factory.py` and deterministic, thread-safe lab state in `runtime.py`. Jinja pages live in `templates/`, while offline CSS, JavaScript, and icons live in `static/`. The loopback gateway configuration is `docker/nginx/default.conf`; the Flask service itself stays on an internal network. Each exercise is self-contained under `labs/<scenario>/` with a `manifest.yaml`, safe payload, and mappings to CWE/OWASP/WSTG/ASVS. Student and instructor materials belong in `docs/`. Tests mirror the product: `tests/unit/`, `tests/integration/`, `tests/e2e/`, and `tests/config/`.

## Build, Test, and Development Commands

- `.\scripts\lab.ps1 -Action start -Pair pair-01 -Mode vulnerable -Port 8080` starts one localhost-only Windows lab instance. Stop that exact instance with `.\scripts\lab.ps1 -Action stop -Pair pair-01 -Mode vulnerable -Port 8080`; use `-Mode hardened` for the retest.
- `docker compose up --build` starts the default isolated local stack at `http://127.0.0.1:8080`. Development overrides are explicit: `docker compose -f docker-compose.yml -f compose.dev.yaml up --build`.
- `py -3.12 -m venv .venv` then `.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock` prepares local tooling.
- `.\.venv\Scripts\python.exe -m pytest -m "not e2e" --cov=pikov_websec_lab --cov-fail-under=85` runs the core contract; append `-m e2e` for browser flows. Run `.\.venv\Scripts\python.exe -m flake8 app.py src tests` before review.

## Coding Style & Naming Conventions

Use Python 3.12, four-space indentation, PEP 8, and a 120-character limit (`.flake8`). Prefer `snake_case`, typed public interfaces, immutable mode configuration, and small cohesive modules. HTML uses two-space indentation, semantic elements, labels, visible focus, and `data-i18n` keys rather than inline handlers. Keep trusted JavaScript/CSS in `static/`; hardened CSP permits only external same-origin scripts.

## Testing Guidelines

Write a failing test before a behavior change. Name tests `test_<behavior>.py` and cover both modes: vulnerable must produce one correlated canary timeline; hardened must block the same SVG while the UI works. Include authorization, reset, upload validation, and run-isolation assertions. Browser tests use separate contexts for attacker and victim; never collect real credentials, cookies, keystrokes, clipboard, or external callbacks.

## Commit, Pull Request, and Security Guidelines

Use focused Conventional Commit-style subjects, for example `feat: add instructor preflight`. Explain the scenario, CWE/OWASP mapping, mode-specific result, tests, documentation update, and screenshots for UI changes. Preserve intentional vulnerabilities only when they are declared in a lab manifest; discuss new or removed scenarios first. Run this lab only on localhost or an isolated private network, use synthetic data, and report unintended flaws through `SECURITY.md`.
