from socket import *

# Message to send
msg = "\r\n I love computer networks!"
endmsg = "\r\n.\r\n"

# Choose a mail server (for example, Gmail)
mailserver = ("smtp.gmail.com", 587)   # SMTP server and port

# Create socket called clientSocket and establish a TCP connection with mailserver
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)

# Receive initial greeting from server
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')

# Send HELO command and print server response
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
    import ssl
    clientSocket = ssl.wrap_socket(clientSocket)

# Now send MAIL FROM command
mailFrom = "MAIL FROM:<your_email@gmail.com>\r\n"
clientSocket.send(mailFrom.encode())
recv2 = clientSocket.recv(1024).decode()
print(recv2)
if recv2[:3] != '250':
    print('250 reply not received from server after MAIL FROM.')

# Send RCPT TO command
rcptTo = "RCPT TO:<receiver_email@example.com>\r\n"
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
