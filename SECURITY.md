# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest | :x:                |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **nils.petzall@gmail.com**. You will receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within 7 days.

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

## Disclosure Policy

When the security team receives a security bug report, they will assign it to a primary handler. This person will coordinate the fix and release process, involving the following steps:

1. Confirm the problem and determine the affected versions.
2. Audit code to find any potential similar problems.
3. Prepare fixes for all releases still under maintenance. These fixes will be released as fast as possible to the public.

We follow a coordinated disclosure process:

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity, typically within 30 days for critical issues

## Security Best Practices

When using this software:

- Keep your dependencies up to date
- Review and understand the code you're running
- Run security scans regularly (we use `cargo audit` and `cargo deny`)
- Report vulnerabilities responsibly

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.0 → 1.0.1) and will be clearly marked in the release notes. Critical security updates will be announced via GitHub Security Advisories.

## Acknowledgments

We thank the security researchers and users who report vulnerabilities to us. Your efforts help keep this project secure for everyone.

---

**Note**: Please do not report security vulnerabilities through public GitHub issues. Use the email address provided above instead.
