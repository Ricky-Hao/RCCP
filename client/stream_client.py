import socket
import time
import picamera

while True:
    try:
        camera = picamera.PiCamera()
        camera.resolution = (1280,720)
        camera.framerate = 24
        camera.rotation = 270
        camera.start_preview()
        time.sleep(2)

        client_socket = socket.socket()
        client_socket.connect(('angela.moe', 45837))
        connection = client_socket.makefile("wb")

        camera.start_recording(connection, format='h264', quality=25)
        camera.wait_recording(300)
        camera.stop_recording()
        connection.close()
        client_socket.close()

    except picamera.exc.PiCameraMMALError:
        time.sleep(10)
