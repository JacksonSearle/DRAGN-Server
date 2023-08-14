import json
import pickle
import util
from game import Game
from pathlib import Path
# import cProfile
#from init_unreal import content_path
from config import path

def update_world_tree():
    with open(Path(path + 'world_tree.json'), 'r') as file: known = json.load(file)
    with open(Path(path + 'game_info/on_startup.json'), 'r') as file: newLocations = json.load(file)
    for place in newLocations['allDestinations']:
        layer = known
        for n in range(len(place['namesId'])-1):
            if 'name' not in layer: 
                layer['name'] = place['namesId'][n]
                layer['position'] = None
                layer['children'] = []
            layer = layer['children']

            found = False
            for entry in layer:
                if entry['name'] == place['namesId'][n+1]: 
                    layer = layer[layer.index(entry)]
                    found = True
            if not found: 
                layer.append({'children': []})
                layer = layer[-1]
            
        layer['name'] = place['namesId'][-1]
        layer['position'] = list(place['location'].values())
    
    with open(Path(path + 'world_tree.json'), 'w') as file: json.dump(known, file)

def gather_initial_data(game):
    # Give original json to client
    data = game.initial_json()
    with open(Path(path + 'game_info/to_client.json'), 'w') as file: json.dump(data, file)
    return data

def update_server_info(game, do_pos=True):
    with open(Path(path + 'game_info/to_server.json'), 'r') as file:
        front_data = json.load(file)
    if front_data['save']:
            game.save()
            return True
    front_agents = front_data['agents']

    for front_agent, agent in zip(front_agents, game.agents):
        agent.observed_objects = front_agent['objects']
        agent.observed_agents = front_agent['agents']
    return False
    
def send_server_info(data, game):
    game.update_agents()
        
    game.update(data)

    with open(Path(path + 'game_info/to_client.json'), 'w') as file:
        json.dump(data, file)

def load_game(time_step):
    with open(Path(path + 'game_info/to_server.json'), 'r') as file:
        front_data = json.load(file)
    index = front_data['file_index']
    if index == -1:
        update_world_tree()
        game = Game(time_step=time_step)
    else:
        pickle_file_name = path + f'saved_games/save_state_{index}.pkl'
        with open(pickle_file_name, 'rb') as file:
            game = pickle.load(file)
    return game


    

def main():
    game_states = 20 # number of time steps
    time_step = 1800 # seconds

    game = load_game(time_step)
    game.save_index = util.get_index()
    data = gather_initial_data(game)

    for i in range(game_states):
        print(f'-------EPOCH: {i}------')
        if i > 0:
            data['spawn'] = False
        print(game.time)
        if update_server_info(game, i>0): break
        send_server_info(data, game)
        print()
    
    print('Done with simulation')

# main()
