from huggingface_hub import InferenceClient
import re
from ..config import Config
from .prompts import CLASSIFIER_SYSTEM_PROMPT

class TaskClassifier:
    def __init__(self):
        self.client = InferenceClient(token=Config.HUGGINGFACE_API_TOKEN)
        # Using a small, fast model for classification
        self.model = "meta-llama/Meta-Llama-3-8B-Instruct" 

    def classify(self, user_input):
        messages = [
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": f"User Input:\n\"{user_input}\""}
        ]

        try:
            response = self.client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.0
            )
            result_text = response.choices[0].message.content
            return self._parse_output(result_text)
        except Exception as e:
            print(f"Error calling HF Classifier: {e}")
            return {"task_type": "ERROR", "reason": str(e)}

    def _parse_output(self, text):
        """
        Parses the structured text output into a dictionary.
        """
        parsed = {}
        
        # Extract Task Type
        # Extract Task Type
        # Updated regex to be more flexible and catch if LLM hallucinates the intent as the type
        task_type_match = re.search(r"Task Type:\s*([A-Z_]+)", text, re.IGNORECASE)
        if task_type_match:
            extracted_type = task_type_match.group(1).upper()
            
            # Map known intents to SYSTEM_ACTION if LLM forgets the wrapper
            system_intents = ["SHOW_WIFI_NETWORKS", "CHANGE_WIFI_NETWORK", "OPEN_APPLICATION", "VOLUME_UP", "VOLUME_DOWN", "VOLUME_MUTE", "TAKE_SCREENSHOT"]
            
            if extracted_type in ["SYSTEM_ACTION", "WEB_SEARCH", "THINK_AND_ANSWER"]:
                parsed["task_type"] = extracted_type
            elif extracted_type in system_intents:
                # Fallback: Treat as SYSTEM_ACTION
                parsed["task_type"] = "SYSTEM_ACTION"
                parsed["intent"] = extracted_type.lower() # Auto-populate intent
            else:
                parsed["task_type"] = "UNKNOWN"
        else:
            parsed["task_type"] = "UNKNOWN"

        # Extract Confidence
        confidence_match = re.search(r"Confidence:\s*([0-9.]+)", text)
        if confidence_match:
            parsed["confidence"] = float(confidence_match.group(1))
        
        # Extract intent and parameters for SYSTEM_ACTION
        if parsed["task_type"] == "SYSTEM_ACTION":
            # Only look for intent if not already set by fallback
            if "intent" not in parsed:
                intent_match = re.search(r"Intent:\s*(.+)", text)
                if intent_match:
                    parsed["intent"] = intent_match.group(1).strip()
            
            params = {}
            param_matches = re.finditer(r"-\s*(.+?):\s*(.+)", text)
            for match in param_matches:
                params[match.group(1).strip()] = match.group(2).strip()
            parsed["parameters"] = params
            parsed["parameters"] = params

        # Extract search query for WEB_SEARCH
        elif parsed["task_type"] == "WEB_SEARCH":
            query_match = re.search(r"Search Query:\s*(.+)", text)
            if query_match:
                parsed["query"] = query_match.group(1).strip()

        # Extract answer for THINK_AND_ANSWER
        elif parsed["task_type"] == "THINK_AND_ANSWER":
            # Answer is everything after "Answer:"
            answer_match = re.search(r"Answer:\s*(.+)", text, re.DOTALL)
            if answer_match:
                parsed["answer"] = answer_match.group(1).strip()

        parsed["raw_output"] = text
        return parsed
