'''
Usage: hallmoot <filename>
'''


__version__ = '1.0.1'

class hallmoot:
    def __init__(self, filename) -> None:
        self.filename = filename
        self._load_convo()
        self._load_tools()
        pass
    def display_user(self, text) -> None:
        import sys
        return sys.stderr.write(text)
    @property
    def messages(self) -> list:
        return self.convo['messages']
    def _load_convo(self) -> None:
        import yaml
        messages = list(yaml.safe_load_all(open(self.filename)))
        self.convo = messages.pop(0)
        self.convo['messages'] = messages
        pass
    def _load_tools(self) -> None:
        if toolkit := self.convo.get('tools', None):
            from importlib import import_module
            mod = import_module(toolkit, __package__)
            self.tools = dict((k, v) for k, v in vars(mod).items() if callable(v))
            self.convo['tools'] = list(self.tools.values())
        else:
            self.tools = self.convo['tools'] = None
        pass
    def user_input(self) -> None:
        while 1:
            if ret := input('user> '):
                self.messages.append({'role': 'user', 'content': ret})
                return
            pass
        pass
    def user_round(self) -> bool:
        import ollama
        contents, tool_calls = [], []
        for response in ollama.chat(**self.convo, stream=True):
            message = response.message
            if message.content:
                if not contents:
                    self.display_user("asst> ")
                    pass
                contents.append(message.content)
                self.display_user(message.content)
                pass
            for tool_call in message.tool_calls or []:
                tool_calls.append(tool_call)
                pass
            pass
        else:
            self.display_user('<<\n')
            pass
        if not tool_calls:
            self.messages.append({'role': 'assistant', 'content': '\n'.join(contents)})
            return False
        else:
            self.messages.append({'role': 'assistant', 'content': '\n'.join(contents),
                'tool_calls': tool_calls})
            for tc in tool_calls:
                name, arguments = tc.function.name, tc.function.arguments
                tool = self.tools.get(name, None)
                if tool is None:
                    self.messages.append({'role': 'tool', 'content': f'Unknown tool: {name}'})
                    continue
                print("GOT TOOL", tool)
                results = tool(**arguments)
                print("GOT RESULT", type(results), results)
                self.messages.append({'role': 'tool', 'name': name, 'content': results})
            return True
        pass
    pass


def main():
    convo = hallmoot('convos/u.yml')
    while 1:
        print("!")
        convo.user_input()
        print("DF")
        while convo.user_round():
            print("QEQWER")
            pass
        pass
    pass


if __name__ == '__main__': main()

