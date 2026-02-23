"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: gpt_structure.py
Description: Wrapper functions for calling OpenAI APIs.
"""
import json
import os
import random
import openai
import time

from utils import *

openai.api_key = openai_api_key
openai.api_base = "http://localhost:11434/v1"

# Configurable model — set REVERIE_MODEL env var to override
REVERIE_MODEL = os.environ.get("REVERIE_MODEL", "qwen2.5:32b")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

def temp_sleep(seconds=0.1):
  time.sleep(seconds)

def ChatGPT_single_request(prompt): 
  temp_sleep()

  system_prompt = "You are a strict data formatting assistant. You must directly output the requested format. Do NOT include conversational filler, explanations, or introductory text like 'Here is the...'. Output ONLY the raw required response."

  completion = openai.ChatCompletion.create(
    model=REVERIE_MODEL, 
    messages=[
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": prompt}
    ]
  )
  return completion["choices"][0]["message"]["content"]


# ============================================================================
# #####################[SECTION 1: CHATGPT-3 STRUCTURE] ######################
# ============================================================================

def GPT4_request(prompt): 
  """
  Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
  server and returns the response. 
  ARGS:
    prompt: a str prompt
    gpt_parameter: a python dictionary with the keys indicating the names of  
                   the parameter and the values indicating the parameter 
                   values.   
  RETURNS: 
    a str of GPT-3's response. 
  """
  temp_sleep()

  try: 
    system_prompt = "You are a strict data formatting assistant. You must directly output the requested format. Do NOT include conversational filler, explanations, or introductory text like 'Here is the...'. Output ONLY the raw required response."
    import requests
    print(f"Making request to Ollama with model {REVERIE_MODEL} (GPT4_request)...")
    response = requests.post(f"{OLLAMA_URL}/api/chat", json={
      "model": REVERIE_MODEL,
      "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
      ],
      "stream": False
    })
    print(f"Received response from Ollama (GPT4_request)")
    return response.json()["message"]["content"]
  
  except Exception as e: 
    print (f"ChatGPT ERROR: {e}")
    return "ChatGPT ERROR"


def ChatGPT_request(prompt): 
  """
  Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
  server and returns the response. 
  ARGS:
    prompt: a str prompt
    gpt_parameter: a python dictionary with the keys indicating the names of  
                   the parameter and the values indicating the parameter 
                   values.   
  RETURNS: 
    a str of GPT-3's response. 
  """
  # temp_sleep()
  try: 
    system_prompt = "You are a strict data formatting assistant. You must directly output the requested format. Do NOT include conversational filler, explanations, or introductory text like 'Here is the...'. Output ONLY the raw required response."
    import requests
    print(f"Making request to Ollama with model {REVERIE_MODEL} (ChatGPT_request)...")
    response = requests.post(f"{OLLAMA_URL}/api/chat", json={
      "model": REVERIE_MODEL,
      "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
      ],
      "stream": False
    })
    print(f"Received response from Ollama (ChatGPT_request)")
    return response.json()["message"]["content"]
  
  except Exception as e: 
    print (f"ChatGPT ERROR: {e}")
    return "ChatGPT ERROR"


def GPT4_safe_generate_response(prompt, 
                                   example_output,
                                   special_instruction,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
  prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
  prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
  prompt += "Example output json:\n"
  prompt += '{"output": "' + str(example_output) + '"}'

  if verbose: 
    print ("CHAT GPT PROMPT")
    print (prompt)

  for i in range(repeat): 

    try: 
      curr_gpt_response = GPT4_request(prompt).strip()
      end_index = curr_gpt_response.rfind('}') + 1
      curr_gpt_response = curr_gpt_response[:end_index]
      curr_gpt_response = json.loads(curr_gpt_response)["output"]
      
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      
      if verbose: 
        print ("---- repeat count: \n", i, curr_gpt_response)
        print (curr_gpt_response)
        print ("~~~~")

    except: 
      pass

  return False


def ChatGPT_safe_generate_response(prompt, 
                                   example_output,
                                   special_instruction,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
  # prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
  prompt = '"""\n' + prompt + '\n"""\n'
  prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
  prompt += "Example output json:\n"
  prompt += '{"output": "' + str(example_output) + '"}'

  if verbose: 
    print ("CHAT GPT PROMPT")
    print (prompt)

  for i in range(repeat): 

    try: 
      curr_gpt_response = ChatGPT_request(prompt).strip()
      end_index = curr_gpt_response.rfind('}') + 1
      curr_gpt_response = curr_gpt_response[:end_index]
      curr_gpt_response = json.loads(curr_gpt_response)["output"]

      # print ("---ashdfaf")
      # print (curr_gpt_response)
      # print ("000asdfhia")
      
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      
      if verbose: 
        print ("---- repeat count: \n", i, curr_gpt_response)
        print (curr_gpt_response)
        print ("~~~~")

    except: 
      pass

  return False


def ChatGPT_safe_generate_response_OLD(prompt, 
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
  if verbose: 
    print ("CHAT GPT PROMPT")
    print (prompt)

  for i in range(repeat): 
    try: 
      curr_gpt_response = ChatGPT_request(prompt).strip()
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      if verbose: 
        print (f"---- repeat count: {i}")
        print (curr_gpt_response)
        print ("~~~~")

    except: 
      pass
  print ("FAIL SAFE TRIGGERED") 
  return fail_safe_response


# ============================================================================
# ###################[SECTION 2: ORIGINAL GPT-3 STRUCTURE] ###################
# ============================================================================

def GPT_request(prompt, gpt_parameter): 
  """
  Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
  server and returns the response. 
  """
  temp_sleep()
  try: 
    system_prompt = "You are a strict data formatting assistant. You must directly output the requested format. Do NOT include conversational filler, explanations, or introductory text like 'Here is the...'. Output ONLY the raw required response."
    
    # Use ChatCompletion instead of Completion for Ollama compatibility
    import requests
    print(f"Making request to Ollama with model {REVERIE_MODEL}...")
    response = requests.post(f"{OLLAMA_URL}/api/chat", json={
      "model": REVERIE_MODEL,
      "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
      ],
      "options": {
        "temperature": gpt_parameter.get("temperature", 0.7),
        "top_p": gpt_parameter.get("top_p", 1.0),
        "frequency_penalty": gpt_parameter.get("frequency_penalty", 0.0),
        "presence_penalty": gpt_parameter.get("presence_penalty", 0.0),
        "stop": gpt_parameter.get("stop", [])
      },
      "stream": False
    })
    print(f"Received response from Ollama")
    return response.json()["message"]["content"]
  except Exception as e: 
    print ("TOKEN LIMIT EXCEEDED", e)
    return "TOKEN LIMIT EXCEEDED"


def generate_prompt(curr_input, prompt_lib_file): 
  """
  Takes in the current input (e.g. comment that you want to classifiy) and 
  the path to a prompt file. The prompt file contains the raw str prompt that
  will be used, which contains the following substr: !<INPUT>! -- this 
  function replaces this substr with the actual curr_input to produce the 
  final promopt that will be sent to the GPT3 server. 
  ARGS:
    curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                INPUT, THIS CAN BE A LIST.)
    prompt_lib_file: the path to the promopt file. 
  RETURNS: 
    a str prompt that will be sent to OpenAI's GPT server.  
  """
  if type(curr_input) == type("string"): 
    curr_input = [curr_input]
  curr_input = [str(i) for i in curr_input]

  f = open(prompt_lib_file, "r")
  prompt = f.read()
  f.close()
  for count, i in enumerate(curr_input):   
    prompt = prompt.replace(f"!<INPUT {count}>!", i)
  if "<commentblockmarker>###</commentblockmarker>" in prompt: 
    prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
  return prompt.strip()


def safe_generate_response(prompt, 
                           gpt_parameter,
                           repeat=5,
                           fail_safe_response="error",
                           func_validate=None,
                           func_clean_up=None,
                           verbose=False): 
  if verbose: 
    print (prompt)

  for i in range(repeat): 
    curr_gpt_response = GPT_request(prompt, gpt_parameter)
    if func_validate(curr_gpt_response, prompt=prompt): 
      return func_clean_up(curr_gpt_response, prompt=prompt)
    if verbose: 
      print ("---- repeat count: ", i, curr_gpt_response)
      print (curr_gpt_response)
      print ("~~~~")
  return fail_safe_response


def get_embedding(text, model="nomic-embed-text:latest"):
  text = text.replace("\n", " ")
  if not text: 
    text = "this is blank"
  
  # Ensure we use ollama's embedding format
  import requests
  try:
    response = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
      "model": model,
      "prompt": text
    })
    return response.json()["embedding"]
  except Exception as e:
    print(f"Embedding error: {e}")
    # Return dummy embedding of size 768 (nomic size)
    return [0.0] * 768

def generate_code_task(context, task_description, repo_path="/Users/tomyimkc/Documents/GitHub/Travian_Bot"):
  """
  Used for the Sim-to-Code bridge. Hits Ollama to generate raw code based on context and task.
  Now uses a two-step process to read necessary files before generating code.
  """
  import os
  import json
  import requests
  
  try:
    # STEP 1: Identify which files to read
    print(f"Making request to Ollama (STEP 1: Identify files to read)...")
    step1_system = (
        "You are an expert Python developer. You will be provided with a codebase summary and a task. "
        "Based on the summary, identify which existing files you need to read to complete the task. "
        "Output ONLY a JSON list of filenames. For example: [\"main.py\", \"utils.py\"]. "
        "CRITICAL: If the task requires modifying an existing file, you MUST include that file in the list so you can read its current contents. Do not guess the contents of existing files. "
        "If you are certain you do not need to read any existing files (e.g. creating a completely new isolated file), output an empty list: []."
    )
    step1_prompt = f"Codebase Summary:\n{context}\n\nTask: {task_description}"
    
    response1 = requests.post(f"{OLLAMA_URL}/api/chat", json={
        "model": REVERIE_MODEL,
      "messages": [
        {"role": "system", "content": step1_system},
        {"role": "user", "content": step1_prompt}
      ],
      "stream": False
    })
    
    files_to_read = []
    try:
        content1 = response1.json()["message"]["content"]
        # Robust JSON extraction
        start_idx = content1.find('[')
        end_idx = content1.rfind(']')
        start_dict = content1.find('{')
        end_dict = content1.rfind('}')
        
        # Determine if it's a list or dict
        if start_idx != -1 and end_idx != -1 and (start_dict == -1 or start_idx < start_dict):
            content1 = content1[start_idx:end_idx+1]
        elif start_dict != -1 and end_dict != -1:
            content1 = content1[start_dict:end_dict+1]
            
        parsed_files = json.loads(content1)
        if isinstance(parsed_files, list):
            files_to_read = parsed_files
        elif isinstance(parsed_files, dict):
            # Sometimes it returns {"files": ["..."]}
            for v in parsed_files.values():
                if isinstance(v, list):
                    files_to_read.extend(v)
    except Exception as e:
        print(f"Failed to parse files to read: {e}. Raw: {response1.json()['message']['content']}")
        
    print(f"Files to read identified: {files_to_read}")
    
    # STEP 2: Read the requested files
    file_contents_str = ""
    if files_to_read:
        file_contents_str = "\n\n=== FULL CONTENT OF REQUESTED FILES ===\n"
        for filename in files_to_read:
            filepath = os.path.join(repo_path, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    file_contents_str += f"\n--- {filename} ---\n{content}\n"
                except Exception as e:
                    file_contents_str += f"\n--- {filename} ---\nError reading file: {e}\n"
            else:
                file_contents_str += f"\n--- {filename} ---\nFile does not exist.\n"
                
    # STEP 3: Generate the actual code
    print(f"Making request to Ollama (STEP 2: Generate code)...")
    step2_system = (
        "You are an expert Python developer. You will be provided with a codebase summary, "
        "the full content of relevant files, and a task. "
        "You must output ONLY a valid JSON object with a single key 'files' containing a list of file objects. "
        "If you are creating a NEW file, the object must have 'filename' and 'code' (the full raw code). "
        "If you are modifying an EXISTING file, the object must have 'filename' and 'search_replace'. "
        "'search_replace' is a list of objects with 'search' (the exact existing lines to replace) and 'replace' (the new lines). "
        "For example, to edit a file:\n"
        "{\"files\": [{\"filename\": \"main.py\", \"search_replace\": [{\"search\": \"    print('a')\\n\", \"replace\": \"    print('b')\\n\"}]}]}\n"
        "For example, to create a file:\n"
        "{\"files\": [{\"filename\": \"new.py\", \"code\": \"print('hello')\"}]}\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. For search_replace, 'search' MUST match the existing file exactly, including indentation and whitespace.\n"
        "2. Do NOT include any conversational filler. Just output the JSON."
    )
    step2_prompt = (
        f"Codebase Summary:\n{context}{file_contents_str}\n\nTask: {task_description}\n\n"
        "CRITICAL: Output ONLY a valid JSON object with a 'files' key containing a list of file objects. "
        "Do not include any conversational filler or explanations. "
        "Begin your response with { and end it with }."
    )
    
    response2 = requests.post(f"{OLLAMA_URL}/api/chat", json={
        "model": REVERIE_MODEL,
      "messages": [
        {"role": "system", "content": step2_system},
        {"role": "user", "content": step2_prompt}
      ],
      "stream": False
    })
    
    content2 = response2.json()["message"]["content"]
    print("DEBUG content2:", content2)
    
    try:
        # Robust JSON extraction
        import re
        start_idx = content2.find('{')
        end_idx = content2.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content2 = content2[start_idx:end_idx+1]
            
        parsed = json.loads(content2)
        
        if "files" in parsed and isinstance(parsed["files"], list):
            # Apply edits to existing files
            final_files = []
            for file_obj in parsed["files"]:
                filename = file_obj.get("filename")
                if "search_replace" in file_obj:
                    # Apply edits
                    filepath = os.path.join(repo_path, filename)
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        
                        for edit in file_obj["search_replace"]:
                            old_code = edit.get("search", "")
                            new_code = edit.get("replace", "")
                            if old_code and old_code in file_content:
                                file_content = file_content.replace(old_code, new_code)
                            else:
                                print(f"WARNING: Could not find search string in {filename}:\n{old_code}")
                        
                        final_files.append({"filename": filename, "code": file_content})
                    else:
                        print(f"WARNING: Tried to edit non-existent file {filename}")
                elif "changes" in file_obj:
                    # Apply line-number based changes (fallback for Qwen's preferred format)
                    filepath = os.path.join(repo_path, filename)
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        # Sort changes in reverse order so line numbers don't shift
                        changes = sorted(file_obj["changes"], key=lambda x: x.get("line_number", 0), reverse=True)
                        for change in changes:
                            line_num = change.get("line_number", 0) - 1 # 0-indexed
                            content = change.get("content", "")
                            ctype = change.get("change_type", change.get("type", "insert"))
                            
                            if 0 <= line_num <= len(lines):
                                if ctype == "insert":
                                    # Ensure content ends with newline if we are inserting a line
                                    if not content.endswith('\n'): content += '\n'
                                    lines.insert(line_num, content)
                                elif ctype == "replace":
                                    if not content.endswith('\n'): content += '\n'
                                    lines[line_num] = content
                                elif ctype == "delete":
                                    lines.pop(line_num)
                                    
                        final_files.append({"filename": filename, "code": "".join(lines)})
                    else:
                        print(f"WARNING: Tried to edit non-existent file {filename}")
                elif "code" in file_obj:
                    final_files.append({"filename": filename, "code": file_obj["code"]})
            
            return final_files
        return [{"filename": "fallback_output.py", "code": content2}]
    except Exception as e:
        print(f"Code Task ERROR: Failed to parse JSON. Raw output: {content2}")
        return [{"filename": "fallback_output.py", "code": content2}]
  except Exception as e:
    print(f"Code Task ERROR: {e}")
    return [{"filename": "error.py", "code": f"# Error: {e}"}]

def generate_code_review(persona_name, task_description, code_results):
    """
    Generates a brief summary/review of the code written by the persona.
    Used to inject context into the Manager's memory so they can discuss it.
    """
    import requests
    
    try:
        print(f"Making request to Ollama to generate code review for {persona_name}...")
        
        # Prepare the code content string
        code_str = ""
        for file_obj in code_results:
            filename = file_obj.get("filename", "unknown")
            if "code" in file_obj:
                code_str += f"\n--- {filename} ---\n{file_obj['code'][:2000]}...\n" # Truncate to avoid massive context
            elif "search_replace" in file_obj:
                code_str += f"\n--- {filename} (Edits) ---\n"
                for edit in file_obj["search_replace"]:
                    code_str += f"Replaced:\n{edit.get('search', '')}\nWith:\n{edit.get('replace', '')}\n"
            elif "changes" in file_obj:
                code_str += f"\n--- {filename} (Changes) ---\n"
                for change in file_obj["changes"]:
                    code_str += f"Line {change.get('line_number')}: {change.get('content')}\n"

        system_prompt = (
            "You are an expert Senior Developer reviewing code from a junior developer. "
            "You will be provided with the original task and the code changes they made. "
            "Write a brief, 2-3 sentence summary of what they did, and include 1 specific piece of feedback or praise. "
            "Write this from a first-person perspective, as if you are thinking to yourself. "
            "For example: 'I see Isabella added the login print statement to travianlogin.py. It looks correct, but I should ask her if she tested it.'"
        )
        
        prompt = f"Developer Name: {persona_name}\nTask: {task_description}\nCode Changes:\n{code_str}"
        
        response = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": REVERIE_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        })
        
        review_content = response.json()["message"]["content"].strip()
        print(f"Generated Code Review: {review_content}")
        return review_content
        
    except Exception as e:
        print(f"Code Review ERROR: {e}")
        return f"I need to review the code {persona_name} just wrote for the task: {task_description}."

if __name__ == '__main__':
  gpt_parameter = {"engine": "text-davinci-003", "max_tokens": 50, 
                   "temperature": 0, "top_p": 1, "stream": False,
                   "frequency_penalty": 0, "presence_penalty": 0, 
                   "stop": ['"']}
  curr_input = ["driving to a friend's house"]
  prompt_lib_file = "prompt_template/test_prompt_July5.txt"
  prompt = generate_prompt(curr_input, prompt_lib_file)

  def __func_validate(gpt_response): 
    if len(gpt_response.strip()) <= 1:
      return False
    if len(gpt_response.strip().split(" ")) > 1: 
      return False
    return True
  def __func_clean_up(gpt_response):
    cleaned_response = gpt_response.strip()
    return cleaned_response

  output = safe_generate_response(prompt, 
                                 gpt_parameter,
                                 5,
                                 "rest",
                                 __func_validate,
                                 __func_clean_up,
                                 True)

  print (output)


















