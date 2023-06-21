import random
import json

def model(messages):
    char = messages[1]["content"][0]
    if char == 'O':
        number = random.randint(1, 10)
        return f'{number}'
    elif char == 'H':
        return "they are highly dedicated to research"
    elif char == 'G':
        return "This person was talking about something. <insert dialogue history here>"
    elif messages[1]["content"][-1] == 't': 
        number = random.randint(0, 1)
        react = number == 0
        message = "this person is interacting with the object"
        data = {
            "react": react,
            "message": message
        }
        json_string = json.dumps(data)
        return json_string
    elif messages[1]["content"][-1] == '?':
        return f'{{"continue_conversation": true, "response": "Something interesting"}}'
