import re
import json
from util import *
from sentence_embed import embed

class Memory:
    def __init__(self, time, description, type="Observation"):
        self.time = time
        self.last_access = time
        self.description = description
        self.type = type
        self.emb = embed(description)
        self.importance = self.generate_importance()

    def generate_importance(self):
        # Prompt chatgpt
        prompt = f'On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory. Return your answer as a JSON object with one field, importance: int. Memory: {self.description}'
        output = query_model(prompt)

        # Turn it into a JSON
        expected_structure = {
            "importance": int,
        }
        dictionary = prompt_until_success(prompt, expected_structure)
        number = dictionary["importance"]

        # Check out of bounds numbers
        if number > 10:
            number = 10
        if number < 1:
            number = 1

        return number
    
    def format_description(self):
        return f'Observation: {self.description}'
