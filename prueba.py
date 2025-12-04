import requests
from duckduckgo_search import DDGS
from trafilatura import fetch_url, extract
import json

def ollama_search_tool(keywords: str) -> str:
    """
    Realiza una búsqueda web, procesa los resultados y genera una respuesta usando Ollama.
    
    Args:
        keywords: Términos de búsqueda introducidos por el usuario
        
    Returns:
        str: Respuesta formateada basada en los resultados de búsqueda
    """
    
    # 1. Búsqueda con DuckDuckGo
    try:
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(keywords, max_results=3)]
    except Exception as e:
        return f"Error en la búsqueda: {str(e)}"

    if not search_results:
        return "No se encontraron resultados de búsqueda"

    # 2. Extracción de contenido de los enlaces
    processed_results = []
    for i, result in enumerate(search_results[:3], 1):
        try:
            url = result.get('href', '')
            if not url:
                continue
                
            downloaded = fetch_url(url)
            content = extract(downloaded, include_links=False, include_tables=False)
            
            if content:
                processed_results.append({
                    'num': i,
                    'url': url,
                    'content': content[:2000]  # Limitamos el contenido para no sobrecargar el modelo
                })
                
        except Exception as e:
            continue

    # 3. Construcción del prompt para Ollama
    search_context = "\n\n".join(
        [f"Búsqueda {res['num']} ({res['url']}):\n{res['content']}" 
         for res in processed_results]
    )

    system_prompt = f"""Eres un asistente de búsqueda experto. El usuario preguntó: '{keywords}'.
    
    Los resultados de búsqueda son:
    {search_context if search_context else 'No se encontró contenido relevante en los resultados'}
    
    Responde de forma concisa y útil:
    1. Si la información es relevante y suficiente: Da una respuesta estructurada citando las fuentes (Búsqueda 1, 2 o 3)
    2. Si la información es insuficiente o no relevante: Indícalo claramente y sugiere parámetros de búsqueda más específicos
    """

    # 4. Llamada a la API de Ollama
    try:
        response = requests.post(
            'http://perseo:11434/api/generate',
            json={
                'model': 'qwen2.5:7b-instruct-q4_0',
                'prompt': f"Pregunta: {keywords}",
                'system': system_prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,
                    'num_ctx': 4096
                }
            }
        )
        response.raise_for_status()
        return json.loads(response.text)['response']
        
    except Exception as e:
        return f"Error en la generación de respuesta: {str(e)}"

# Ejemplo de uso
if __name__ == "__main__":
  search_term = input("Indica la búsqueda a realizar: ")
  print(ollama_search_tool(search_term))
