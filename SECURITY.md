# Security Policy

## ⚠️ Important Disclaimer

**Evil Sheep Trap is an intentionally vulnerable application designed for educational purposes.**

It demonstrates real-world web vulnerabilities (Stored XSS via SVG injection) so
that students and aspiring security professionals can learn by *seeing them in action*.

## What This Project Is ✅

- An **educational sandbox** for learning about XSS attacks
- A **training platform** for cybersecurity courses, CTFs, and self-study
- A **demonstration tool** showing OWASP Top 10 vulnerabilities in a controlled environment

## What This Project Is NOT ❌

- **NOT** a production-ready application
- **NOT** safe to deploy on the public internet
- **NOT** intended for use against real systems or unauthorized targets
- **NOT** a framework for creating actual attack tools

## Known Vulnerabilities

The following vulnerabilities are **intentional** and form the core of the training:

| #  | Vulnerability                | CWE     | Severity | Description                    |
|----|-----------------------------|---------|----------|--------------------------------|
| 1  | Stored XSS via SVG          | CWE-79  | High     | SVG files execute scripts in victim's browser |
| 2  | Missing CSRF protection     | CWE-352 | Medium   | Cookie-based auth without tokens |
| 3  | Insecure cookie flags       | CWE-614 | Medium   | Cookies accessible via JavaScript |
| 4  | No file type validation     | CWE-434 | Medium   | Uploads lack MIME/content checks |
| 5  | Missing CSP headers         | CWE-693 | Low      | No Content-Security-Policy set |

## Safe Usage Guidelines

1. **Run locally only** — use `localhost` or a private Docker network
2. **Never expose port 8080** to the public internet
3. **Use firewall rules** if running on a shared machine
4. **Do not use real credentials** in the chat
5. **Read the docs** before experimenting

## Reporting Issues

If you discover an **unintentional** vulnerability (e.g., RCE via file upload,
server-side code execution), please report it responsibly:

1. Open a GitHub Issue with the label `security-bug`
2. Describe the vulnerability and reproduction steps
3. Do NOT include exploit code that could be misused

## Mitigations

All mitigations are documented in [`docs/vulnerability-analysis.md`](docs/vulnerability-analysis.md).
The lab guide walks you through applying each fix step by step.

## License

MIT — see [LICENSE](LICENSE) for details. Use responsibly.
