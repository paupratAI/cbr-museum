import ollama

class Llama:
    def __init__(self, model_name='llama3.2'):
        self.model_name = model_name

    def run_llm(self, answers):
        # Define the system prompt to instruct the model
        system_prompt = (
            "You will receive a list of user-provided answers. "
            "Analyze these answers and provide a comprehensive summary that captures the key points and common themes. "
            "Ensure your response is concise and informative."
        )
        
        # Prepare the messages for the chat, starting with the system message
        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend({'role': 'user', 'content': answer} for answer in answers)
        
        # Call the Ollama chat API
        response = ollama.chat(model=self.model_name, messages=messages)
        
        # Extract and return the content of the assistant's response
        return response['message']['content']