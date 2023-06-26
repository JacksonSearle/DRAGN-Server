import json
import time
from game import Game
# import cProfile

def update_world_tree():
    with open('world_tree.json', 'r') as file: places = json.load(file)
    with open('game_info/on_startup.json', 'r') as file: newLocations = json.load(file)
    for place in newLocations['allDestinations']:
        layer = places
        for n in range(len(place['namesId'])-1):
            if 'name' not in layer: 
                layer['name'] = place['namesId'][n]
                layer['position'] = None
                layer['children'] = []
            layer = layer['children']

            found = False
            for c in layer:
                if c['name'] == place['namesId'][n+1]: 
                    layer = layer[layer.index(c)]
                    found = True
            if not found: 
                layer.append({})
                layer = layer[-1]
            
        layer['name'] = place['namesId'][-1]
        layer['position'] = list(place['location'].values())
        if 'children' not in layer: layer['children'] = []
    
    with open('world_tree.json', 'w') as file: json.dump(places, file)

def gather_initial_data(game):
    # Give original json to client
    data = game.initial_json()
    with open('game_info/to_client.json', 'w') as file: json.dump(data, file)
    return data

def update_server_info(i, game):
    # Reading a JSON file
    with open('game_info/to_server.json', 'r') as file:
        c_data = json.load(file)
    c_agents = c_data['agents']

    # Update the server agent's position
    if i != 0:
        for c_agent, s_agent in zip(c_agents, game.agents):
            s_agent.position = c_agent['position']
    
def send_server_info(i, data, game, game_states):
    # Calculate the next step in the game
    game.update_agents()
    # Possibly end the game
    if i == game_states - 1:
        data['stop'] = True
        
    # Update our computed info
    game.update(data)

    # Writing to a JSON file
    with open('game_info/to_client.json', 'w') as file:
        json.dump(data, file)

def main():
    game_states = 60 # number of time steps
    time_step = 6000 # seconds
    update_world_tree()
    game = Game(time_step=time_step)
    data = gather_initial_data(game)

    for i in range(game_states):
        print(i)
        print(game.time)
        update_server_info(i, game)
        send_server_info(i, data, game, game_states)
        
        # Delay the specified time
        # time.sleep(1)

    print('Done with simulation')

main()