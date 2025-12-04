import os
import json
import uuid
import logging
import requests
from trafilatura import fetch_url, extract
from duckduckgo_search import DDGS

#from .dbconfig import DB_CONFIG
#from dotenv import load_dotenv

RESULT_LIMIT = 5
CONTENT_LEN_CUT = 10000

# Configure basic logging
logging.basicConfig(
    format='%(levelname)s: %(name)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def toolcall_to_json(tool):
    id_ = str(uuid.uuid4())
    name = tool.function.name
    args = tool.function.arguments
    return {"id":id_ , "type":"function", "function":{"name":name,"arguments":args}}

def search_internet_tool(keywords: str) -> str:
    """
    This tool will search on the internet by using a search engine.
    You can search for:
    1. current date and time
    2. weather for a given city/location
    3. online tutorials or manuals
    4. technical info
    5. images and videos
    6. any other online content...

    Args:
        keywords: search terms, it will just be sent to the search engine

    Returns:
        str: Result text processed by another LLM model based on the search terms and the 
             info found on the internet
    """

    logger.info(f"Iniciando búsqueda para keywords: {keywords}")

    # 1. Búsqueda con DuckDuckGo
    try:
        logger.debug("Realizando búsqueda en DuckDuckGo")
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(keywords, max_results=RESULT_LIMIT)]

        logger.info(f"Encontrados {len(search_results)} resultados de búsqueda")

    except Exception as e:
        logger.error(f"Error en búsqueda DDG: {str(e)}", exc_info=True)
        return f"Error en la búsqueda: {str(e)}"

    if not search_results:
        logger.warning("No se encontraron resultados de búsqueda")
        return "No se encontraron resultados de búsqueda"

    # 2. Extracción de contenido de los enlaces
    processed_results = []
    logger.debug("Iniciando extracción de contenido")

    for i, result in enumerate(search_results):
        try:
            url = result.get('href', '')
            if not url:
                logger.debug(f"Resultado {i} sin URL válida")
                continue

            logger.info(f"Procesando URL {i}: {url}")

            downloaded = fetch_url(url)
            content = extract(downloaded, include_links=False, include_tables=False)

            if content:
                logger.debug(f"Contenido extraído ({len(content)} caracteres)")
                processed_results.append({
                    'num': i,
                    'url': url,
                    'content': content[:CONTENT_LEN_CUT]
                })
            else:
                logger.warning(f"No se pudo extraer contenido de {url}")

        except Exception as e:
            logger.error(f"Error procesando {url}: {str(e)}", exc_info=True)
            continue

    # 3. Construcción del prompt para Ollama
    logger.debug("Construyendo prompt para Ollama")
    search_context = "\n\n".join(
        [f"Búsqueda {res['num']} ({res['url']}):\n{res['content']}"
         for res in processed_results]
    )

    system_prompt = f"""Eres un asistente de búsqueda experto. El usuario preguntó: '{keywords}'.

    Los resultados de búsqueda son:
    {search_context if search_context else 'No se encontró contenido relevante en los resultados'}

    Responde de forma concisa y útil:
    1. Si la información es relevante y suficiente: Da una respuesta estructurada citando las fuentes o URLs.
    2. Si la información es insuficiente o no relevante: Indícalo claramente y sugiere parámetros de búsqueda más específicos.
    3. Ten en cuenta el orden de los resultados, el primer resultado es el que el motor de búsqueda consideró más relevante.
    """

    logger.debug(f"Longitud del prompt: {len(system_prompt)} caracteres")

    # 4. Llamada a la API de Ollama
    try:
        logger.info("Enviando solicitud a Ollama API")
        response = requests.post(
            'http://antares:11434/api/generate',
            json={
                'model': 'qwen2.5:7b-instruct-q4_0',
                'prompt': f"Términos de la búsqueda: {keywords}",
                'system': system_prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_ctx': 7500
                }
            }
        )
        response.raise_for_status()

        logger.debug("Respuesta recibida de Ollama")
        return json.loads(response.text)['response']

    except Exception as e:
        logger.error(f"Error en generación: {str(e)}", exc_info=True)
        return f"Error en la generación de respuesta: {str(e)}"

def get_tools():
  tools = [
    search_internet_tool
  ]

  available_functions = {
    'search_internet_tool': search_internet_tool
  }
  return tools, available_functions
