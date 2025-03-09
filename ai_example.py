from AIUnit import AIUnit
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

model = AIUnit(config)
response = model.generate_response("What is the weather like today?")
print(response)
