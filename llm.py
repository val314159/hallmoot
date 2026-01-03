#!/usr/bin/env python3
from gevent import monkey as _;_.patch_all()
from websocket import create_connection
import sys
sys.path.append('.')
from hallmoot import hallmoot

class WS:
    URL = "ws://localhost:9090/ws?channels=llm,one,two,hello"
    CH = 'llm'
    def __init__(self, url=URL):
        self.url = url
        self.ws = create_connection(url)
        self.hm = hallmoot('convos/llm.yml')
        # Override display_user to stream over WebSocket
        self.hm.display_user = self.stream_output
    def pub(self, message, channel=CH):
        self.ws.send(channel)
        self.ws.send(message)
        return
    def recv2(self):
        c = self.ws.recv()
        p = self.ws.recv()
        return c,p
    def close(self):
        return self.ws.close()
    def stream_output(self, text):
        # Stream assistant output over WebSocket
        self.pub(text, channel='llm')
    def handle_llm(self, payload):
        # Append user message and run a round
        message = {'role': 'user', 'content': payload}
        self.hm.messages.append(message)
        self.hm._persist_message(message)
        # Run round (streaming via overridden display_user)
        more = True
        while more:
            more = self.hm.user_round()
        # No need to return content; it's streamed
    pass

ws = WS()
ws.pub("zone", "hello")
while True:
    channel, payload = ws.recv2()
    print(211,channel,payload)
    if channel=='llm':
        ws.handle_llm(payload)
    pass
ws.close()
