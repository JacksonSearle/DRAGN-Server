import time
import json
import config

if config.MODE == 'debugging':
    from debugging_model import query_model  # Import for debugging mode
elif config.MODE == 'testing':
    from testing_model import query_model  # Import for testing mode

def valid_json(json_str, expected_structure):
    start_index = json_str.find('{')
    end_index = json_str.rfind('}') + 1
    json_str = json_str[start_index:end_index]

    try:
        data = json.loads(json_str)
    except ValueError as e:
        return False

    for key, value_type in expected_structure.items():
        if key not in data:
            return False, json_str #, f"Missing key: {key}"
        if isinstance(value_type, list):  # special handling for lists
            if not isinstance(data[key], list):
                return False, json_str #, f"Incorrect type for key: {key}. Expected a list, but got {type(data[key])}."
            if not all(isinstance(i, value_type[0]) for i in data[key]):
                return False, json_str #, f"Incorrect type for elements in key: {key}. Expected {value_type[0]}, but got different type."
        else:  # for non-lists, we can directly use isinstance
            if not isinstance(data[key], value_type):
                return False, json_str #, f"Incorrect type for key: {key}. Expected {value_type}, but got {type(data[key])}."
    return True, json_str

def prompt_until_success(prompt, expected_structure):
    response_text = query_model(prompt, expected_structure)
    valid_answer, json_str = valid_json(response_text, expected_structure)
    i = 0
    num_tries = 10
    while i < num_tries and not valid_answer:
        response_text = query_model(prompt, expected_structure)
        valid_answer, json_str = valid_json(response_text, expected_structure)
        i += 1
    if valid_answer:
        dictionary = json.loads(json_str)
        print(f'{dictionary}\n\n')
        return dictionary
    else:
        print(f'ERROR: FAILED {num_tries} times\nPrompt: {prompt}')
        return None

def format_time(curr_time):
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", curr_time)
    return formatted_time

def get_timeofday(curr_time):
    return curr_time.tm_hour*100 + curr_time.tm_min

def increase_time(curr_time, seconds):
    new_time = time.mktime(curr_time) + seconds
    return time.localtime(new_time)

def set_start_time(year, month, day, hour, minute, second):
    start_time = time.struct_time((year, month, day, hour, minute, second, 1, 1, 0))
    return start_time

def time_prompt(curr_time):
    formatted_time = "It is " + time.strftime("%B %d, %Y, %I:%M %p.", curr_time)
    return formatted_time