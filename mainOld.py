from aiohttp import web
import socketio
import ssl
import astroCalcs
import asyncio

# create a Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins="https://192.168.1.77:80",logger=True, engineio_logger=True)
app = web.Application()
sio.attach(app)
i = 0
abort = False


async def index(request):
    with open("index.html") as f:
        return web.Response(text=f.read(), content_type="text/html")






@sio.event
def connect(sid, environ):
    print("Socket client connected: ", sid)

@sio.event
def disconnect(sid):
    print("Socket client disconnected: ", sid)

@sio.on('orientation')
def another_event(sid, data):
    print(data)

@sio.on('userInput')
def another_event(sid, data):
    global exposure
    dataPairs = data["userInput"].split("&")
    target = dataPairs[0].split("=")[1]
    exposureT = dataPairs[1].split("=")[1]
    loc = dataPairs[2].split("=")[1]
    exposure = astroCalcs.CalcMovement(target, exposureT, loc)
    # print(data)


# @sio.on("abort")
# def abort(sid, data):
#     abort = True
#     abort = False


@sio.on('dataRequest')
async def another_event(sid, data):
    ExposureComplete = False
    while not ExposureComplete:
        deltaData, ExposureComplete = exposure.track()
        await sio.emit("DataUpdate", deltaData, room=sid)
    await sio.emit("ExposureComplete", {}, room=sid)








app.router.add_get('/', index)
app.router.add_static('/static', 'static')
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('cert.pem', 'key.pem')


if __name__ == '__main__':
    web.run_app(app, port=80, ssl_context=ssl_context)
