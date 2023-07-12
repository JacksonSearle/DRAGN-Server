import json

def query_model(_, expected_structure):
    data = {}
    for key, value_type in expected_structure.items():
        if value_type == str:
            data[key] = "default"
        elif value_type == int:
            data[key] = 0
        elif value_type == bool:
            data[key] = False
        else:
            data[key] = None  # set value to None if type is not str, int, or bool
    return json.dumps(data)
