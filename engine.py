import json
import time
import requests
from typing import List, Dict, Any, Tuple

import config
import tools
from personas import get_system_prompt

class GroqInferenceEngine:


    def __init__(self):
        self.api_url = config.GROQ_API_URL
        self.api_key = config.GROQ_API_KEY
        self.model = config.MODEL_NAME
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _execute_api_call(self, payload: Dict[str, Any], max_retries: int = 3, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Executes the HTTP POST to Groq with exponential backoff."""
        attempt = 0
        current_headers = headers if headers else self.headers
        while attempt < max_retries:
            try:
                response = requests.post(self.api_url, headers=current_headers, json=payload, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                print(f"[Engine] HTTP Error {status_code}: {e.response.text}")
                
                # Rate limit or server error backoff
                if status_code in [429, 500, 502, 503, 504]:
                    attempt += 1
                    sleep_time = 2 ** attempt
                    print(f"[Engine] Retrying in {sleep_time} seconds (Attempt {attempt}/{max_retries})...")
                    time.sleep(sleep_time)
                else:
                    raise Exception(f"API Request Failed: {e.response.text}")
            except requests.exceptions.RequestException as e:
                attempt += 1
                print(f"[Engine] Network Error: {e}. Retrying...")
                time.sleep(2)
                
        raise Exception("Max retries exceeded while calling inference engine.")

    def generate_response(self, mode: str, context_messages: List[Dict[str, str]], api_key: str = None) -> str:

        
        # 0. Set up request-specific headers
        current_api_key = api_key if api_key else self.api_key
        request_headers = {
            "Authorization": f"Bearer {current_api_key}",
            "Content-Type": "application/json"
        }
        
        # 1. Compile the active message stack
        sys_prompt_content = get_system_prompt(mode)
        
        active_messages = [{"role": "system", "content": sys_prompt_content}]
        active_messages.extend(context_messages)
        
        # 2. Build Initial Payload
        payload = {
            "model": self.model,
            "messages": active_messages,
            "tools": tools.TOOLS_SCHEMA,
            "tool_choice": "auto",
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        print(f"[Engine] Initiating inference sequence for mode: {mode}")
        
        # 3. Fire first request
        resp_data = self._execute_api_call(payload, headers=request_headers)
        response_message = resp_data['choices'][0]['message']
        
        # 4. Process Tool Calls if any
        if response_message.get('tool_calls'):
            active_messages.append(response_message)
            
            for tool_call in response_message['tool_calls']:
                func_name = tool_call['function']['name']
                func_args = json.loads(tool_call['function']['arguments'])
                
                print(f"[Engine] Autonomous Tool Execution Triggered: {func_name}({func_args})")
                
                # Locate and execute the tool
                if func_name in tools.TOOL_REGISTRY:
                    tool_func = tools.TOOL_REGISTRY[func_name]
                    if func_args:
                        tool_result = tool_func(**func_args)
                    else:
                        tool_result = tool_func()
                else:
                    tool_result = json.dumps({"error": f"Unknown tool: {func_name}"})
                    
                # Append tool result to stack
                active_messages.append({
                    "tool_call_id": tool_call['id'],
                    "role": "tool",
                    "name": func_name,
                    "content": tool_result
                })
                
            # Fire secondary request with tool data injected
            payload['messages'] = active_messages
            payload.pop('tool_choice', None) # Prevent infinite loops
            payload.pop('tools', None)
            
            print(f"[Engine] Synthesizing final response post-tool execution...")
            second_resp_data = self._execute_api_call(payload, headers=request_headers)
            final_reply = second_resp_data['choices'][0]['message']['content']
        else:
            final_reply = response_message.get('content', '')
            
        # 5. Format Guarantee Layer
        # Ensure the response always matches the Ren identity tag for UI parsing
        if not final_reply.strip().startswith('[Ren]:'):
            final_reply = f"[Ren]: {final_reply.strip()}"
            
        return final_reply

if __name__ == "__main__":
    engine = GroqInferenceEngine()
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    print(engine.generate_response("ren", messages))
