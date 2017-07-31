import subprocess,socket,time,json,os,logging

class StreamServer:
    def __init__(self):
        self.LoggerInit()
        self.ReadConfig()
        self.Listen()
        self.run()

    def run(self):
        while True:
            conn = self.socket.accept()[0].makefile("rb")
            self.logger.info("New connection accepted.")
            StreamSaver(conn, self.config['video_path'])
            conn.close()
    
    def ReadConfig(self):
        self.script_path=os.path.realpath(__file__)
        self.dir_name=os.path.dirname(self.script_path)
        self.logger.info("Reading config from " + self.dir_name + "/config/server.json")

        try:
            with open(self.dir_name+"/config/server.json", "r") as f:
                self.config = json.load(f)
        except IOError as err:
            self.logger.critical(err)
            exit()
        self.logger.info("Reading config done.")

    def Listen(self):
        self.socket = socket.socket()
        self.socket.bind((self.config['server_ip'], self.config['server_port']))
        self.socket.listen(0)
        self.logger.info("Start listening " + self.config['server_ip'] + ":" + str(self.config['server_port']))

    def LoggerInit(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)


class StreamSaver:
    def __init__(self, conn, video_path):
        self.LoggerInit()
        self.connection = conn
        self.video_path = video_path
        os.environ['TZ']="Asia/Shanghai"
        time.tzset()
        self.timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.run()

    def LoggerInit(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)

    def run(self):
        self.h264_filename = "Camera_"+self.timestamp+".h264"
        self.logger.info("Start recording as " + self.h264_filename)
        try:
            with open(self.video_path+"/"+self.h264_filename, "ab+") as f:
                while True:
                    data = self.connection.read(1024)
                    if not data:
                        break
                    f.write(data)
        except IOError as err:
            self.logger.critical(err)
        self.logger.info("Record done.")
        self.Convert2MP4()
        
    def Convert2MP4(self):
        self.h264_path = self.video_path + "/" + self.h264_filename
        self.mp4_filename = "Camera_"+self.timestamp+".mp4"
        self.mp4_path = self.video_path + "/" + self.mp4_filename
        self.logger.info("Start convert " + self.h264_filename + " to " + self.mp4_filename)

        try:
            if subprocess.run(["ffmpeg", "-i", self.h264_path, "-c", "copy", self.mp4_path], stdout=subprocess.DEVNULL).returncode is 0:
                try:
                    if subprocess.run(["rm", "-f", self.h264_path]).returncode is 0:
                        pass
                    else:
                        raise IOError("Could not remove" + self.h264_path)
                except IOError as err:
                    print(err)
            else:
                raise RuntimeError("Could not convert " + self.h264_filename + " to mp4.")
        except RuntimeError as err:
            self.logger.error("Could not to convert " + self.h264_filename)
        self.logger.info("Convert done.")

if __name__ == "__main__":
    StreamServer()
