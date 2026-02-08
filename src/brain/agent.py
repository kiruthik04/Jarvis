import os
import subprocess
import sys
import traceback

class SystemAgent:
    def __init__(self, llm_client=None):
        self.llm = llm_client # Placeholder if we want to reuse the main LLM client later
        
    def execute_general_task(self, goal, history=None):
        """
        Generates and executes Python code to achieve a general system task.
        For this simplified version, we will mock the LLM code generation part since 
        the main 'ReasoningBrain' or 'TaskClassifier' usually handles the LLM interaction.
        
        However, to make this functional 'as requested', we need a way to get code from the LLM.
        Since I don't have direct access to the 'ReasoningBrain' instance here easily without circular imports,
        I will assume the caller passes the code or we use a separate simple generation method if needed.
        
        For now, let's implement a safe-guard wrapper that *would* execute code if we had it.
        """
        pass

    def run_generated_code(self, code_snippet):
        """
        Executes the provided Python code snippet.
        WARNING: This is dangerous and should be used with caution (User Confirmation recommended).
        """
        print(f"[SystemAgent] Executing code:\n{code_snippet}")
        
        try:
            # Wrap the code to capture output
            wrapped_code = f"""
import os
import shutil
import glob
import sys
import datetime

def task_execution():
{self._indent_code(code_snippet)}

task_execution()
"""
            # Execute in a separate process for safety/isolation
            result = subprocess.run(
                [sys.executable, "-c", wrapped_code],
                capture_output=True,
                text=True,
                timeout=60 # 1 minute timeout
            )
            
            output = result.stdout
            error = result.stderr
            
            if result.returncode == 0:
                return f"Task executed successfully.\nOutput:\n{output}"
            else:
                return f"Task execution failed.\nError:\n{error}\nOutput:\n{output}"
                
        except Exception as e:
            return f"System Agent Error: {e}"

    def _indent_code(self, code):
        """Helper to indent code for the wrapper function."""
        return "\n".join(["    " + line for line in code.split("\n")])

# NOTE: In a real integration, we would need the LLM to generate this code.
# Since 'ReasoningBrain' is the one holding the LLM connection (likely via an API or local model),
# we should probably add a method there to "generate_plan_code(goal)" and then pass it here.
