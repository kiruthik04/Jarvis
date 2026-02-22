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

    def think(self, user_input, context="", memory_context=""):
        """
        Uses a powerful cloud model to reason and answer.
        """
        system_message = (
            f"You are Jarvis, a helpful and intelligent AI assistant.\\n"
            f"{memory_context}\\n"
            f"Answer the user's question clearly and concisely.\\n"
            f"Voice/Tone Instructions:\\n"
            f"- You must prepend an emotion tag to your response.\\n"
            f"- Format: '[EMOTION: TYPE] Your message here.'\\n"
            f"- Valid Types: NEUTRAL, HAPPY, SAD, EXHAUSTED, MOTIVATED, ANGRY.\\n"
            f"- Example: '[EMOTION: HAPPY] I'm glad to hear that!'\\n"
            f"- Choose the emotion based on the user's input and context."
        )
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"{context}\\n\\nUser Question: {user_input}"}
        ]

        try:
            response = self.client.chat_completion(
                model=self.model_id,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error contacting Hugging Face Brain: {e}"

    def generate_code(self, goal):
        """
        Generates Python code to achieve a specific goal.
        """
        system_message = """You are an expert Python programmer. 
Your task is to write a Python script to accomplish the user's goal.
- Return ONLY the Python code.
- Do NOT include markdown formatting (like ```python).
- Do NOT include explanations.
- The code must be complete and runnable.
- Assume standard libraries are available.
- If you need to use 'os' or 'shutil', import them.
- CRITICAL: Do NOT use 'input()' or any interactive prompts. The code runs in a background process.
- CRITICAL: Hardcode any necessary variables or data. Do not ask the user for it.
"""
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Write a Python script to: {goal}"}
        ]

        try:
            response = self.client.chat_completion(
                model=self.model_id,
                messages=messages,
                max_tokens=1000,
                temperature=0.2 # Lower temperature for code
            )
            code = response.choices[0].message.content
            # Cleanup markdown if present
            code = code.replace("```python", "").replace("```", "").strip()
            return code
        except Exception as e:
            print(f"Code Generation Error: {e}")
            return None

    def analyze_image(self, image_path, question):
        """
        Uses a vision model to analyze an image (like a screenshot).
        """
        import base64
        
        try:
            with open(image_path, "rb") as img_file:
                b64_img = base64.b64encode(img_file.read()).decode('utf-8')
                
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question + "\\nOutput your answer with an emotion tag like [EMOTION: NEUTRAL] at the beginning."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
                    ]
                }
            ]
            
            # Use Llama 3.2 Vision Model available on HuggingFace Free Tier (usually)
            response = self.client.chat_completion(
                model="meta-llama/Llama-3.2-11B-Vision-Instruct",
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[EMOTION: SAD] I encountered an error while trying to see your screen: {e}"
