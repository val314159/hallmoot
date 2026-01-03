'''
Usage: hallmoot <filename>
'''

# -- tools -- #
import os

SANDBOX = 'sandbox'
os.makedirs(SANDBOX, exist_ok=True)

def _sanitize_path(path):
    # Resolve absolute path and ensure it's within sandbox
    abs_path = os.path.abspath(os.path.join(SANDBOX, path))
    if not abs_path.startswith(os.path.abspath(SANDBOX)):
        raise ValueError("Path outside sandbox")
    return abs_path

def list_files(directory=".", recursive=False, details=False):
    """
    Lists files in the specified directory within the sandbox.

    Args:
        directory (str): The directory to list files from. Defaults to the current directory.
        recursive (bool): Whether to list files recursively. Defaults to False.
        details (bool): Whether to include file details (size, mtime). Defaults to False.

    Returns:
        str: JSON string of file list or details.
    """
    try:
        safe_dir = _sanitize_path(directory)
        import json
        if recursive:
            result = []
            for root, dirs, files in os.walk(safe_dir):
                for name in files + dirs:
                    full_path = os.path.join(root, name)
                    rel_path = os.path.relpath(full_path, SANDBOX)
                    if details:
                        stat = os.stat(full_path)
                        result.append({'path': rel_path, 'size': stat.st_size, 'mtime': stat.st_mtime})
                    else:
                        result.append(rel_path)
            return json.dumps(result)
        else:
            items = os.listdir(safe_dir)
            if details:
                result = []
                for name in items:
                    full_path = os.path.join(safe_dir, name)
                    stat = os.stat(full_path)
                    result.append({'path': name, 'size': stat.st_size, 'mtime': stat.st_mtime})
                return json.dumps(result)
            else:
                return json.dumps(items)
    except Exception as e:
        return f"Error: {e}"

def read_file(filepath, start=None, end=None):
    """
    Reads the content of a file within the sandbox.

    Args:
        filepath (str): The path to the file to read.
        start (int, optional): Byte offset to start reading.
        end (int, optional): Byte offset to end reading.

    Returns:
        str: The content of the file or a slice.
    """
    try:
        safe_path = _sanitize_path(filepath)
        with open(safe_path, 'r') as file:
            if start is not None or end is not None:
                file.seek(start or 0)
                return file.read((end or file.size()) - (start or 0))
            return file.read()
    except Exception as e:
        return f"Error: {e}"

def write_file(filepath, content, append=False):
    """
    Writes content to a file within the sandbox.

    Args:
        filepath (str): The path to the file to write to.
        content (str): The content to write to the file.
        append (bool): Whether to append to the file. Defaults to False.

    Returns:
        str: A success message or an error message.
    """
    try:
        safe_path = _sanitize_path(filepath)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        mode = 'a' if append else 'w'
        with open(safe_path, mode) as file:
            file.write(content)
        return "File written successfully."
    except Exception as e:
        return f"Error: {e}"

def mkdir(path):
    """
    Creates a directory within the sandbox.

    Args:
        path (str): The directory path to create.

    Returns:
        str: A success message or an error message.
    """
    try:
        safe_path = _sanitize_path(path)
        os.makedirs(safe_path, exist_ok=True)
        return "Directory created successfully."
    except Exception as e:
        return f"Error: {e}"

def rm_file(filepath):
    """
    Removes a file within the sandbox.

    Args:
        filepath (str): The path to the file to remove.

    Returns:
        str: A success message or an error message.
    """
    try:
        safe_path = _sanitize_path(filepath)
        os.remove(safe_path)
        return "File removed successfully."
    except Exception as e:
        return f"Error: {e}"

def run_make(target='all', directory=None):
    """
    Runs make in the sandbox or a subdirectory within it.

    Args:
        target (str): The make target to run. Defaults to 'all'.
        directory (str, optional): Subdirectory within sandbox to run make in.

    Returns:
        str: The output of make or an error message.
    """
    try:
        import subprocess
        cwd = _sanitize_path(directory) if directory else SANDBOX
        result = subprocess.run(['make', '-C', cwd, target], capture_output=True, text=True)
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

            
# -- main -- #

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
        # Load base config
        with open(self.filename, 'r') as f:
            config = yaml.safe_load(f)
        if not config:
            raise ValueError("Invalid convo file")
        # Handle branching
        if 'branch' in config and 'length' in config:
            branch_file = config['branch']
            max_bytes = config['length']
            with open(branch_file, 'r') as f:
                chunk = f.read(max_bytes)
            messages = list(yaml.safe_load_all(chunk))
        elif 'branch' in config and 'length' not in config:
            raise ValueError("Branch file specified but no length")
        elif 'branch' not in config and 'length' in config:
            raise ValueError("Length specified but no branch file")
        else:
            # Normal load
            with open(self.filename) as f:
                messages = list(yaml.safe_load_all(f))
                pass
            pass
        self.convo = messages.pop(0)
        self.convo['messages'] = messages
        pass
    def _load_tools(self) -> None:
        if toolkit := self.convo.get('tools', None):
            from importlib import import_module
            mod = import_module(toolkit, __package__)
            self.tools = dict((k, v) for k, v in vars(mod).items() if callable(v))
        else:
            self.tools = {
                'list_files': list_files,
                'read_file': read_file,
                'write_file': write_file,
                'mkdir': mkdir,
                'rm_file': rm_file,
                'run_make': run_make,
            }
            pass
        self.convo['tools'] = list(self.tools.values())
    def _persist_message(self, message) -> None:
        import yaml
        with open(self.filename, 'a') as f:
            f.write('---\n')
            yaml.dump(message, f)
        pass
    def user_input(self) -> None:
        while 1:
            if ret := input('user> '):
                if ret.startswith('/q'):
                    print('>> Bye!')
                    raise SystemExit
                if ret.startswith('/m'):
                    print(self.messages)
                    continue
                message = {'role': 'user', 'content': ret}
                self.messages.append(message)
                self._persist_message(message)
                return
            pass
        pass
    def run_tool(self, tool_name, tool_args) -> None:
        if tool := self.tools.get(tool_name, None):
            try:
                return tool(**tool_args)
            except Exception as e:
                return f"Error: {e}"
        else:
            return f"Error: Unknown tool {tool_name}"
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
                results = self.run_tool(tc.function.name, tc.function.arguments)
                tool_msg = {'role': 'tool', 'name': tc.function.name, 'content': results}
                self.messages.append(tool_msg)
                self._persist_message(tool_msg)
                pass
            return True
        pass
    pass


def main():
    import sys
    try:
        filename = sys.argv[1]
    except:
        filename = 'convos/u.yml'        
    convo = hallmoot(filename)
    while 1:
        convo.user_input()
        while convo.user_round():
            pass
        pass
    pass


if __name__ == '__main__': main()

