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

## MESSAGE HANDLING
def init_context(system_prompt):
  logger.info(f"Context initialization")
  return [{'role': 'system', 'content': system_prompt}]

def append_context(messages, role, content="<no content>", tools=None):
    if tools:
      logger.info(f"Message with tools request from {role}")
      msg = {'role': role, 'content': content, 'tool_calls': tools}
    else:
      logger.info(f"Text-only message from {role}")
      msg = {'role': role, 'content': content}

    logger.debug(msg)
    messages.append(msg)
    return messages

def purge_context(messages, msg_keep, msg_max):
    logger.info(f"\💬 Messages: {len(messages)} / {msg_max}")
    if len(messages) > msg_max:
      logger.warning(f" 📋🗑️ Context purge triggered")
      return [messages[0]] + messages[-msg_keep:]
    return messages

def print_context(messages, window):
    messages_part = messages[-window:]
    logger.debug(json.dumps(messages_part, indent=2))

def save_context(key, messages):
  logger.info(f"saved context for {key}")
  logger.debug(abspath(f"data/{key}.json"))
  try:
    with open(f"data/{key}.json", "w") as f:
      f.write(json.dumps(messages))
  except Exception as e:
    logger.error(f"Cannot save chat history for {key}!\n{str(e)}")

def load_context(key):
  logger.info(f"loaded context for {key}")
  logger.debug(abspath(f"data/{key}.json"))
  try:
    f = open(f"data/{key}.json","r")
    return json.loads(f.read())
  except Exception as e:
    logger.error(f"Cannot load chat history for {key}!\n{str(e)}")
    return None

def compress_context(messages, init_msg, config):
    load_dotenv()

    proto = config["protocol"]
    host = config["hostname"]
    port = config["port"]
    model = config["model"]
    stream = config["stream"]
    client = Client(host=f"{proto}://{host}:{port}")
    options = {'temperature': config["temperature"], 'num_ctx': config["num_ctx"]}

    logger.debug(f"{messages}")
    messages = append_context(messages, "user", content=config['system_prompt'])
    logger.debug(f"{messages}")
    llm_reply = client.chat(model=model, options=options, messages=messages, stream=stream)
    logger.info(f"{llm_reply}")

    new_messages = init_context(init_msg)
    new_messages = append_context(new_messages, "assistant", content=llm_reply.message.content)
    logger.info(f"Compression completed!")
    return new_messages
