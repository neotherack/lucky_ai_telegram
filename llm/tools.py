import os
import json
import uuid
import psycopg2
import logging
import requests
from typing import List, Optional, Union
from bs4 import BeautifulSoup

from .dbconfig import DB_CONFIG
from dotenv import load_dotenv

# Configure basic logging
logging.basicConfig(
    format='%(levelname)s: %(name)s %(message)s',
    level=logging.DEBUG
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

def connect_to_db():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None

def search_series_by_name(name:str):
    """
    It will return a series listing based on the name filter provided

    Args:
    - name (str): series name part like "naruto" "dragon" or "hanako"

    Returns:
    - str: markdown table id, name, type and status.
           id is the series id.
           name is the series title
           type can be 'Anime' for japanese series, 'Donghua' for chinese series
           status 'Yes' if it's fully downloaded, 'No' if it's not yet read
    """
    response = "|ID|Title|Type|Downloaded|\n|----|----|----|\n"
    conn = connect_to_db()
    with conn.cursor() as cur:
        query = f"SELECT id, name, type, status FROM anime_downloader_anime WHERE name ILIKE '%{name}%'"
        logger.debug(query)
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            #logger.debug(row)
            id=row[0]
            name=row[1]
            type="Anime" if row[2]=="JP" else "Donghua"
            status="Yes" if row[3]=="CMP" else "No"
            response += f"|{id}|{name}|{type}|{status}|\n"

        if len(rows)==0:
         response=f"We could not find any name like '{name}', try another name."

        return response

def get_series_details(series_id):
    """
    Retrieves details of a specific series from the database based on its ID.
    Use 'search_series_by_name' tool first to get the ID.

    Args:
    - series_id (int): The unique identifier of the series to retrieve.

    Returns:
    - str: A string containing the details of the specified series.

    If the series is not found, returns an error message indicating that the ID was not found.
    """
    conn = connect_to_db()
    with conn.cursor() as cur:
        query = f"SELECT id,name,genres,viewed as watched,other_names,status as downloaded,synopsis "+\
                 "FROM anime_downloader_anime WHERE id={series_id}"
        logger.debug(query)
        cur.execute(query)
        row = cur.fetchone()
        if not row:
            logger.error(f"Series id={series_id} not found")
            return f"Series id={series_id} not found"
        else:
            logger.info(f"Anime id={series_id} found")
            return json.loads(json.dumps(row))

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
    search_series_by_name,
    get_series_details,
    list_local_dir,
    get_weather_forecast,
    get_current_time,
    browse_website,
    write_file,
    read_file
  ]

  available_functions = {
    'search_series_by_name': search_series_by_name,
    'get_series_details': get_series_details,
    'list_local_dir': list_local_dir,
    'get_weather_forecast': get_weather_forecast,
    'get_current_time': get_current_time,
    'browse_website': browse_website,
    'write_file': write_file,
    'read_file': read_file
  }
  return tools, available_functions
