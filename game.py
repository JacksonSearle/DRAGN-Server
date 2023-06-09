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
        # Percieve the objects around them
        for place in self.places:
            if agent.is_within_range(place.x, place.y, place.z):
                # Make an observation for that thing
                memory = Memory(self.time, place.state)
                agent.memory_stream.append(memory)
                # Choose whether or not to react to each observation
                react, interact = agent.react(self.time, memory)
                if react:
                    agent.regenerate_plan()
                    agent.status = interact

        # Percieve the people around them
        for i, agent in enumerate(self.agents):
            for j, other_agent in enumerate(self.agents):
                # Make sure an agent isn't talking to themselves
                if i != j and agent.is_within_range(other_agent.x, other_agent.y, other_agent.z):
                    # Make both agents see eachother
                    description = f'{other_agent.name} is {other_agent.status}'
                    memory = Memory(self.time, description)
                    agent.memory_stream.append(memory)
                    
                    # Choose whether or not to react to each observation
                    react, interact = agent.react(self.time, memory)
                    if react:
                        # make a memory for the person they are talking to
                        description = f'{agent.name} is {agent.status}'
                        memory = Memory(self.time, description)
                        other_agent.memory_stream.append(memory)
                        # generate dialogue
                        self.conversation(agent, other_agent)
                        agent.regenerate_plan()
                        other_agent.regenerate_plan()
    
    def update(self, data):
        for i, agent in enumerate(self.agents):
            data['agents'][i]['status'] = agent.status
            data['agents'][i]['destination'] = agent.destination
            data['agents'][i]['conversation'] = agent.conversation
    
    def initial_json(self):
        data = {}
        data['stop'] = False
        data['agents'] = []
        for i, agent in enumerate(self.agents):
            data['agents'].append({})
            data['agents'][i]['name'] = agent.name
            data['agents'][i]['status'] = agent.status
            data['agents'][i]['destination'] = agent.destination
            data['agents'][i]['conversation'] = agent.conversation
        return data

    def conversation(self, agent, other_agent):
        pass