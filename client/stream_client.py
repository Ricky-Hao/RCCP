import socket
import time
import picamera

def Connect():
    global client_socket
    client_socket = socket.socket()
    client_socket.connect(('angela.moe', 45837))
    return client_socket.makefile("wb")


while True:
    try:
        camera = picamera.PiCamera()
        camera.resolution = (1280,720)
        camera.framerate = 24
        camera.rotation = 270
        camera.start_preview()
        time.sleep(2)
        connection=Connect()
        camera.start_recording(connection, format='h264', quality=25)
        camera.wait_recording(300)
        camera.stop_recording()
        connection.close()
        client_socket.close()

    except PiCameraMMALError:
        time.sleep(10)
