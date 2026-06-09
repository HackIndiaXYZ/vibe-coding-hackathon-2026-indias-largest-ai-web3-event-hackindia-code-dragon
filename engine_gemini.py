import json
import time
from typing import List, Dict, Any

import config
import tools
from personas import get_system_prompt

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[Engine] WARNING: google-generativeai not installed. Install with: pip install google-generativeai")


class GeminiInferenceEngine:
    """Firebase Gemini AI Inference Engine - Drop-in replacement for GroqInferenceEngine"""

    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise RuntimeError("google-generativeai library not installed")
        
        self.api_key = config.FIREBASE_GEMINI_API_KEY
        self.model = config.GEMINI_MODEL
        
        if not self.api_key:
            raise ValueError("FIREBASE_GEMINI_API_KEY not configured in .env")
        
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model_name=self.model)
        print(f"[Engine] [OK] Gemini AI Engine initialized with model: {self.model}")

    def generate_response(
        self, 
        mode: str, 
        context_messages: List[Dict[str, str]], 
        api_key: str = None, 
        settings: Dict[str, Any] = None
    ) -> str:
        """
        Generate response using Gemini API
        
        Args:
            mode: Interaction mode (e.g., 'ren', 'study', 'code')
            context_messages: List of message dicts with 'role' and 'content'
            api_key: Optional override API key
            settings: Optional settings dict for personality/response length
        
        Returns:
            str: Response formatted with [Ren]: prefix
        """
        
        # 1. Set up request-specific API key if provided
        current_api_key = api_key if api_key else self.api_key
        if current_api_key != self.api_key:
            genai.configure(api_key=current_api_key)
        
        # 2. Get system prompt and customize based on settings
        sys_prompt_content = get_system_prompt(mode)
        temperature = 0.7
        
        if settings:
            custom_directives = []
            
            personality = settings.get('personality', 'friendly')
            if personality == 'professional':
                custom_directives.append("Adopt an elite, professional, and strictly technical tone. Keep explanations formal, precise, and highly structured.")
            elif personality == 'creative':
                custom_directives.append("Adopt a creative, explanatory, and open-minded tone. Connect concepts to interesting real-world analogies and outside-the-box ideas.")
            
            resp_len = settings.get('response_length', 'medium')
            if resp_len == 'short':
                custom_directives.append("Be extremely brief, short, and concise. Avoid unnecessary preambles and keep explanations minimal.")
            elif resp_len == 'long':
                custom_directives.append("Be very thorough, long, and detailed. Provide comprehensive step-by-step breakdowns, detail edge cases, and elaborate fully.")
            
            if settings.get('coding_mode'):
                custom_directives.append("Focus heavily on production-ready, clean, optimal code examples. Explain syntactical and architectural nuances.")
            if settings.get('study_mode'):
                custom_directives.append("Prioritize educational concepts, pedagogical explanations, and structured breakdowns. Use study guide principles and prompt learning checkpoints.")
            
            if custom_directives:
                sys_prompt_content += "\n\n[USER CUSTOM SETTINGS DIRECTIVES]\n" + "\n".join(f"- {d}" for d in custom_directives)
            
            if 'creativity' in settings:
                try:
                    temperature = float(settings['creativity'])
                except (ValueError, TypeError):
                    pass
        
        # 3. Prepare messages for Gemini
        # Gemini expects: role = 'user' or 'model' (not 'assistant')
        formatted_messages = []
        
        # Add system prompt as first user message if not already included
        first_message_added = False
        for msg in context_messages:
            role = msg['role']
            if role == 'system':
                continue  # Skip system role, we'll prepend it
            if role == 'assistant':
                role = 'model'
            
            if not first_message_added:
                # Prepend system prompt to first user message
                formatted_messages.append({
                    'role': 'user',
                    'parts': [f"{sys_prompt_content}\n\n{msg['content']}"]
                })
                first_message_added = True
            else:
                formatted_messages.append({
                    'role': role,
                    'parts': [msg['content']]
                })
        
        # If no user messages, add system prompt alone
        if not first_message_added:
            formatted_messages.append({
                'role': 'user',
                'parts': [sys_prompt_content]
            })
        
        print(f"[Engine] Initiating Gemini inference for mode: {mode} | model: {self.model}")
        
        try:
            # 4. Call Gemini API (without tool calling for now - Gemini has different tool syntax)
            response = self.client.generate_content(
                contents=formatted_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048
                )
            )
            
            final_reply = response.text if response.text else "[Ren]: I encountered an issue generating a response."
            
        except Exception as e:
            print(f"[Engine] Gemini API Error: {str(e)}")
            raise Exception(f"Gemini API request failed: {str(e)}")
        
        # 5. Format response with [Ren]: prefix
        if not final_reply.strip().startswith('[Ren]:'):
            final_reply = f"[Ren]: {final_reply.strip()}"
        
        return final_reply


if __name__ == "__main__":
    engine = GeminiInferenceEngine()
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    print(engine.generate_response("ren", messages))
