import subprocess,socket,time,json,os

class StreamServer:
    def __init__(self):
        self.ReadConfig()
        self.Listen()
        self.run()

    def run(self):
        while(conn = self.socket.accept()[0].makefile("rb")):
            StreamSaver(conn, self.config['vedio_path'])
            conn.close()
    
    def ReadConfig(self):
        self.script_path=os.path.realpath(__file__)
        self.dir_name=os.path.dirname(self.script_path)

        try:
            with open(self.dir_name+"/config/server.json", "r") as f:
                self.config = json.load(f)
        except IOError as err:
            print(err)
            exit()

    def Listen(self):
        self.socket = socket()
        self.socket.bind((self.config['server_ip'], self.config['server_port']))
        self.socket.listen(0)


class StreamSaver:
    def __init__(self, conn, video_path):
        self.connection = conn
        self.video_path = video_path
        self.timestamp = str(int(time.time()))
        self.run()

    def run(self):
        self.h264_filename = "Camera_"+self.timestamp+".h264"
        try:
            with open(self.video_path+"/"+self.h264_filename, "ab+") as f:
                while True:
                    data = self.connection.read(1024)
                    if not data:
                        break
                    f.write(data)
        except IOError as err:
            print(err)
            print(self.h264_filename)
            print(time.ctime())
        self.Convert2MP4()
        
    def Convert2MP4(self):
        self.h264_path = self.video_path + "/" + self.h264_filename
        self.mp4_filename = "Camera_"+self.timestamp+".mp4"
        self.mp4_path = self.video_path + "/" + self.mp4_filename

        try:
            if subprocess.run(["ffmpeg", "-i", self.h264_path, "-c", "copy", self.mp4_path]):
                try:
                    if subprocess.run(["rm", "-f", self.h264_path]):
                        pass
                    else:
                        raise IOError("Could not remove" + self.h264_path)
                except IOError as err:
                    print(err)
            else:
                raise RuntimeError("Could not convert " + self.h264_filename + " to mp4.")
        except RuntimeError as err:
            print(err)

