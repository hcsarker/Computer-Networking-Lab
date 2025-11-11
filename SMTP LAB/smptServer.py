import socket

CRLF = "\r\n"


def recv_line(conn: socket.socket) -> str:
    data = b""
    while b"\n" not in data:
        chunk = conn.recv(1024)
        if not chunk:
            break
        data += chunk
    return data.decode(errors="replace").rstrip("\r\n")


def send_line(conn: socket.socket, line: str) -> None:
    conn.sendall((line + CRLF).encode())


def handle_client(conn: socket.socket) -> None:
    send_line(conn, "220 localhost Simple SMTP ready")
    mail_from = None
    rcpt_to = None
    data_mode = False
    msg_lines = []

    while True:
        line = recv_line(conn)
        if not line:
            break
        print(f"C: {line}")

        if data_mode:
            if line == ".":
                data_mode = False
                print("--- Message Received ---")
                print("\n".join(msg_lines))
                print("--- End Message ---")
                msg_lines.clear()
                send_line(conn, "250 Message accepted")
            else:
                msg_lines.append(line)
            continue

        parts = line.split(" ", 1)
        cmd = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in {"EHLO", "HELO"}:
            send_line(conn, "250-localhost greets you")
            send_line(conn, "250 HELP")
        elif cmd == "MAIL":
            if arg.upper().startswith("FROM:"):
                mail_from = arg[5:].strip()
                send_line(conn, "250 OK")
            else:
                send_line(conn, "501 Syntax: MAIL FROM:<address>")
        elif cmd == "RCPT":
            if arg.upper().startswith("TO:"):
                rcpt_to = arg[3:].strip()
                send_line(conn, "250 OK")
            else:
                send_line(conn, "501 Syntax: RCPT TO:<address>")
        elif cmd == "DATA":
            if not mail_from or not rcpt_to:
                send_line(conn, "503 Bad sequence of commands")
            else:
                data_mode = True
                send_line(conn, "354 End data with <CR><LF>.<CR><LF>")
        elif cmd == "RSET":
            mail_from = None
            rcpt_to = None
            msg_lines.clear()
            send_line(conn, "250 OK")
        elif cmd == "NOOP":
            send_line(conn, "250 OK")
        elif cmd == "QUIT":
            send_line(conn, "221 Bye")
            break
        elif cmd == "STARTTLS":
            send_line(conn, "454 TLS not available")
        elif cmd == "AUTH":
            send_line(conn, "503 AUTH not supported")
        else:
            send_line(conn, "502 Command not implemented")


def run_server(host: str = "127.0.0.1", port: int = 2525) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(5)
        print(f"SMTP debug server listening on {host}:{port}")
        while True:
            conn, addr = srv.accept()
            print(f"Connection from {addr}")
            try:
                handle_client(conn)
            finally:
                conn.close()


if __name__ == "__main__":
    run_server()
