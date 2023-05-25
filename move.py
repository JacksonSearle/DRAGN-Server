import json
import time
import os.path

def pathfinding(dest_x, dest_y, x, y):
    # Calculate the difference between current position and destination
    dx = dest_x - x
    dy = dest_y - y
    if dx == 0 and dy == 0:
        return x, y
    
    if abs(dx) > abs(dy):
        if dx > 0:
            x += 1
        else:
            x -= 1
    else:
        if dy > 0:
            y += 1
        else:
            y -= 1

    return x, y


def update():
    # Reading a JSON file
    with open('agent_info.json', 'r') as file:
        data = json.load(file)
        # `data` now contains the parsed JSON data

    # Modifying data
    for agent in data['agents']:
        dest_x, dest_y = agent['destination']
        x, y = agent['position']
        x, y = pathfinding(dest_x, dest_y, x, y)
        agent['position'] = [x, y]

    # Writing to a JSON file
    with open('agent_info.json', 'w') as file:
        json.dump(data, file)
        # The `data` dictionary is written to the file in JSON format


file = 'agent_info.json'
last_modified = os.path.getmtime(file)

while(True):
    # Check every _ seconds
    time.sleep(1)
    current_modified = os.path.getmtime(file)
    if current_modified > last_modified:
        update()
        current_modified = os.path.getmtime(file)
        last_modified = current_modified
