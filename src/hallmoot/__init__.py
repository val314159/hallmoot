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
    def _persist_message(self, message) -> None:
        import yaml
        with open(self.filename, 'a') as f:
            f.write('---\n')
            yaml.dump(message, f)
        pass
    def user_input(self) -> None:
        while 1:
            if ret := input('user> '):
                if ret.startswith('/m'):
                    print(self.messages)
                    continue
                message = {'role': 'user', 'content': ret}
                self.messages.append(message)
                self._persist_message(message)
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
            message = {'role': 'assistant', 'content': '\n'.join(contents)}
            self.messages.append(message)
            self._persist_message(message)
            return False
        else:
            message = {'role': 'assistant', 'content': '\n'.join(contents), 'tool_calls': [{'function': {'name': tc.function.name, 'arguments': tc.function.arguments}} for tc in tool_calls]}
            self.messages.append(message)
            self._persist_message(message)
            for tc in tool_calls:
                name, arguments = tc.function.name, tc.function.arguments
                tool = self.tools.get(name, None)
                if tool is None:
                    tool_msg = {'role': 'tool', 'content': f'Unknown tool: {name}'}
                    self.messages.append(tool_msg)
                    self._persist_message(tool_msg)
                    continue
                print("GOT TOOL", tool)
                results = tool(**arguments)
                print("GOT RESULT", type(results), results)
                tool_msg = {'role': 'tool', 'name': name, 'content': results}
                self.messages.append(tool_msg)
                self._persist_message(tool_msg)
            return True
        pass
    pass


def main():
    convo = hallmoot('convos/u.yml')
    while 1:
        convo.user_input()
        while convo.user_round():
            pass
        pass
    pass


if __name__ == '__main__': main()

