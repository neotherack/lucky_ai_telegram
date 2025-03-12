import json
import logging
from dotenv import load_dotenv
from ollama import Client
import os
from os.path import abspath

# Configure basic logging
logging.basicConfig(
    format='%(levelname)s: %(name)s %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def save_user_preferences(filename, text):
    """Creates or overwrites a file in the disk server, you can save any file.
    Consider adding the proper extension to the file.
    Do not set any path, just filename.

    Args:
        filename (str): Name of file to create/overwrite. Include extension.
        text (str): Content to write to the file. UTF-8 encoded.

    Returns:
        str: Success or error message
    """
    logger.info(f"Written to {filename}")
    try:
        with open(f"drafts/{filename}", "w") as f:
            f.write(text)

        return "Success, data written to {filename}"

    except Exception as e:
        logger.error(f"Cannot write to {filename}!\n{str(e)}")
        return "Error, cannot write to {filename}"


def read_file(filename):
    """Retrieves file contents from disk server, useful to retrieve any previously saved file.
    Do not set any path, just the filename.

    Args:
        filename (str): Name of file to read from drafts folder. Include extension.

    Returns:
        str: File contents as string if successful, error message if file doesn't
        exist or can't be read.
    """
    logger.info(f"Read from {filename}")
    try:
        f = open(f"drafts/{filename}","r")
        return f.read()
    except Exception as e:
        logger.error(f"Cannot read from {filename}!\n{str(e)}")
        return f"Error, cannot read from {filename}"