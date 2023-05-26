import json
import time
from game import Game

if __name__ == "__main__":

    game_states = 100
    time_step = 1 # seconds
    game = Game(time_step=time_step)
    # # Give original json to client

    # # Reading a JSON file
    # with open('agent_info.json', 'r') as file:
    #     data = json.load(file)
    #     c_agents = data['agents']

    # # Update the client agents' status
    # data['stop'] = False
    # game.update(data)

    #TODO: Get initial JSON from server
    data = game.initial_json()

    # Writing initial data to a JSON file
    with open('agent_info.json', 'w') as file:
        json.dump(data, file)

    for i in range(game_states):
        # Reading a JSON file
        with open('agent_info.json', 'r') as file:
            data = json.load(file)
        c_agents = data['agents']

        if i != 0:
            # Update the server agent's position
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
        with open('agent_info.json', 'w') as file:
            json.dump(data, file)
        
        # Delay the specified time
        # time.sleep(1)
    print('Done with simulation')