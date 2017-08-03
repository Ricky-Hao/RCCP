import picamera,time,os,subprocess,logging,json,threading

class LocalRecorder:
    def __init__(self):
        self.LoggerInit()
        self.ConfigInit()
        self.CameraInit()
        self.run()
    
    def LoggerInit(self):
        os.environ['TZ'] = 'Asia/Shanghai'
        self.logger = logging.getLogger(type(self).__name__)
        self.ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setLevel(logging.INFO)
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Logger prepared.")

    def ConfigInit(self):
        self.script_path = os.path.realpath(__file__)
        self.dir_path = os.path.dirname(self.script_path)

        try:
            with open(self.dir_path+"/config.json","r") as f:
                self.config = json.load(f)
        except IOError as err:
            self.logger.critical(err)
            exit

        self.logger.info("Config loaded.")

    def CameraInit(self):
        while True:
            try:
                self.camera = picamera.PiCamera()
                break
            except BaseException as err:
                self.logger.error(err)
                time.sleep(10)
            
        self.camera.resolution = self.config["resolution"]
        self.logger.info("PiCamera resolution: "+str(self.config["resolution"]))

        self.camera.framerate = self.config["framerate"]
        self.logger.info("PiCamera framerate: "+str(self.config["framerate"]))

        self.camera.rotation = self.config["rotation"]
        self.logger.info("PiCamera rotation: "+str(self.config["rotation"]))

        self.logger.info("PiCamera h264 quality: "+str(self.config["quality"]))
        self.logger.info("PiCamera video length: "+str(self.config["video_length"]))
        self.logger.info("PiCamera video store path: "+str(self.config["video_path"]))
        
        self.camera.start_preview()
        self.logger.info("PiCamera prepared.")

    def run(self):
        (filename, filepath)=next(self.GenerateFile())
        self.camera.start_recording(filepath+".h264", format = "h264", quality = self.config["quality"])
        self.logger.info("Start recording "+filename+".h264")
        while True:
            self.camera.wait_recording(self.config["video_length"])
            self.logger.info(filename+".h264"+" recorded.")
           
            Converter(filename, filepath).start()

            (filename, filepath) = next(self.GenerateFile())
            self.camera.split_recording(filepath+".h264")
            self.logger.info("Start recording "+filename+".h264")

    def GenerateFile(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = "PiCamera_"+timestamp
        filepath = self.config["video_path"]+"/"+filename
        yield (filename,filepath)

class Converter(threading.Thread):
    def __init__(self, filename, filepath):
        threading.Thread.__init__(self)
        self.filename = filename
        self.filepath = filepath

    def run(self):
        if subprocess.run(["ffmpeg", "-i", self.filepath+".h264", "-c", "copy", self.filepath+".mp4"], stderr = subprocess.DEVNULL).returncode is 0:
            self.logger.info(self.filename+".h264"+" converted.")
            if subprocess.run(["rm", "-f", self.filepath+".h264"]).returncode is 0:
                self.logger.info(self.filename+".h263"+" deleted.")
            else:
                self.logger.error("Error in delete file: "+self.filename+".h263")
        else:
            self.logger.error("Error in convert file: "+self.filename+".h263")





if __name__ == "__main__":
    LocalRecorder()
        
