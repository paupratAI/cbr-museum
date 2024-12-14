import ollama
import sqlite3

class Llama:
    def __init__(self, model_name='llama3.2'):
        self.model_name = model_name

    def run_llm(self, answers):
        system_prompt = (
            "You will receive a list of user-provided answers. "
            "Analyze these answers and provide a comprehensive summary that captures the key points and common themes. "
            "Ensure your response is concise and informative."
        )

        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend({'role': 'user', 'content': answer} for answer in answers)

        response = ollama.chat(model=self.model_name, messages=messages)
        return response['message']['content']

class Interface:
    def __init__(self):
        self.llama = Llama()
        # Add check_same_thread=False here
        self.db = sqlite3.connect("data/database.db", check_same_thread=False)

    def get_id(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT group_id FROM abstract_problems ORDER BY group_id DESC LIMIT 1")
        group_id = cursor.fetchone()
        if group_id is None:
            return 1
        else:
            return group_id[0] + 1
