from util import *
from agent import Agent
from memory import Memory
from tree import get_all_nodes, build_tree, places
from character_sheets import character_sheets

class Game:
    def __init__(self, time_step):
        self.time_step = time_step
        self.time = set_start_time(2023, 5, 24, 6, 0, 0)
        self.root = build_tree(places)
        self.places = get_all_nodes(self.root) # These are all visitable places
        self.agents = self.make_agents()
        self.make_agent_info()
    
    def make_agents(self):
        agents = []
        for character_sheet in character_sheets:
            agents.append(Agent(character_sheet))
        return agents

    def make_agent_info(self):
        agents = []
        for agent in self.agents:
            agents.append(
                {
                    'name': agent.name,
                    'position': [agent.x, agent.y],
                    'destination': agent.destination
                }
            )

    def update_agents(self):
        increase_time(self.time, self.time_step)
        for agent in self.agents:
            self.update_agent(agent)


    def update_agent(self, agent):
        # Percieve the world around them
        for place in self.places:
            if agent.is_within_range(place.x, place.y):
                # Make an observation for that thing
                memory = Memory(self.time, place.description())
                agent.memory_stream.append(memory)
                # Choose whether or not to react to each observation
                # if agent.react(memory):
