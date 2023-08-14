import re
import json

def query_model(prompt, expected_structure):
    data = {}
    for key, value_type in expected_structure.items():
        if value_type == str:
            data[key] = "default"
        elif value_type == int:
            data[key] = 0
        elif value_type == bool:
            data[key] = False
        elif isinstance(value_type, list):  # handling for list type
            number = find_first_integer(prompt)
            if value_type[0] == str:
                # This one is hard coded for 3 salient questions, the rest are generalized
                data[key] = ["default" for _ in range(number)]
            elif value_type[0] == int:
                data[key] = [0 for _ in range(number)]
            elif value_type[0] == bool:
                data[key] = [False for _ in range(number)]
            else:
                data[key] = [None for _ in range(number)]
        else:
            data[key] = None  # set value to None if type is not str, int, or bool
    return json.dumps(data)


def find_first_integer(string):
    match = re.search(r'\d+', string)
    if match:
        return int(match.group())
    else:
        return 1