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
        dest_x, dest_y, dest_z = s_agent['destination']
        x, y, z = c_agent['position']
        x, y, z = pathfinding(dest_x, dest_y, dest_z, x, y, z)
        c_agent['position'] = [x, y, z]

    # Writing to a JSON file
    with open('game_info/to_server.json', 'w') as file:
        json.dump(c_data, file)

while(True):
    # Check every _ seconds
    time.sleep(1)
    update()

# Example to_server in case you write over it
# {"agents": [{"name": "Frank", "position": [0, 1, 1]}, {"name": "Bob", "position": [0, 0, 1]}, {"name": "Alice", "position": [0, 0, 0]}]}

# Example to_client in case you don't have destinations or write over it
# {"stop": true, "agents": [{"name": "Frank", "status": null, "destination": [10, 10, 10], "conversation": null}, {"name": "Bob", "status": null, "destination": [10, 10, 10], "conversation": null}, {"name": "Alice", "status": null, "destination": [10, 10, 10], "conversation": null}]}