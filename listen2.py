import socket
import cv2
import time
import numpy as np
from AlphaBot2 import AlphaBot
from picamera import PiCamera
from bottle import Bottle, get, run, request

app = Bottle()

def setup_app(app):
    app.bot = AlphaBot()
    app.camera = PiCamera()
    app.camera.resolution = (640,480)
    app.camera.framerate = 24
    app.camera.start_preview()
    time.sleep(2)
        
setup_app(app)

@app.get("/camera/get")
def get_image():
    width, height = app.camera.resolution
    image = np.empty((height * width * 3,), dtype=np.uint8)
    app.camera.capture(image, 'bgr', use_video_port=True)
    image = image.reshape((height, width, 3))
    return cv2.imencode('.jpg', image)[1].tobytes()
    
@app.get('/robot/set/velocity')
def set_velocity():
    vel = request.query.value.split(',')
    app.bot.setMotor(float(vel[0]), float(vel[1]))
    if request.query.time != '':
        time_run = float(request.query.time)
        start_time = time.time()
        duration = 0
        while duration < time_run:
            duration = time.time() - start_time
            if get_ir() == 1:
                app.bot.setMotor(-1, 0)
                time.sleep(5)
                break
        # time.sleep(time_run)
        app.bot.stop()

@app.get('/ir_sensor')
def get_ir():
    if (app.bot.get_IR() == 1):
        return 1
    else:
        return 0
    

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('8.8.8.8',80))
localhost=s.getsockname()[0]
run(app, host=localhost, port=8000)
