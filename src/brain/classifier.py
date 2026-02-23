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
        task_type_match = re.search(r"Task Type:\s*([A-Z_]+)", text, re.IGNORECASE)
        if task_type_match:
            extracted_type = task_type_match.group(1).upper()
            
            # Map known intents to SYSTEM_ACTION if LLM forgets the wrapper
            system_intents = ["SHOW_WIFI_NETWORKS", "CHANGE_WIFI_NETWORK", "OPEN_APPLICATION", "VOLUME_UP", "VOLUME_DOWN", "VOLUME_MUTE", "TAKE_SCREENSHOT"]
            
            # Whitelist valid task types
            valid_types = [
                "SYSTEM_ACTION", 
                "WEB_SEARCH", 
                "THINK_AND_ANSWER", 
                "OFFICE_ACTION", 
                "MEETING_MODE", 
                "GENERAL_TASK",
                "MEMORY_ACTION",
                "AUTOMATION_ACTION",
                "ANALYZE_SCREEN",
                "EMAIL_ACTION"
            ]
            
            if extracted_type in valid_types:
                parsed["task_type"] = extracted_type
            elif extracted_type in system_intents:
                # Fallback: Treat as SYSTEM_ACTION
                parsed["task_type"] = "SYSTEM_ACTION"
                parsed["intent"] = extracted_type.lower()
            else:
                parsed["task_type"] = "UNKNOWN"
        else:
            parsed["task_type"] = "UNKNOWN"

        # Extract Confidence
        confidence_match = re.search(r"Confidence:\s*([0-9.]+)", text)
        if confidence_match:
            parsed["confidence"] = float(confidence_match.group(1))
        
        # --- PARSING PER TASK TYPE ---

        # 1. SYSTEM_ACTION & OFFICE_ACTION & AUTOMATION_ACTION (Shared structure: Intent + Parameters)
        if parsed["task_type"] in ["SYSTEM_ACTION", "OFFICE_ACTION", "AUTOMATION_ACTION"]:
            # Extract Intent
            if "intent" not in parsed:
                intent_match = re.search(r"Intent:\s*(.+)", text)
                if intent_match:
                    parsed["intent"] = intent_match.group(1).strip()
            
            # Extract Parameters
            params = {}
            param_matches = re.finditer(r"-\s*(.+?):\s*(.+)", text)
            for match in param_matches:
                params[match.group(1).strip()] = match.group(2).strip()
            parsed["parameters"] = params

        # 2. MEETING_MODE (Intent only)
        elif parsed["task_type"] == "MEETING_MODE":
             intent_match = re.search(r"Intent:\s*(.+)", text)
             if intent_match:
                parsed["intent"] = intent_match.group(1).strip()

        # 3. MEMORY_ACTION
        elif parsed["task_type"] == "MEMORY_ACTION":
             intent_match = re.search(r"Intent:\s*(.+)", text)
             if intent_match:
                parsed["intent"] = intent_match.group(1).strip()
             
             # Extract Parameters (key/value)
             params = {}
             param_matches = re.finditer(r"-\s*(.+?):\s*(.+)", text)
             for match in param_matches:
                 params[match.group(1).strip()] = match.group(2).strip()
             parsed["parameters"] = params

        # 4. GENERAL_TASK (Goal)
        elif parsed["task_type"] == "GENERAL_TASK":
            goal_match = re.search(r"Goal:\s*(.+)", text, re.DOTALL)
            if goal_match:
                parsed["goal"] = goal_match.group(1).strip()

        # 5. WEB_SEARCH (Query)
        elif parsed["task_type"] == "WEB_SEARCH":
            query_match = re.search(r"Search Query:\s*(.+)", text)
            if query_match:
                parsed["query"] = query_match.group(1).strip()

        # 6. THINK_AND_ANSWER (Answer)
        elif parsed["task_type"] == "THINK_AND_ANSWER":
            # Answer is everything after "Answer:"
            answer_match = re.search(r"Answer:\s*(.+)", text, re.DOTALL)
            if answer_match:
                parsed["answer"] = answer_match.group(1).strip()

        # 7. ANALYZE_SCREEN (Question)
        elif parsed["task_type"] == "ANALYZE_SCREEN":
            question_match = re.search(r"Question:\s*(.+)", text, re.DOTALL)
            if question_match:
                parsed["question"] = question_match.group(1).strip()
            else:
                parsed["question"] = "What is currently shown on my screen?"

        # 8. EMAIL_ACTION (Intent + Parameters)
        elif parsed["task_type"] == "EMAIL_ACTION":
            intent_match = re.search(r"Intent:\s*(.+)", text)
            if intent_match:
                parsed["intent"] = intent_match.group(1).strip()
            params = {}
            param_matches = re.finditer(r"-\s*(.+?):\s*(.+)", text)
            for match in param_matches:
                params[match.group(1).strip()] = match.group(2).strip()
            parsed["parameters"] = params

        parsed["raw_output"] = text
        print(f"[DEBUG] Parsed classification: {parsed}")
        return parsed
