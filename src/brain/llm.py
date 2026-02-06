from huggingface_hub import InferenceClient
from ..config import Config

class ReasoningBrain:
    def __init__(self):
        self.token = Config.HUGGINGFACE_API_TOKEN
        if not self.token:
            print("Warning: HUGGINGFACE_API_TOKEN not found in environment variables.")
        # passing the token is optional for some models but recommended for higher limits
        self.client = InferenceClient(token=self.token)
        # Using the requested 70B model via API
        self.model_id = "meta-llama/Llama-3.3-70B-Instruct" 

    def think(self, user_input, context=""):
        """
        Uses a powerful cloud model to reason and answer.
        """
        system_message = "You are Jarvis, a helpful and intelligent AI assistant. Answer the user's question clearly and concisely."
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"{context}\n\nUser Question: {user_input}"}
        ]

        try:
            response = self.client.chat_completion(
                model=self.model_id,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error contacting Hugging Face Brain: {e}"
