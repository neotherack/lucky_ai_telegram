import uuid

from ollama import Client, ResponseError
from .context import init_context, append_context, purge_context, print_context, save_context, load_context
from .tools import get_tools, toolcall_to_json

nanosec_to_sec = 100000000

def get_client(config):
  proto = config["protocol"]
  host = config["hostname"]
  port = config["port"]
  return Client(host=f"{proto}://{host}:{port}")

def ai_step_stats(llm_response):
    model = llm_response.model
    prompt_tokens = llm_response.prompt_eval_count
    eval_tokens = llm_response.eval_count
    load_dur = int(llm_response.load_duration/nanosec_to_sec)
    prompt_dur = int(llm_response.prompt_eval_duration/nanosec_to_sec)
    gen_dur = int(llm_response.eval_duration/nanosec_to_sec)
    total_dur = int(llm_response.total_duration/nanosec_to_sec)
    print(f" 🧠 {model} loaded in {load_dur} secs\nPROMPT: {prompt_tokens} tokens in {prompt_dur} secs\nGENERATION: {eval_tokens} tokens in  {gen_dur} secs. TOTAL {total_dur}")

def get_response_from_model(client, messages, config, tools):
    model = config["model"]
    stream = config["stream"]
    show_stats = config["show_stats"]
    options = {'temperature': config["temperature"], 'num_ctx': config["num_ctx"]}

    llm_reply = client.chat(model=model, options=options, messages=messages, stream=stream, tools=tools)

    if show_stats:
        ai_step_stats(llm_reply)

    if llm_reply.message.tool_calls:
      tool_call_list = [toolcall_to_json(tool) for tool in llm_reply.message.tool_calls]
      return llm_reply.message.content, tool_call_list
    else:
      return llm_reply.message.content, None

def run_tools(available_functions, requested_tools):
    tool_messages = []

    if requested_tools:
      for tool in requested_tools:

        tool_id   = tool["id"]
        func = tool["function"]
        tool_name = func["name"]
        tool_args = func["arguments"]

        func_call = available_functions.get(tool_name)
        if func_call:
          print(f" 🛠️ TOOL {tool_name}({tool_args})")
          try:
            function_result = func_call(**tool_args)
            tool_messages.append({'role': 'tool', 'content': str(function_result), 'name': tool_name, 'tool_call_id': tool_id})
          except Exception as e:
            tool_messages.append({'role': 'tool', 'content': str(e), 'name': tool_name, 'tool_call_id': tool_id})
        else:
          print('Function', tool_name, 'not found')
          tool_messages.append({'role': 'tool', 'content': 'tool not found!', 'name': tool_name, 'tool_call_id': tool_id})
      return tool_messages
    else:
      print(' 🙅‍♂️ NO TOOLS, text only')
      return tool_messages

def tool_list_info(tools):
    if tools and tools!=[]:
      return "\n".join([f'🛠️ {tool["function"]["name"]}' for tool in tools])
    else:
      return ""

def interact_with_ai(user_request, chat_id, config):
    client = get_client(config)
    tool_captions = ""

    history = load_context(chat_id)
    if history:
      messages=history
    else:
      messages=init_context(config["system_prompt"])

    messages = append_context(messages, "user", user_request)

    tool_iter = 0
    tool_max_iter = config["max_iter"]
    tools, available_functions = get_tools()

    while tool_iter < tool_max_iter:
      tool_iter+=1

      llm_response, tool_calls = get_response_from_model(client, messages, config, tools)
      messages = append_context(messages, "assistant", llm_response, tool_calls)
      tool_messages = run_tools(available_functions, tool_calls)

      if tool_messages!=[]: #loop, tools used
        messages = messages+tool_messages
        messages = purge_context(messages, config["context_keep"], config["context_max"])
        tool_captions+=tool_list_info(tool_calls)
      else: #talk to user, loop finished!
        save_context(chat_id, messages)
        return tool_captions+messages[-1]['content']

    return "Max tool iterations triggered!"
