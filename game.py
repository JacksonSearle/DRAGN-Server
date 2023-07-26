from util import *
from multiprocessing import Pool
from pathlib import Path
import json
import pickle
from agent import Agent
from memory import Memory
from tree import build_tree
from character_sheets import character_sheets

from config import path
#from init_unreal import content_path

class Game:
    def __init__(self, time_step):
        self.time_step = time_step
        self.time = set_start_time(2023, 5, 24, 7, 0, 0)

        with open(Path(path + 'world_tree.json'), 'r') as file:
            self.root = build_tree(json.load(file))
        self.places = {}
        self.lookup_places(self.root)
        self.agents = self.make_agents()
        self.get_save_index()

    def lookup_places(self,node):
        self.places[node.path] = node
        if node.children:
            for child in node.children: self.lookup_places(child)
    
    def initial_json(self):
        data = {}
        data['save_index'] = self.save_index
        data['spawn'] = True
        data['agents'] = []
        for i, agent in enumerate(self.agents):
            data['agents'].append({})
            data['agents'][i]['name'] = agent.name
            data['agents'][i]['status'] = agent.status
            data['agents'][i]['destination'] = agent.destination.location
            data['agents'][i]['conversation'] = agent.conversation
            data['agents'][i]['spawn_location'] = agent.spawn.location
        return data
    
    def make_agents(self):
        agents = []
        for character_sheet in character_sheets:
            agents.append(Agent(character_sheet, self.time, self.places[character_sheet['spawn']]))
        return agents

    def update(self, data):
        for i, agent in enumerate(self.agents):
            data['agents'][i]['status'] = agent.status
            data['agents'][i]['destination'] = {"nameId": agent.destination.name, "location": agent.destination.location}
            data['agents'][i]['conversation'] = agent.conversation

    def update_agents(self):
        self.time = increase_time(self.time, self.time_step)
        for agent in self.agents:
            self.update_agent(agent)
        # with Pool(processes=10) as pool:
        #     pool.map(self.update_agent, self.agents)
        

    def update_agent(self, agent):
        timeofday = get_timeofday(self.time)
        if timeofday == agent.waking_hours["up"]: 
            agent.plan_day(self.time)
            self.execute_plan(agent)
        #Call reflection if agent is going to bed, or call hour/minute plans if during waking hours
        elif timeofday == agent.waking_hours["down"]: agent.reflect(self.time)
        elif agent.waking_hours["up"] < timeofday < agent.waking_hours["down"]:
            if not self.perceive_objects(agent):
                self.perceive_agents(agent)
            if agent.busy_time <= 0:
                agent.conversation = None
                if timeofday%100 == 0: agent.plan_hour(self.time)
                else: agent.plan_next(self.time)
                self.execute_plan(agent)
            else: agent.busy_time -= self.time_step

    def perceive_objects(self,agent):
        perceived = []
        choices = []
        #TODO: Front-end determines the objects seen by the agent
        for place in self.places.values():
            if agent.is_within_range(place.location):
                # Make an observation for that thing if its state is different or newly observed
                if place.name not in agent.last_observed or agent.last_observed[place.name] != place.state:
                    agent.last_observed[place.name] = place.state
                    description = f'{place.name} is {place.state}'
                    memory = Memory(self.time, description)
                    agent.add_memory(memory)
                    perceived.append(memory)
                    choices.append(place)
        # Choose whether or not to react to each observation
        if agent.conversation == None and len(perceived) > 0:
            react, interact = agent.react(self.time, perceived)
            if react>=0: 
                agent.status = interact
                self.execute_plan(agent, choices[min(react, len(choices)-1)])
                return True
        return False
    
    def perceive_agents(self,agent):
        for other_agent in self.agents:
            # Make sure an agent isn't talking to themselves
            if agent is not other_agent and agent.is_within_range(other_agent.location):
                # Make both agents see each other
                #TODO: prompts do not consistently produce statuses that fit with this sentence structure, e.g "Bob is check on Alice", "Alice is Alice would chat"
                description = f'{other_agent.name}\'s plan is to {other_agent.status}'
                memory = Memory(self.time, description)
                agent.memory_stream.append(memory)
                
                # Choose whether or not to react to each observation
                react, interact = agent.react(self.time, [memory])
                if react>=0:
                    agent.status = interact
                    # make a memory for the person they are talking to
                    description = agent.status
                    memory = Memory(self.time, description)
                    other_agent.add_memory(memory)
                    other_agent.status = description
                    # generate dialogue
                    self.conversation(agent, other_agent)

    
    def execute_plan(self,agent,destination=None):
        if agent.destination: agent.destination.state = "idle"
        if destination: agent.destination = destination
        else: agent.destination = self.choose_location(agent)
        prompt = f'{agent.name} is {agent.status} at the {agent.destination.name}. Generate a JSON dictionary object with a single field, "state": string, which describes the state the {agent.destination.name} is in.'
        expected_structure = {
            "state": str,
        }
        dictionary = prompt_until_success(prompt, expected_structure)
        agent.destination.state = dictionary['state']
    
    def choose_location(self,agent,root=None):
        if root: location = root
        else:
            #Remaining at current location is an option at the first level of traversal
            location = agent.destination
            root = self.root

        choices = f'0: {location.name}'
        for c in range(len(root.children)): 
            s = f'{c+1}: {root.children[c].name}'
            choices = '\n'.join([choices,s])
        query = f'Given the place(s) above, write a JSON dictionary object with "choice": int. Choice should be one of the indices shown above. Make its value the index of the place which is the most reasonable for {agent.name} to do the following activity: {agent.status}'
        prompt = '\n'.join([choices, query])
        expected_structure = {
            "choice": int,
        }
        dictionary = prompt_until_success(prompt, expected_structure)
        index = dictionary["choice"]
        
        if not 1 <= index <= len(root.children): return location
        location = root.children[index-1]
        return self.choose_location(agent,location) if location.children else location
        

    def conversation(self, agent, other_agent):
        # Every conversation will be 5 minutes
        agent.busy_time = 5 * 60
        other_agent.busy_time = 5*60
        conversation = agent.converse(other_agent, self.time)
        # TODO: could we set their destination to a halfway point between the agents?
        agent.conversation, other_agent.conversation = conversation, conversation
        agent.destination.location, other_agent.destination.location = None, None

        conversation_description = self.create_conversation_description(conversation)
        shared_memory = Memory(self.time, conversation_description)
        agent.add_memory(shared_memory)
        other_agent.add_memory(shared_memory)
    
    def create_conversation_description(self, dialogue_history):
        message = f'Generate a one sentence description of the following dialogue history:\n {dialogue_history}\n\nReturn a json object with one field "description": str'
        expected_structure = {
            "description": str
        }
        dictionary = prompt_until_success(message, expected_structure)
        return dictionary["description"]
    
    def get_save_index(self):
        self.save_index = get_index()

    def save(self):
        pickle_file_name = path + f'saved_games/save_state_{self.save_index}.pkl'
        with open(pickle_file_name, 'wb') as file:
            pickle.dump(self, file)
