import picamera,time,os,subprocess,logging,json

class LocalRecorder:
    def __init__(self):
        self.LoggerInit()
        self.ConfigInit()
        self.CameraInit()
    
    def LoggerInit(self):
        os.environ['TZ'] = 'Asia/Shanghai'
        self.logger = logging.getLogger()
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
        self.camera.start_recording(filename+".h264", format = "h264", quality = self.config["quality"])
        self.logger.info("Start recording "+filename+".h264")
        while True:
            self.camera.wait_recording(self.config["video_length"])
            self.logger.info(filename+".h264"+" recorded.")
            
            if subprocess.run(["ffmpeg", "-i", filepath+".h264", "-c", "copy", filename+".mp4"], stderr = subprocess.DEVNULL).returncode is 0:
                self.logger.info(filename+".h264"+" converted.")
                if subprocess.run(["rm", "-f", filepath+".h264"]).returncode is 0:
                    self.logger.info(filename+".h264"+" deleted.")
                else:
                    self.logger.error("Error in delete file: "+filename+".h264")
            else:
                self.logger.error("Error in convert file: "+filename+".h264")

            (filename, filepath) = next(self.GenerateFile())
            self.camera.split_recording(filename+".h264")
            self.logger.info("Start recording "+filename+".h264")

    def GenerateFile(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = "PiCamera_"+timestamp
        filepath = self.config["video_path"]+"/"+h264_filename
        yield (filename,filepath)



if __name__ == "__main__":
    LocalRecorder()
        
