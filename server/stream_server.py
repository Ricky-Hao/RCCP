import socket
import time

# Bind server socket and listening.
server_socket = socket.socket()
server_socket.bind("0.0.0.0",45837)
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it.
connection = server_socket.accept()[0].makefile('rb')

try:
    #cmdline = ['vlc', '--demux', 'h264', '-']
    #player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
    f = open("/home/ricky/ras/video/camera_"+int(time.time())+".raw","ab+")
    while True:
        data=connection.read(1024)
        if not data:
            break
        #player.stdin.write(data)
        f.write(data)
finally:
    connection.close()
    server_socket.close()
    #player.terminate()
    f.close()
