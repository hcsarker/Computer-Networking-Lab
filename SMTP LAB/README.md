# SMTP Lab Project

A simple educational implementation of an SMTP client (raw sockets, no `smtplib`) plus a tiny local SMTP debug server to help you understand the SMTP protocol flow (HELO/EHLO, STARTTLS, AUTH LOGIN, MAIL FROM, RCPT TO, DATA, QUIT).

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
  - [Local Debug Server](#local-debug-server)
  - [Sending via Gmail](#sending-via-gmail)
- [Features](#features)
- [Project Structure](#project-structure)
- [Protocol Flow Explained](#protocol-flow-explained)
- [Common Errors & Fixes](#common-errors--fixes)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

## Overview

This lab demonstrates how SMTP works at the command/reply level by manually constructing the dialogue with a server. It intentionally avoids Python's `smtplib` to expose the raw protocol steps including TLS upgrade and authentication.

## Architecture

| Component       | Purpose                                                                                                                       |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `smtpClient.py` | Connects to an SMTP server, upgrades to TLS (STARTTLS), optionally authenticates (AUTH LOGIN), and sends a simple text email. |
| `smptServer.py` | Minimal local SMTP debug server (no TLS or AUTH) so you can practice without external dependencies.                           |

## Installation

No external dependencies are required beyond Python 3.10+ (standard library only).

```bash
# (Optional) create a virtual environment
python3 -m venv venv
source venv/bin/activate
```

## Usage

### Local Debug Server

Run the test server in one terminal:

```bash
python3 smptServer.py
```

It listens on `127.0.0.1:2525`.

In another terminal, run the client pointing to the local server (no TLS/auth required):

```bash
python3 smtpClient.py
```

If your client is still configured for Gmail, adjust the top of `smtpClient.py`:

```python
mailserver = ("127.0.0.1", 2525)
username = "sender@example.com"  # Not used by local server
password = ""                    # Leave blank
```

Expected output (abridged):

```
220 localhost Simple SMTP ready
250-localhost greets you
250 HELP
354 End data with <CR><LF>.<CR><LF>
250 Message accepted
221 Bye
```

### Sending via Gmail

Requirements:

- Port 587 (submission) with STARTTLS.
- App Password (if your Google account has 2FA; normal password will fail with 535 / 534).

Adjust variables near the top of `smtpClient.py`:

```python
mailserver = ("smtp.gmail.com", 587)
username = "your_account@gmail.com"
password = "your_app_password"  # 16-character App Password
```

Run:

```bash
python3 smtpClient.py
```

You should see a sequence of `220`, `250`, `220` (after STARTTLS), `250` (post-EHLO), `235` (after AUTH), `250` (MAIL/RCPT), `354` (DATA), `250` (message queued), `221` (QUIT).

## Features

- Raw socket implementation (no abstraction layer)
- STARTTLS upgrade using `ssl.create_default_context()` + SNI
- Re-EHLO after TLS (required by RFC 3207)
- AUTH LOGIN (Base64 username + password)
- Basic error code checking & printing
- Local debug server for offline experimentation

## Project Structure

```
SMTP LAB/
  smtpClient.py     # Raw SMTP client
  smptServer.py     # Local debug server (no TLS/auth)
  README.md         # This documentation
```

## Protocol Flow Explained

1. 220 Service ready (banner)
2. EHLO / HELO identifies the client and requests capabilities.
3. STARTTLS (optional) asks to begin TLS handshake.
4. EHLO again (capabilities may change under TLS).
5. AUTH LOGIN (optional) to authenticate.
6. MAIL FROM specifies the envelope sender.
7. RCPT TO specifies each recipient.
8. DATA signals start of message content.
9. Message headers + blank line + body.
10. Single period line terminates the data section.
11. QUIT gracefully closes the session.

## Common Errors & Fixes

| Code / Symptom                | Cause                             | Fix                                                  |
| ----------------------------- | --------------------------------- | ---------------------------------------------------- |
| 530 Auth required             | Tried MAIL before AUTH on Gmail   | Do STARTTLS then AUTH LOGIN first                    |
| 503 Bad sequence              | Forgot second EHLO after STARTTLS | Send EHLO again post-TLS                             |
| TLS failure / handshake error | Missing SNI / outdated wrap       | Use `context.wrap_socket(..., server_hostname=host)` |
| 535 / 534 Auth failure        | Wrong credentials                 | Use valid App Password                               |
| Hanging after DATA            | Missing `\r\n.\r\n` terminator    | Ensure end marker line with just a period            |

## Security Notes

- Never commit real passwords or app passwords to version control.
- Use environment variables or a secrets manager for credentials in production projects.
- This educational client does not implement full robustness (multi-line reply parsing, pipelining, 8BITMIME, etc.).

## Contributing

Educational lab; contributions (improved parsing, tests) are welcome. Open a PR or issue.

## License

MIT. [See LICENSE](../License) for details.

---

Happy learning: explore SMTP by modifying commands, forcing errors, and observing server replies.
