import os
import json
import uuid
import logging
import requests
import matplotlib.pyplot as plt
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

def list_local_dir() -> str:
    """
    This tool will return a local disk directory listing, it's useful to check existing files in local disk.
    You can use it anytime.

    Args: No args needed, it will always list the local directory

    Returns:
        str: a text string containing all file names from the local directory

    Example:
        list_local_dir() -> file listing from the local directory
    """
    return str(os.listdir())

def plot_chart(x_data: Union[List[float], List[List[float]]],
               y_data: Union[List[float], List[List[float]]],
               chart_type: str = 'line',
               title: str = 'Chart',
               x_label: str = 'X Axis',
               y_label: str = 'Y Axis',
               color: Union[str, List[str]] = 'blue',
               filename: str = 'plot.png') -> str:
    """
    Generates and saves various types of charts using Matplotlib. 
    Supports one single line if you set x_data or y_data as a List[Float]
    Supports multiple lines if you set x_data or y_data as List[List[Float]]
    The plot is saved to a file and returns the filename.

    Args:
        x_data (Union[List[float], List[List[float]]]): X-axis data. If a single list is provided,
            it is used for all lines. If a list of lists, each sublist is X-data for a corresponding line.
        y_data (Union[List[float], List[List[float]]]): Y-axis data. Each sublist represents a line's Y-data.
            If a single list, it is treated as a single line.
        chart_type (str): Type of chart (line/bar/scatter). Default: line
        title (str): Chart title. Default: 'Chart'
        x_label (str): X-axis label. Default: 'X Axis'
        y_label (str): Y-axis label. Default: 'Y Axis'
        color (Union[str, List[str]]): Color for each line. Default: blue
        filename (str): Output filename. Default: plot.png

    Returns:
        str: Path to the generated chart image file

    Example:
        plot_chart([1,2,3], [[4,5,6], [7,8,9]], 'line', 'Sales', 'Months', 'Revenue', ['red', 'blue'], 'plot.png')
    """
    # Process y_data into a list of lists
    if not y_data:
        raise ValueError("y_data must not be empty")
    if not isinstance(y_data[0], (list, tuple)):
        y_data = [y_data]

    num_lines = len(y_data)

    # Process x_data into a list of lists
    if not x_data:
        raise ValueError("x_data must not be empty")
    if isinstance(x_data[0], (list, tuple)):
        if len(x_data) != num_lines:
            raise ValueError("x_data must have the same number of lines as y_data when provided as a list of lists")
        x_data_list = x_data
    else:
        x_data_list = [x_data] * num_lines

    # Check lengths of each x and y line
    for i, (x_line, y_line) in enumerate(zip(x_data_list, y_data)):
        if len(x_line) != len(y_line):
            raise ValueError(f"Line {i}: x_data and y_data lengths must match. Found {len(x_line)} vs {len(y_line)}")

    # Process color into a list
    if isinstance(color, list):
        if len(color) != num_lines:
            raise ValueError("Number of colors must match the number of lines")
        colors = color
    else:
        colors = [color] * num_lines

    plt.figure()

    chart_type = chart_type.lower()
    for x_line, y_line, c in zip(x_data_list, y_data, colors):
        if chart_type == 'line':
            plt.plot(x_line, y_line, color=c)
        elif chart_type == 'bar':
            plt.bar(x_line, y_line, color=c)
        elif chart_type == 'scatter':
            plt.scatter(x_line, y_line, color=c)
        else:
            plt.close()
            raise ValueError(f"Unsupported chart type: {chart_type}. Use line/bar/scatter")

    plt.title(title)
    #plt.xlabel(x_label)
    plt.xlabel(x_label, rotation='vertical')
    plt.ylabel(y_label)
    plt.grid(True)

    ## EN PRUEBAS!!!
    #plt.set_xlabel(plt.get_xlabel())

    plt.savefig(filename)
    plt.close()

    return f"Chart saved as {filename}"

def do_math_operations(a:int, op:str, b:int)->str:
    """
    Do basic math operations

    Args:
    a(integer): The first operand
    op(string): The operation to perform, one of '+' (sum, addition), '-' (minus, difference), '*' (times,multiplication), '/' (division)
    b(integer): The second operand

    Returns:
      str: the result of the math operation requested

    Example:
        do_math("3", "*", "2") -> 6
        do_math("10", "-", "7") -> 3
    """
    res = "NaN"
    if op == "+":
        res = str(int(a) + int(b))
    elif op == "-":
        res = str(int(a) - int(b))
    elif op == "*":
        res = str(int(a) * int(b))
    elif op == "/":
        if int(b) != 0:
            res = str(int(a) / int(b))
    return res

def browse_website(url: str, mode: str)->str:
    """
    This function allows to get any webpage on the internet at any time, to function will trigger an HTTP GET to the URL in the paramter.
    "html" is computationally expensive and slow, only for website debugging.
    "human" mode will get the text of the website in markdown format
    "links" mode is the best approach to explore a website first
    For exploration or browsing purporses use a multi-step strategy use first the "links" method call and then call again several times using "human" mode.
    If you need to search for something you can start here 'https://es.wikipedia.org/w/index.php?search=<search_term>' (<search_term> is your place holder)
    Do not request the same website more than one time per iteration, it makes no sense.

    Args:
      url(string): The URL get data from, any valid URL will work.
      mode(string): Valid modes: "html", "markdown", "links".
        - "html" to just get full HTML site, only for debug HTML code analysis
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


def toolcall_to_json(tool):
    id_ = str(uuid.uuid4())
    name = tool.function.name
    args = tool.function.arguments
    return {"id":id_ , "type":"function", "function":{"name":name,"arguments":args}}


def get_tools():
  tools = [
    do_math_operations,
    get_weather_forecast,
    get_current_time,
    browse_website,
    plot_chart
  ]

  available_functions = {
    'do_math_operations': do_math_operations,
    'get_weather_forecast': get_weather_forecast,
    'get_current_time': get_current_time,
    'browse_website': browse_website,
    'plot_chart': plot_chart,
  }
  return tools, available_functions
