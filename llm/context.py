import json
from os.path import abspath

## MESSAGE HANDLING
def init_context(system_prompt):
  return [{'role': 'system', 'content': system_prompt}]

def append_context(messages, role, content="<no content>", tools=None):
    if tools:
      msg = {'role': role, 'content': content, 'tool_calls': tools}
    else:
      msg = {'role': role, 'content': content}

    print(msg)

    messages.append(msg)
    return messages

def purge_context(messages, msg_keep, msg_max):
    #print(f"len(messages) {len(messages)} > msg_max {msg_max} => {len(messages) > msg_max}")
    print(f"\n 💬 Messages: {len(messages)} / {msg_max}")
    if len(messages) > msg_max:
      print(f" 📋🗑️ Context purge triggered")
      return [{'role': 'system', 'content': system_prompt}] + messages[-msg_keep:]
    return messages

def print_context(messages, window):
    #print(json.dumps(messages, indent=2))
    messages_part = messages[-window:]
    print(json.dumps(messages_part, indent=2))

def save_context(key, messages):
  #print(abspath(f"data/{key}.json"))
  try:
    with open(f"data/{key}.json", "w") as f:
      f.write(json.dumps(messages))
  except Exception as e:
    print(f"Cannot save chat history for {key}!\n{str(e)}")

def load_context(key):
  #print(abspath(f"data/{key}.json"))
  try:
    f = open(f"data/{key}.json","r")
    return json.loads(f.read())
  except Exception as e:
    print(f"Cannot load chat history for {key}!\n{str(e)}")
    return None

