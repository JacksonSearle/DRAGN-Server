import random
import json

def query_model(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    return model(messages)

def model(messages):
    char = messages[1]["content"][0]
    if 'What 5 high-level insights can you infer from ' in messages[1]["content"]:
        return '1: Something insightful?\n2: Second insightful thing?\n3: Third insightful thing?\n4: Fourth insightful thing?\n5: Fifth insightful thing?'
    if '3 most salient high-level questions' in messages[1]["content"]:
        return 'Example question?\n Second example question?\n Third example question?'
    if 'single field, "state": string,' in messages[1]["content"]:
        return '{"state": "example state of object"}'
    if '"plan": string and "duration": int' in messages[1]["content"]:
        return '{"plan": "exampleminute plan", "duration": 5}'
    elif 'do this hour' in messages[1]["content"]:
        return 'Example plan for this hour'
    elif 'following summary of what he did yesterday' in messages[1]["content"]:
        return 'This person did something yesterday'
    elif '"choice"' in messages[1]["content"]:
        return '{"choice": 0}'
    elif char == 'O':
        number = random.randint(1, 10)
        return f'{number}'
    elif char == 'H':
        return "they are highly dedicated to research"
    elif char == 'G':
        return "This person was talking about something. <insert dialogue history here>"
    elif messages[1]["content"][-1] == 's': 
        number = random.randint(0, 1)
        duration = random.randint(5,15)
        react = number == 0
        message = "this person is interacting with the object"
        data = {
            "react": react,
            "interact": message,
            "duration": duration
        }
        json_string = json.dumps(data)
        return json_string
    elif messages[1]["content"][-1] == '?':
        return f'{{"continue_conversation": true, "response": "Something interesting"}}'
