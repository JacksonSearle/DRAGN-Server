import json
import time
import os.path

def pathfinding(dest_x, dest_y, dest_z, x, y, z, step=300):
    # Calculate the difference between current position and destination
    dx = dest_x - x
    dy = dest_y - y
    dz = dest_z - z
    if dx == 0 and dy == 0 and dz == 0:
        return x, y, z
    largest = max(abs(dx), abs(dy), abs(dz))
    if abs(dx) == largest:
        if dx > 0:
            x += min(dx, step)
        else:
            x -= min(abs(dx), step)
    elif abs(dy) == largest:
        if dy > 0:
            y += min(dy, step)
        else:
            y -= min(abs(dy), step)
    else:
        if dz > 0:
            z += min(dz, step)
        else:
            z -= min(abs(dz), step)

    return x, y, z



def update():
    # Reading a JSON file
    with open('game_info/to_client.json', 'r') as file:
        s_data = json.load(file)
    with open('game_info/to_server.json', 'r') as file:
        c_data = json.load(file)

    # Modifying data
    for s_agent, c_agent in zip(s_data['agents'], c_data['agents']):
        try:
            dest_x, dest_y, dest_z = s_agent['destination']['location']['x'], s_agent['destination']['location']['y'], s_agent['destination']['location']['z']
        except:
            print(f'S_DATA\n\n{s_data}\n\nS_AGENT\n\n{s_agent}')
        x, y, z = c_agent['position']['x'], c_agent['position']['y'], c_agent['position']['z']
        x, y, z = pathfinding(dest_x, dest_y, dest_z, x, y, z)
        if s_data['spawn']:
            c_agent['position'] = {"x": s_data['spawn_location'], "y": s_data['spawn_location'], "z": s_data['spawn_location']}
        else:
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