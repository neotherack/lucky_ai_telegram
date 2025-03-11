import os
import json
import uuid
import logging
import requests
from typing import List, Optional, Union
from bs4 import BeautifulSoup

from dotenv import load_dotenv

# Configure basic logging
logging.basicConfig(
    format='%(levelname)s: %(name)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def remove_empty_lines(text):
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip() != '']
    return str('\n'.join(non_empty_lines))

def toolcall_to_json(tool):
    id_ = str(uuid.uuid4())
    name = tool.function.name
    args = tool.function.arguments
    return {"id":id_ , "type":"function", "function":{"name":name,"arguments":args}}

def list_local_dir(directory) -> str:
    """
    This tool will return a local disk directory listing, it's useful to check existing files in local disk.
    You have to pick one of the allowed folders: drafts, plots or data.

    Args:
        directory (str): pick of these "drafts","plots","data".

    Returns:
        str: a text string containing all file names

    Example:
        list_local_dir("drafts") -> file listing in string format from the drafts dir
    """
    return str(os.listdir())

def browse_website(url: str, mode: str)->str:
    """
    This function allows to get any webpage on the internet at any time, to function will trigger an HTTP GET to the URL in the paramter.
    "human" mode will get the text of the website in markdown format
    "links" mode is the best approach to explore a website first
    For exploration or browsing purporses use a multi-step strategy use first the "links" method call and then call again several times using "human" mode.
    If you need to search for something you can start here 'https://es.wikipedia.org/w/index.php?search=<search_term>' (<search_term> is your place holder)

    Args:
      url(string): The URL get data from, any valid URL will work.
      mode(string): Valid modes: "html", "markdown", "links".
        - "human" which will get only the text parts in markdown (MD) format
        - "links" which will return all links within the website, this method is suitable while exploring websites

    Returns:
      str: [http status code] the http body if the web site requested, html if "html" mode is selected or markdown if "markdown" mode.

    Example:
       browse_website("https://www.opentext.com/contact/", "human") -> [404] failed attempt to extract text from website
    """
    response = requests.get(url)
    status = response.status_code

    if mode=="html":
        ret_data = f"[{status}] {str(response.__dict__)}"
    if mode=="human":
        soup = BeautifulSoup(response.text, 'html.parser')
        #markdown_converter = mistune.Markdown()
        #return f"[{status}] {markdown_converter(soup.get_text())}"
        ret_data = f"[{status}] {soup.get_text()}"
    if mode=="links":
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        links = sorted(list(set(links)))
        ret_data = f"[{status}] {', '.join(links)}"

    return remove_empty_lines(ret_data)

def get_weather_forecast(city_name: str, mode: str) -> str:
  """
  Get weather forecast for a given city or location, all data comes from api.openweathermap.org API public endpoints.
  "simple" report will include just basic forecast information.
  "detailed" extensive forecast details, use "dt" for plotting charts but you have to convert it from unix time to human readable.

  Args:
  city_name (string): the name of the city or location to get weather forecast from
  mode (string): it can be "simple" to get highs and lows basic info, or "detailed" to get a full hourly json dump.

  Returns:
    str: the weather forecast for the location in JSON format, you should translate to a very detailed human readable text. All units will be in international system
  """
  load_dotenv()
  WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

  geo_url=f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={WEATHER_API_KEY}"
  response_geo = requests.get(geo_url)

  lon = response_geo.json()[0]["lon"]
  lat = response_geo.json()[0]["lat"]
  query = f"lon={lon}&lat={lat}&appid={WEATHER_API_KEY}&units=metric&cnt=8"

  if mode=="simple":
     weather_url=f"https://api.openweathermap.org/data/2.5/weather?{query}"
  else:
     weather_url=f"https://api.openweathermap.org/data/2.5/forecast?{query}"

  response_weather = requests.get(weather_url)
  return str(response_weather.json())

def get_current_time() -> str:
  """
  Returns today's date and time for Madrid (Spain) timezone

  Returns:
    str: current date and time, translate to a human friendly format
  """
  from datetime import datetime
  return str(datetime.now())


def write_file(filename, text):
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


def get_tools():
  tools = [
    list_local_dir,
    get_weather_forecast,
    get_current_time,
    browse_website,
    write_file,
    read_file
  ]

  available_functions = {
    'list_local_dir': list_local_dir,
    'get_weather_forecast': get_weather_forecast,
    'get_current_time': get_current_time,
    'browse_website': browse_website,
    'write_file': write_file,
    'read_file': read_file
  }
  return tools, available_functions
