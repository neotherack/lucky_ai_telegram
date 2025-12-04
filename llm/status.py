import logging
from datetime import datetime
from zoneinfo import ZoneInfo

# Configure basic logging
logging.basicConfig(
    format='%(levelname)s: %(name)s %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def get_filename(key, ext='prf'):
  return f"data/{key}.prf"

def load_status():
  logger.info(f"loaded status")
  try:
    return datetime.now(tz=ZoneInfo('Europe/Madrid'))
  except Exception as e:
    logger.error(f"Cannot load status!\n{str(e)}")
    return None
