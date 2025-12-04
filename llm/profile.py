import json
import logging
import requests
import os
from os.path import abspath

# Configure basic logging
logging.basicConfig(
    format='%(levelname)s: %(name)s %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def get_filename(key, ext='prf'):
  return f"data/{key}.prf"

def save_profile(key, messages, previous_profile):
  logger.info(f"saved profile for {key}")
  logger.debug(abspath(get_filename(key)))
  try:
    profile_data = extract_profile(messages, previous_profile)
    with open(get_filename(key), "w") as f:
      f.write(profile_data)
  except Exception as e:
    logger.error(f"Cannot save profile for {key}!\n{str(e)}")

def load_profile(key):
  logger.info(f"loaded profile for {key}")
  logger.debug(abspath(get_filename(key)))
  try:
    f = open(get_filename(key), "r")
    return f.read()
  except Exception as e:
    logger.error(f"Cannot load profile for {key}!\n{str(e)}")
    return None

def extract_profile(messages, previous_profile):
    logger.info("Profile extraction in progress")
    system_prompt = f"""Actualiza el perfil del usuario utilizando la información de los últimos mensajes, manteniendo la plantilla de datos.
    No respondas nada más que la plantilla con los datos con aquellos datos conocidos, deja el resto en blanco mientras sean desconocidos.

    Plantilla de datos:
    - Nombre / Alias:
    - Edad / Fecha de nacimiento:
    - Idiomas que puede hablar:
    - Nacionalidad:
    - Profesión:
    - Intereses personales:
    - Otros detalles:
    """

    prompt = f"""Perfil anterior:
              {previous_profile}

              Mensajes:
              {messages}"""

    try:
        logger.info("Enviando solicitud a Ollama API")
        response = requests.post(
            'http://antares:11434/api/generate',
            json={
                'model': 'qwen2.5:7b-instruct-q4_0',
                'prompt': prompt,
                'system': system_prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_ctx': 5000
                }
            }
        )

        logger.info(f"{prompt}")
        response.raise_for_status()

        resp = json.loads(response.text)['response']

        logger.info(f"Respuesta recibida de Ollama\n{resp}")
        return resp

    except Exception as e:
        logger.error(f"Error en generación: {str(e)}", exc_info=True)
        return f"Error en la generación de respuesta: {str(e)}"
