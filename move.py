import json
import time

def pathfinding(dest_x, dest_y, dest_z, x, y, z, step=100):
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
        data = json.load(file)
    with open('game_info/to_server.json', 'r') as file:
        front_data = json.load(file)

    # Modifying data
    for agent, front_agent in zip(data['agents'], front_data['agents']):
        dest_x, dest_y, dest_z = agent['destination']['location']['x'], agent['destination']['location']['y'], agent['destination']['location']['z']
        x, y, z = front_agent['position']['x'], front_agent['position']['y'], front_agent['position']['z']
        x, y, z = pathfinding(dest_x, dest_y, dest_z, x, y, z)
        front_agent['position'] = {"x": x, "y": y, "z": z}

    # Writing to a JSON file
    with open('game_info/to_server.json', 'w') as file:
        json.dump(front_data, file)

while(True):
    # Check every _ seconds
    time.sleep(1)
    update()

# Example to_server in case you write over it
# {"agents": [{"name": "Frank", "position": {"x": 44, "y": 10, "z": 10}}, {"name": "Bob", "position": {"x": 10, "y": 10, "z": 10}}, {"name": "Alice", "position": {"x": 10, "y": 10, "z": 10}}]}

# Example to_client in case you don't have destinations or write over it
# {"stop": true, "agents": [{"name": "Frank", "status": null, "destination": {"x": 100, "y": 10, "z": 10}, "conversation": null}, {"name": "Bob", "status": null, "destination": {"x": 10, "y": 10, "z": 10}, "conversation": null}, {"name": "Alice", "status": null, "destination": {"x": 10, "y": 10, "z": 10}, "conversation": null}]}
