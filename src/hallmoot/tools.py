import os

def list_files(directory="."):
    """
    Lists files in the specified directory.

    Args:
        directory (str): The directory to list files from. Defaults to the current directory.

    Returns:
        list: A list of filenames in the directory.
    """
    try:
        import json
        return json.dumps(os.listdir(directory))
    except Exception as e:
        return f"Error: {e}"

def read_file(filepath):
    """
    Reads the content of a file.

    Args:
        filepath (str): The path to the file to read.

    Returns:
        str: The content of the file.
    """
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error: {e}"

def write_file(filepath, content):
    """
    Writes content to a file.

    Args:
        filepath (str): The path to the file to write to.
        content (str): The content to write to the file.

    Returns:
        str: A success message or an error message.
    """
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        return "File written successfully."
    except Exception as e:
        return f"Error: {e}"

def rm_file(filepath):
    """
    Removes a file.

    Args:
        filepath (str): The path to the file to remove.

    Returns:
        str: A success message or an error message.
    """
    try:
        os.remove(filepath)
        return "File removed successfully."
    except Exception as e:
        return f"Error: {e}"
