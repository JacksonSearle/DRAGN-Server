import json
import time
import os.path

def pathfinding(dest_x, dest_y, dest_z, x, y, z):
    # Calculate the difference between current position and destination
    dx = dest_x - x
    dy = dest_y - y
    dz = dest_z - z
    if dx == 0 and dy == 0 and dz == 0:
        return x, y, z
    largest = max(abs(dx), abs(dy), abs(dz))
    if abs(dx) == largest:
        if dx > 0:
            x += 1
        else:
            x -= 1
    elif abs(dy == largest):
        if dy > 0:
            y += 1
        else:
            y -= 1
    else:
        if dz > 0:
            z += 1
        else:
            z -= 1

    return x, y, z



def update():
    # Reading a JSON file
    with open('game_info/to_client.json', 'r') as file:
        s_data = json.load(file)
    with open('game_info/to_server.json', 'r') as file:
        c_data = json.load(file)

    # Modifying data
    for s_agent, c_agent in zip(s_data['agents'], c_data['agents']):
        dest_x, dest_y, dest_z = s_agent['destination']['x'], s_agent['destination']['y'], s_agent['destination']['z']
        x, y, z = c_agent['position']['x'], c_agent['position']['y'], c_agent['position']['z']
        x, y, z = pathfinding(dest_x, dest_y, dest_z, x, y, z)
        c_agent['position'] = {"x": x, "y": y, "z": z}

    # Writing to a JSON file
    with open('game_info/to_server.json', 'w') as file:
        json.dump(c_data, file)

while(True):
    # Check every _ seconds
    time.sleep(1)
    update()

# Example to_server in case you write over it
# {"agents": [{"name": "Frank", "position": {"x": 44, "y": 10, "z": 10}}, {"name": "Bob", "position": {"x": 10, "y": 10, "z": 10}}, {"name": "Alice", "position": {"x": 10, "y": 10, "z": 10}}]}

# Example to_client in case you don't have destinations or write over it
# {"stop": true, "agents": [{"name": "Frank", "status": null, "destination": {"x": 100, "y": 10, "z": 10}, "conversation": null}, {"name": "Bob", "status": null, "destination": {"x": 10, "y": 10, "z": 10}, "conversation": null}, {"name": "Alice", "status": null, "destination": {"x": 10, "y": 10, "z": 10}, "conversation": null}]}