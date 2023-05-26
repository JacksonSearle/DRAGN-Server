import json
import time
from game import Game

if __name__ == "__main__":

    game_states = 100
    time_step = 1 # seconds
    game = Game(time_step=time_step)
    # Give original json to client
    data = game.initial_json()

    # Writing initial data to a JSON file
    with open('game_info/to_client.json', 'w') as file:
        json.dump(data, file)

    for i in range(game_states):
        # Reading a JSON file
        with open('game_info/to_server.json', 'r') as file:
            c_data = json.load(file)
        c_agents = c_data['agents']

        # Update the server agent's position
        if i != 0:
            for c_agent, s_agent in zip(c_agents, game.agents):
                s_agent.position = c_agent['position']

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
        
        # Delay the specified time
        # time.sleep(1)

    print('Done with simulation')