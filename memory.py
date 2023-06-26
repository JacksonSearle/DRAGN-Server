import re
import json
from util import *
import config
from sentence_embed import embed

if config.MODE == 'debugging':
    from debugging_model import query_model  # Import for debugging mode
elif config.MODE == 'testing':
    from testing_model import query_model  # Import for testing mode

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
        output = brackets(output)
        if output == "error":
            output = '{"importance": 5}'
        data = json.loads(output)
        number = data["importance"]

        # Check out of bounds numbers
        if number > 10:
            number = 10
        if number < 1:
            number = 1

        return number
    
    def format_description(self):
        return f'Observation: {self.description}'

def find_integer_in_string(input_string):
    match = re.search(r'\d+', input_string)  # searches for the first contiguous integer
    if match is not None:  # if a match is found
        return (match.start(), match.end()-1)  # returns the starting and ending indices
    else:
        return None  # returns None if no integer is found

    