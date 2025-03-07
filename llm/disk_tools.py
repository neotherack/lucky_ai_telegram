import json
import logging

# Configure basic logging
logging.basicConfig(
    format='%(name)s -%(levelname)s- %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def write_file(filename, text):
    """Creates or overwrites a file in the drafts subdirectory. Use this for safely
    storing generated content before final approval. All files are saved in a
    dedicated folder to prevent accidental overwrites of production files.

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
    """Retrieves file contents from the drafts subdirectory. Use this to access
    previously saved files or to verify written content.

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


def get_disk_tools():
  tools = [
    read_file,
    write_file
  ]

  available_functions = {
    'read_file': read_file,
    'write_file': write_file,
  }
  return tools, available_functions
