import ollama
import sqlite3
from typing import List
from recommender import Recommender
from dotenv import load_dotenv
import openai
import os

class Llama:
    def __init__(self, model_name='llama3.2'):
        self.model_name = model_name
        self.chat = 'openai'

    def run_llm(self, answers: List[str], prompt=1):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        client = openai.Client(api_key=api_key)
        if prompt == 1:
            system_prompt = ("""
                You are a museum route planning assistant that processes a user's responses to a series of questions. The user’s answers may be imprecise or informal. Your job is to produce a clean, standardized list of values derived from their answers. The final output should be a structured list containing one cleaned value per question, in order.

                You have received the following 8 answers (in this specific order):
                1. How many people will join the visit? (user might say "There are four of us" -> interpret as an integer, e.g. 4)
                2. Are there children under 12? (user may say "no kids", "yes, a toddler" -> output "yes" or "no"). You should write your answer in binary, so 0 for "no" and 1 for "yes".
                3. Would you like a guided visit? (interpret variations like "I think so" as "yes"). You should write your answer in binary, so 0 for "no" and 1 for "yes".
                4. How many experts are in the group? (if user says "just me is an expert" -> interpret as an integer, e.g. 1)
                5. How many museums have you visited before? (convert responses like "I've seen a couple" to an integer approximation, e.g. 2)
                6. Enter the year of your favorite art period (1000 to 1900): (if user says "around fifteen hundred" -> interpret as 1500)
                7. Which theme do you prefer? Possible themes and their labels are:
                - Emotional: Sadness, Joy, Nostalgia, Hope, Love, Despair
                - Historical: Battles and Wars, Conquests, Revolutions, Antiquity, Monarchies, Colonizations
                - Religious: Christianity, Islam, Greek Mythology, Roman Mythology, Egyptian Religion, Buddhism
                - Natural: Landscapes, Fauna, Flora, Maritime Scenes, Meteorological Phenomena, Mountains and Valleys
                - Mystical: Magic, Occult, Astrology, Alchemy, Mysticism, Ancient Rituals

                If the user’s chosen theme isn't explicitly listed, pick the closest one based on semantic similarity. For example, if they say "spooky ancient rituals," that fits "Mystical" or "Ancient Rituals" directly under Mystical.

                8. What's your favorite author? 
                If the user chooses an author not in the dataset, pick the closest match from a known set of authors
                            
                    Pablo Picasso, China, Georgia O'Keeffe, Claude Monet, Giovanni Battista, James McNeill, Japan, Edgar Degas, Édouard Manet, Paul Cezanne, Marc Chagall, Roy Lichtenstein, Henri Matisse, Jasper Johns, Frank Lloyd, Diego Rivera, Artist unknown, Pierre-Auguste Renoir, Henri de, Francisco José, Arshile Gorky, Paul Gauguin, India Tamil, Winslow Homer, Vincent van, Claude Lorrain, Andy Warhol, India Rajasthan,, Jean-Honoré Fragonard, George Inness, Korea, Willem de, Eugène Delacroix, Fernand Léger, After a, Ivan Albright, Spanish, Rembrandt van, Frederic Remington, Design attributed, Attributed to, Georges Braque, Vija Celmins, Bruce Nauman, Meissen Porcelain, Salvador Dalí, Edvard Munch, Emma Stebbins, Rudolph Schindler, Meindert Hobbema

                9. Group Description: (user might say "We are a group of friends" -> interpret as a string, e.g. "group of friends"). You do not need to process this answer, just keep it as a string and add it to the final output.
                            
                
                Your task:
                - Parse each answer to extract a clean, normalized value.
                - Handle approximate or vague answers by making a reasonable assumption (e.g., "a few" -> 3).
                - If a theme or author isn't directly listed, pick the closest known category or name.
                - Return the final result as a simple JSON list corresponding to the answers in order.
                - Do not explain your reasoning or provide extra commentary in the final output. Only output the cleaned list of values.

                Your final answer should strictly be the cleaned values in a JSON list, nothing else. From response 1 to 9, the output should be in the following format: [1, "yes", "yes", 1, 2, 1500, "Mystical", "Salvador Dalí", "group of friends"] for example.
            """)
        else:
            system_prompt = (""" You are a museum route planning assistant that processes a user's responses to a series of three questions. The user’s answers may be imprecise or informal. Your job is to produce a clean, standardized list of values derived from their answers. The final output should be a structured list containing one cleaned value per question, in order.

                You have received the following 3 answers (in this specific order):

                How many days would you like to visit? (1 to 7):
                The user might say something vague like "Maybe a couple of days" -> interpret as an integer (e.g., 2).
                How many daily hours will you dedicate to the visit? (1 to 12):
                The user may say "a few hours" or "about three hours" -> interpret as an integer (e.g., 3).
                Is there someone with reduced mobility? (yes/no):
                The user may say "No, I think we are all good" -> output "no".
                If the user says something like "My grandma has trouble walking" -> interpret as "yes". You should write your answer in binary, so 0 for "no" and 1 for "yes".
                Your task:

                Parse each answer to extract a clean, normalized value.
                Handle approximate or vague answers by making a reasonable assumption (e.g., "a few" -> 3).
                For the first two questions, the output should be an integer number.
                For the third question, output should be either the boolean values true or false.
                Return the final result as a simple JSON list corresponding to the answers in order.
                Do not explain your reasoning or provide extra commentary in the final output. Only output the cleaned list of values.
                For example, if the user said:

                "I guess maybe three days"
                "just a couple of hours"
                "I think we have someone who can't walk well" Your output could be: [3, 2, true]
                No additional text outside the JSON list should be returned. """)


        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend({'role': 'user', 'content': answer} for answer in answers)

        if self.chat == 'openai':
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=messages,
            )

            return response.choices[0].message.content

        response = ollama.chat(model=self.model_name, messages=messages)
        return response['message']['content']

class Interface:
    def __init__(self):
        self.llama = Llama()
        self.recommender = Recommender(db_path="data/database.db", clustering=False)
        self.db = sqlite3.connect("data/database.db", check_same_thread=False)

    def get_id(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT group_id FROM cases ORDER BY group_id DESC LIMIT 1")
        group_id = cursor.fetchone()
        self.id = 1 if group_id is None else group_id[0] + 1
        return self.id
