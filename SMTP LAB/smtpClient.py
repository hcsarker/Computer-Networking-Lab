from socket import *
import ssl
import base64

# Message to send
msg = "\r\n I love computer networks!"
endmsg = "\r\n.\r\n"

# Choose a mail server (for example, Gmail)
mailserver = ("smtp.gmail.com", 587)   # SMTP server and port

# Credentials (Gmail requires App Password if 2FA enabled)
username = "hcsarker2002@gmail.com"
password = "xsnb urjm mwoa sjqb"

# Create socket called clientSocket and establish a TCP connection with mailserver
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)

# Receive initial greeting from server
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')

# Send HELO command and print server response (Gmail also accepts HELO here)
heloCommand = 'HELO Alice\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')

# Since Gmail requires encryption, start TLS
clientSocket.send("STARTTLS\r\n".encode())
recv_tls = clientSocket.recv(1024).decode()
print(recv_tls)
if recv_tls[:3] != '220':
    print("TLS not started properly.")
else:
    # Wrap socket with TLS using SNI and default CA validation
    context = ssl.create_default_context()
    clientSocket = context.wrap_socket(clientSocket, server_hostname=mailserver[0])

    # After STARTTLS, you MUST send EHLO again to get capabilities
    ehloCommand = 'EHLO Alice\r\n'
    clientSocket.send(ehloCommand.encode())
    recv_ehlo = clientSocket.recv(1024).decode()
    print(recv_ehlo)
    if recv_ehlo[:3] != '250':
        print('250 reply not received from server after EHLO (post-TLS).')

    # Authenticate if username/password provided (required by Gmail)
    if username and password:
        clientSocket.send("AUTH LOGIN\r\n".encode())
        recv_auth = clientSocket.recv(1024).decode()
        print(recv_auth)
        if not recv_auth.startswith('334'):
            print('AUTH LOGIN not accepted by server.')

        clientSocket.send((base64.b64encode(username.encode()).decode() + "\r\n").encode())
        recv_user = clientSocket.recv(1024).decode()
        print(recv_user)
        if not recv_user.startswith('334'):
            print('Username not accepted.')

        clientSocket.send((base64.b64encode(password.encode()).decode() + "\r\n").encode())
        recv_pass = clientSocket.recv(1024).decode()
        print(recv_pass)
        if not recv_pass.startswith('235'):
            print('235 reply not received after AUTH (authentication failed).')

# Now send MAIL FROM command
mailFrom = f"MAIL FROM:<{username}>\r\n"
clientSocket.send(mailFrom.encode())
recv2 = clientSocket.recv(1024).decode()
print(recv2)
if recv2[:3] != '250':
    print('250 reply not received from server after MAIL FROM.')

# Send RCPT TO command
rcptTo = "RCPT TO:<ug2102019@cse.pstu.ac.bd>\r\n"
clientSocket.send(rcptTo.encode())
recv3 = clientSocket.recv(1024).decode()
print(recv3)
if recv3[:3] != '250':
    print('250 reply not received from server after RCPT TO.')

# Send DATA command
data = "DATA\r\n"
clientSocket.send(data.encode())
recv4 = clientSocket.recv(1024).decode()
print(recv4)
if recv4[:3] != '354':
    print('354 reply not received from server after DATA.')

# Send message data
subject = "Subject: SMTP Lab Test\r\n"
message = subject + msg
clientSocket.send(message.encode())

# Message ends with a single period
clientSocket.send(endmsg.encode())

# Server response after sending message
recv_msg = clientSocket.recv(1024).decode()
print(recv_msg)
if recv_msg[:3] != '250':
    print('250 reply not received from server after message sent.')

# Send QUIT command
quitCommand = "QUIT\r\n"
clientSocket.send(quitCommand.encode())
recv5 = clientSocket.recv(1024).decode()
print(recv5)
if recv5[:3] != '221':
    print('221 reply not received from server.')

# Close socket
clientSocket.close()
