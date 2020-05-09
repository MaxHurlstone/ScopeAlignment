from aiohttp import web
import socketio
import ssl
import asyncio

import numpy as np

import queue
import threading

import plotting

global sio
global app
sio = socketio.AsyncServer(cors_allowed_origins="https://192.168.1.77:80") # engineio_logger=True)
app = web.Application()
sio.attach(app)

async def index(request):
    with open("index.html") as f:
        return web.Response(text=f.read(), content_type="text/html")

app.router.add_get('/', index)
app.router.add_static('/static', 'static')
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('cert.pem', 'key.pem')


@sio.event
def connect(sid, environ):
    # queueHolder.gyroConnected = True
    print("Socket client connected: ", sid)

@sio.event
def disconnect(sid):
    # queueHolder.gyroConnected = False
    print("Socket client disconnected: ", sid)

@sio.on('OrientationData')
def HandleData(sid, data):
    # print("Hello?")
    # print(data)
    lastdata =  [data["a"], data["b"]] #np.recarray((data[0],data[1]))
    queueHolder.oQ.put(lastdata)

@sio.on('MotionData')
def HandleData(sid, data):
    # print("Hello?")
    # print(data)
    lastdata =  [data["x"], data["y"], data["z"], data["gx"], data["gy"], data["gz"]] #np.recarray((data[0],data[1]))
    queueHolder.aQ.put(lastdata)


class QueueHolder():
    def __init__(self, oQ, aQ):
        self.oQ = oQ
        self.aQ = aQ
        self.gyroConnected = False

class Server(threading.Thread):
    def __init__(self, app, ssl_context, port):
        super(Server, self).__init__()
        self.app = app
        self.ssl_context = ssl_context
        self.port = port

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        web.run_app(self.app, port=self.port, ssl_context=self.ssl_context, handle_signals=False)


if __name__ == '__main__':

    # Initialise the queue where data will be stored
    oQueue = queue.Queue()
    aQueue = queue.Queue()
    global queueHolder
    queueHolder = QueueHolder(oQueue, aQueue)

    gyroscope = Server(app, ssl_context, 80)
    # gyroscope.run()

    gyroscope.daemon = True
    print("Starting Thread... .")
    gyroscope.start()

    # Initialise plotter classs
    observation = plotting.PyQtPlotter(oQueue, aQueue)
    #Test(dataqueue) or PyQtPlotter(dataqueue)
