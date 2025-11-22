from socket import *
import ssl
import base64
import sys

# Message to send
msg = "\r\n Hello Sir,\r\nThis is my SMTP Lab test message.\r\nRegards,\r\nHridoy."
endmsg = "\r\n.\r\n"

# Gmail SMTP ("smtp.pstu.ac.bd", 25) for PSTU SMTP server
mailserver = ("smtp.gmail.com", 587)

# Create socket and connect
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)

recv = clientSocket.recv(1024).decode()
print("S:", recv.strip())
if recv[:3] != '220':
    print('220 reply not received from server.')
    

# EHLO (better than HELO)
ehlo = "EHLO myhost\r\n"
clientSocket.send(ehlo.encode())
recv1 = clientSocket.recv(1024).decode()
print("S:", recv1.strip())
if recv1[:3] != '250':
    print('250 reply not received from server on EHLO (before TLS).')

# STARTTLS
clientSocket.send("STARTTLS\r\n".encode())
recv_tls = clientSocket.recv(1024).decode()
print("S:", recv_tls.strip())
if recv_tls[:3] != '220':
    print("TLS not started properly. If using a server without STARTTLS, skip this step.")
else:
    
    context = ssl.create_default_context()
    clientSocket = context.wrap_socket(clientSocket, server_hostname=mailserver[0])

    clientSocket.send(ehlo.encode())
    recv_ehlo2 = clientSocket.recv(1024).decode()
    print("S (after TLS):", recv_ehlo2.strip())
    if recv_ehlo2[:3] != '250':
        print("250 reply not received from server on EHLO (after TLS).")

# --- Authentication (Gmail requires login) ---
USERNAME = "hcsarker2002@gmail.com"      
APP_PASSWORD = "xsnb urjm mwoa sjqb"   

# AUTH LOGIN sequence (base64 username, base64 password)
clientSocket.send("AUTH LOGIN\r\n".encode())
recv_a = clientSocket.recv(1024).decode()
print("S:", recv_a.strip())
if recv_a[:3] not in ('334','235'):

    print("AUTH not started correctly (server response above).")

# send username (base64)
clientSocket.send((base64.b64encode(USERNAME.encode()) + b"\r\n"))
recv_u = clientSocket.recv(1024).decode()
print("S:", recv_u.strip())

# send password (base64)
clientSocket.send((base64.b64encode(APP_PASSWORD.encode()) + b"\r\n"))
recv_p = clientSocket.recv(1024).decode()
print("S:", recv_p.strip())
if recv_p[:3] != '235':
    print("Authentication failed. Check app password and account settings.")
    

# Now MAIL FROM / RCPT TO / DATA
mailFrom = f"MAIL FROM:<{USERNAME}>\r\n"
clientSocket.send(mailFrom.encode())
recv2 = clientSocket.recv(1024).decode()
print("S:", recv2.strip())

rcptTo = "RCPT TO:<ug2102019@cse.pstu.ac.bd>\r\n"   
clientSocket.send(rcptTo.encode())
recv3 = clientSocket.recv(1024).decode()
print("S:", recv3.strip())

# DATA
clientSocket.send("DATA\r\n".encode())
recv4 = clientSocket.recv(1024).decode()
print("S:", recv4.strip())
if recv4[:3] != '354':
    print("Server did not accept DATA command.")

# send headers + body
subject = "Subject: Lab 3 - SMTP Client Test\r\n"
clientSocket.send((subject + msg + "\r\n").encode())

# end of message
clientSocket.send(endmsg.encode())

recv_msg = clientSocket.recv(1024).decode()
print("S:", recv_msg.strip())

# QUIT
clientSocket.send("QUIT\r\n".encode())
recv5 = clientSocket.recv(1024).decode()
print("S:", recv5.strip())

clientSocket.close()
