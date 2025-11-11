# SMTP Lab Project Report

## 1. Introduction

This report documents the design and implementation of a minimal SMTP client and a local debug SMTP server using raw sockets in Python. The goal is to understand the Simple Mail Transfer Protocol (SMTP) by manually issuing commands instead of relying on Python's `smtplib` high-level abstractions.

## 2. Objectives

- Implement a raw socket SMTP client capable of talking to public servers (e.g., Gmail).
- Demonstrate STARTTLS upgrade, repeated EHLO, and AUTH LOGIN flows.
- Provide a lightweight local server for safe offline experimentation.
- Highlight common protocol errors and remediation.
- Reinforce understanding of SMTP command sequence.

## 3. Background

SMTP (RFC 5321) defines how email messages are transferred between mail servers. Key extensions used here:

- STARTTLS (RFC 3207) for opportunistic TLS upgrade.
- AUTH LOGIN (SASL mechanism; base64 encoding of username/password).

Typical flow: `220` banner → `EHLO` → (optional) `STARTTLS` → `EHLO` → (optional) `AUTH` → `MAIL FROM` → `RCPT TO` → `DATA` → message body → `QUIT`.

## 4. Design Overview

### 4.1 Client (`smtpClient.py`)

A linear script reflecting lab expectations. Enhancements added:

- TLS upgrade using `ssl.create_default_context()` with SNI.
- Re-issue EHLO after TLS.
- AUTH LOGIN if credentials present.
- Basic reply code checks per step.

### 4.2 Server (`smptServer.py`)

Simplified single-thread loop:

- Accept connection, emit `220` banner.
- Handle commands with minimal validation.
- Store message lines until terminating '.' line.
- Print received message to stdout.
- Provide instructional rejection for `STARTTLS`, `AUTH`.

### 4.3 Message Handling

Message is terminated using `<CR><LF>.<CR><LF>` as per RFC. This server omits advanced dot-stuffing logic (acceptable for lab scope).

## 5. Implementation Details

- Socket operations use blocking mode and small (1024-byte) reads sufficient for short responses.
- Server handles only one connection at a time (lab simplicity).
- Multi-line EHLO reply simulated with two 250 lines.
- No external dependencies beyond Python standard library.
- Credentials are stored inline for demonstration; production would use environment variables.

## 6. Testing Strategy

### 6.1 Local Tests

1. Start server: `python3 smptServer.py`.
2. Adjust client to use `("127.0.0.1", 2525)` and blank password.
3. Observe successful MAIL/RCPT/DATA flow ending with `250 Message accepted` and `221 Bye`.

### 6.2 Gmail Test

1. Set host: `smtp.gmail.com`, port: `587`.
2. Acquire App Password (Google Account → Security → App Passwords).
3. Run client; verify sequence: 220 → 250 → 220 (STARTTLS) → 250 → 334/235 (AUTH) → 250 → 354 → 250 → 221.

### 6.3 Negative Tests

- Omit second EHLO → expect `503` after attempting AUTH.
- Skip AUTH on Gmail → expect `530 Authentication Required` after MAIL FROM.
- Send DATA before RCPT → expect `503 Bad sequence` from local server.

## 7. Results

- Local server confirmed message receipt and termination logic.
- Gmail flow succeeds with valid App Password; errors observed when steps are skipped match expected protocol behavior.
- Minimal code size offers clear traceability of each SMTP stage.

## 8. Limitations

- No support for multiple RCPT recipients.
- No dot-stuffing escapes inside message body lines starting with '.'.
- Lacks robust parsing of multi-line responses (reads only first line in some cases).
- No concurrency / threading for multiple simultaneous clients.
- No graceful timeout handling or retries.

## 9. Future Improvements

- Implement full multi-line reply parsing per RFC (look for leading status code + '-').
- Add multiple recipient handling and loop over RCPT TO.
- Add environment variable configuration and remove inline secrets entirely.
- Integrate unit tests (pytest) for response parsing and error cases.
- Implement STARTTLS support on the debug server using self-signed certificates.

## 10. Conclusion

The project meets its educational objectives: exposing SMTP command sequence, TLS upgrade requirements, and authentication workflow without relying on high-level libraries. The included local server facilitates experimentation while the Gmail flow demonstrates real-world constraints. This hands-on approach deepens understanding of network protocols and secure communication practices.

## 11. References

- RFC 5321: Simple Mail Transfer Protocol
- RFC 3207: SMTP Service Extension for Secure SMTP over TLS
- Google Workspace / Gmail SMTP guidelines

## 12. Appendix

### Sample Successful Local Session

```
220 localhost Simple SMTP ready
EHLO client
250-localhost greets you
250 HELP
MAIL FROM:<sender@example.com>
250 OK
RCPT TO:<receiver@example.com>
250 OK
DATA
354 End data with <CR><LF>.<CR><LF>
Subject: Test
Hello world.
.
250 Message accepted
QUIT
221 Bye
```

### Sample Gmail Session (abridged)

```
220 smtp.gmail.com ESMTP x23-123456789
HELO Alice
250 smtp.gmail.com at your service
STARTTLS
220 2.0.0 Ready to start TLS
EHLO Alice
250-smtp.gmail.com at your service
250 AUTH LOGIN PLAIN XOAUTH2
AUTH LOGIN
334 VXNlcm5hbWU6
<base64(user)>
334 UGFzc3dvcmQ6
<base64(pass)>
235 2.7.0 Accepted
MAIL FROM:<user@gmail.com>
250 2.1.0 OK
RCPT TO:<receiver@example.com>
250 2.1.5 OK
DATA
354  Go ahead
Subject: Raw SMTP
Body line...
.
250 2.0.0 Queued
QUIT
221 2.0.0 closing connection
```

---

End of Report.
