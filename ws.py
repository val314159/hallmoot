#!/usr/bin/env python3
from gevent import monkey as _;_.patch_all()
import bottle
from geventwebsocket import WebSocketServer
from collections import UserDict

def hexid(ws):
    return hex(id(ws))[2:]

class pubsub(UserDict):
    def __init__(self):
        self.data = {}
    def sub(self, ws, channels):
        for channel in channels:
            if channel not in self.data:
                self.data[channel] = list()
            self.data[channel].append(ws)
    def unsub(self, ws, channels):
        for channel in channels:
            if channel in self.data:
                self.data[channel].remove(ws)
                if not self.data[channel]:
                    del self.data[channel]
    def pub(self, channel, message, ws_in=None):
        if channel in self.data:
            for ws in self.data[channel]:
                if ws is not ws_in:
                    ws.send(channel)
                    ws.send(message)

app = bottle.Bottle()
app.ps = pubsub()

@app.get('/ws')
def websocket():
    ws = bottle.request.environ.get('wsgi.websocket')
    if not ws:
        raise bottle.abort(400)
    wsid = hex(id(ws))[2:]
    channels = bottle.request.query.channels or ''
    channels = [c.strip() for c in channels.split(',') if c.strip()]
    channels.append(wsid)
    print("CHANNELS", channels)
    try:
        app.ps.sub(ws, channels)
        while True:
            print("RECV")
            if not (c := ws.receive()):
                print("BREAK1")
                break
            print("CHANNEL", c)
            if not (p := ws.receive()):
                print("BREAK2")
                break
            print("MESSAGE", p)
            if c=='hello':
                print("HELLO")
                ws.send("welcome")
                import json
                s = json.dumps({"id":wsid})
                print((33,s))
                ws.send(s)
            else:
                app.ps.pub(c, p, ws_in=ws)
    except Exception as e:
        print("ERROR", e)
    finally:
        app.ps.unsub(ws, channels)

@app.get('/')
@app.get('/<path>')
def index(path="index.html"):
    return bottle.static_file(path, root="./static")

if __name__ == '__main__':
    WebSocketServer(('0.0.0.0', 9090), app).serve_forever()