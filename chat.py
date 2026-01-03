"""
Hallmoot Chat CLI

Usage:
  chat.py [--url=<url>] [--channels=<channels>] [--file=<file>]
  chat.py -h | --help

Options:
  -h --help         Show this screen.
  --url=<url>       WebSocket server URL [default: ws://localhost:9090/ws].
  --channels=<ch>   Comma-separated channels to subscribe to [default: llm].
  --file=<file>     Conversation file for hallmoot [default: convos/chat.yml].
"""

import sys
import docopt
import time
from websocket import create_connection

class ChatClient:
    def __init__(self, url, channels, convo_file):
        self.url = f"{url}?channels={channels}"
        self.ws = create_connection(self.url)
        self.convo_file = convo_file
        print(f"Connected to {self.url}")
        print("Type messages. Ctrl+C to exit.")

    def send(self, message):
        self.ws.send("llm")
        self.ws.send(message)

    def recv(self):
        try:
            channel = self.ws.recv()
            payload = self.ws.recv()
            return channel, payload
        except Exception:
            return None, None

    def run(self):
        try:
            while True:
                # User input
                try:
                    user_input = input("you> ")
                except EOFError:
                    break
                if not user_input:
                    continue
                if user_input.strip() in ('/q', '/quit', '/exit'):
                    break
                # Send to server
                self.send(user_input)
                # Receive responses (streaming)
                while True:
                    channel, payload = self.recv()
                    if channel is None:
                        break
                    if channel == 'llm':
                        print(f"bot> {payload}", end='', flush=True)
                    else:
                        print(f"[{channel}] {payload}")
                print()  # Newline after response
        except KeyboardInterrupt:
            pass
        finally:
            self.ws.close()
            print("\nBye!")

def main():
    args = docopt.docopt(__doc__)
    url = args['--url']
    channels = args['--channels']
    convo_file = args['--file']
    client = ChatClient(url, channels, convo_file)
    client.run()

if __name__ == '__main__':
    main()