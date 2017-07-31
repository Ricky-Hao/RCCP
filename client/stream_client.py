import socket,picamera,logging,os,time,json

class PiCamera:
    def __init__(self):
        self.LoggerInit()
        self.ReadConfig()
        self.CameraInit()
        self.run()

    def run(self):
        while True:
            self.ClientStart()
            self.Recording()
            self.ClientStop()


    def LoggerInit(self):
        os.environ['TZ'] = "Asia/Shanghai"
        self.logger = logging.getLogger(type(self).__name)
        self.logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("'%(asctime)s - %(name)s - %(levelname)s - %(message)s'")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def CameraInit(self):
        try:
            self.camera = picamera.PiCamera()
        except picamera.exc.PiCameraMMALError as err:
            self.logger.critical(err)
            self.logger.critical("Please close all the program which use the picamera.")
        self.logger.info("PiCamera started.")

        self.camera.resolution = self.config['resolution']
        self.logger.info("PiCamera resolution: "+self.config['resolution'])
        self.camera.framerate = self.config['framerate']
        self.logger.info("PiCamera framerate: "+self.config['framerate'])
        self.camera.rotation = self.config['rotation']
        self.logger.info("PiCamera rotation: "+self.confg['rotation'])

        self.camera.start_preview()
        time.sleep(2)


    def ClientStart(self):
        try:
            self.client_socket = socket.socket()
            self.client_socket.connect_ex((self.config['server_ip'],self.config['server_port']))
            self.connection = self.client_socket.makefile("wb")
            self.logger.info("Connected to "+self.config['server_ip']+":"+self.config['server_port']+'.')
        except BaseException as err:
            self.logger.error(err)
            self.ClientStart()

    def ClientClose(self):
        self.connection.close()
        self.client_socket.close()
        self.logger.info("Connection closed.")

    def ReadConfig(self):
        self.script_path = os.path.realpath(__path__)
        self.dir_path = os.path.dirname(self.script_path)
        try:
            with open(self.dir_path+"/client.json", "r") as f:
                self.config = json.load(f)
        except IOError as err:
            self.logger.critical(err)
            exit()
        self.logger.info("Configuration loaded.")

    def Recording(self):
        self.camera.start_recording(self.connection, format='h264', quality=self.config['quality'])
        self.camera.wait_recording(self.config['wait_recording'])
        self.stop_recording()

