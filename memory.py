import re
import config
from sentence_embed import embed

if config.MODE == 'debugging':
    from debugging_model import model  # Import for debugging mode
elif config.MODE == 'testing':
    from testing_model import model  # Import for testing mode

class Memory:
    def __init__(self, time, description, type="Observation"):
        self.time = time
        self.last_access = time
        self.description = description
        self.type = type
        self.emb = embed(description)
        self.importance = self.generate_importance()

    def generate_importance(self):
        # prompt chatgpt
        prompt = f'On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory. Give no explanation. Only print the number. Memory: {self.description}'
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        output = model(messages)
        start, end = find_integer_in_string(output)
        number = int(output[start:end+1])
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

    