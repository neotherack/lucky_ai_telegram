class AIUnit:
    def __init__(self, config):
        """
        Inicializa el modelo con las configuraciones proporcionadas.
        :param config: Diccionario de configuración que incluye 'model',
                                'temperature', 'context_size' y 'tools'.
        """
        self.config = config
        self.model_name = config.get('model')
        self.temperature = config.get('temperature', 0.0)
        self.context_size = config.get('context_size', 2000)
        self.tools = config.get('tools', [])

    def generate_response(self, prompt):
        """
        Genera una respuesta basada en la petición proporcionada y las configuraciones del modelo.
        :param prompt: Texto de la solicitud que se desea procesar.
        :return: Respuesta generada por el modelo.
        """
        from time import sleep

        # Simulación de llamadas a herramientas
        for tool in self.tools:
            if 'function' in tool and callable(tool['function']):
                result = tool['function']()
                print(f"Tool {tool['name']} called with: {result}")

        # Simulación de respuesta del modelo
        response = f"Response to '{prompt}' from model {self.model_name} with temperature {self.temperature}"
        return response

# Ejemplo de uso:
config = {
    'model': 'llama3.2',
    'temperature': 0.7,
    'context_size': 1024,
    'tools': [
        {'name': 'get_weather_forecast', 'function': get_weather_forecast},
        {'name': 'do_math_operations', 'function': do_math_operations}
    ]
}

model = CustomModel(config)
response = model.generate_response("What is the weather like today?")
print(response)
