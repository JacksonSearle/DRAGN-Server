from util import *
from multiprocessing import Pool
from pathlib import Path
import json
from agent import Agent
from memory import Memory
from tree import get_all_nodes, build_tree
from character_sheets import character_sheets

import global_path
#from init_unreal import content_path

class Game:
    def __init__(self, time_step):
        self.time_step = time_step
        self.time = set_start_time(2023, 5, 24, 7, 0, 0)
        with open(Path(global_path.path + 'world_tree.json'), 'r') as file:
            self.root = build_tree(json.load(file))
        self.places = get_all_nodes(self.root)
        self.agents = self.make_agents()

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
    
    def make_agents(self):
        agents = []
        for character_sheet in character_sheets:
            agents.append(Agent(character_sheet, self.time))
        return agents

    def update(self, data):
        for i, agent in enumerate(self.agents):
            data['agents'][i]['status'] = agent.status
            data['agents'][i]['destination'] = agent.destination
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
        for place in self.places:
            if agent.is_within_range(place.x, place.y, place.z):
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
            if react > len(choices)-1:
                react = len(choices)-1
            if react!=-1: 
                agent.status = interact
                self.execute_plan(agent, choices[react])
                return True
        return False
    
    def perceive_agents(self,agent):
        for j, other_agent in enumerate(self.agents):
            # Make sure an agent isn't talking to themselves
            if agent is not other_agent and agent.is_within_range(other_agent.x, other_agent.y, other_agent.z):
                # Make both agents see each other
                #TODO: prompts do not consistently produce statuses that fit with this sentence structure, e.g "Bob is check on Alice", "Alice is Alice would chat"
                description = f'{other_agent.name}\'s plan is to {other_agent.status}'
                memory = Memory(self.time, description)
                agent.memory_stream.append(memory)
                
                # Choose whether or not to react to each observation
                react, interact = agent.react(self.time, [memory])
                if react:
                    agent.status = interact
                    # make a memory for the person they are talking to
                    description = f'{agent.name} is {agent.status}'
                    memory = Memory(self.time, description)
                    other_agent.add_memory(memory)
                    other_agent.status = description
                    # generate dialogue
                    self.conversation(agent, other_agent)

    
    def execute_plan(self,agent,object=None):
        if agent.object: agent.object.state = "idle"
        if object: agent.object = object
        else: agent.object = self.choose_location(agent)
        prompt = f'{agent.name} is {agent.status} at the {agent.object.name}. Generate a JSON dictionary object with a single field, "state": string, which describes the state the {agent.object.name} is in.'
        expected_structure = {
            "state": str,
        }
        dictionary = prompt_until_success(prompt, expected_structure)
        agent.object.state = dictionary['state']
        agent.destination = {"x":agent.object.x, "y":agent.object.y, "z":agent.object.z}
    
    def choose_location(self,agent,root=None):
        children = []
        if not root: 
            root = self.root
            if agent.object != None:
                children = [agent.object]
        children.extend(root.children)

        choices = ''
        for c in range(len(children)): 
            s = f'{c+1}: {children[c].name}'
            choices = '\n'.join([choices,s])
        query = f'Given the place(s) above, write a JSON dictionary object with "choice": int. Choice should be one of the indices shown above. Make its value the index of the place which is the most reasonable for {agent.name} to do the following activity: {agent.status}'
        prompt = '\n'.join([choices, query])
        expected_structure = {
            "choice": int,
        }
        dictionary = prompt_until_success(prompt, expected_structure)
        index = dictionary["choice"]

        location = root.children[index]
        if not location.children: return location
        return self.choose_location(agent,location)

    def conversation(self, agent, other_agent):
        # Every conversation will be 5 minutes
        agent.busy_time = 5 * 60
        other_agent.busy_time = 5*60
        conversation = agent.converse(other_agent, self.time)
        # TODO: could we set their destination to a halfway point between the agents?
        agent.conversation, other_agent.conversation = conversation, conversation
        agent.destination, other_agent.destination = None, None

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
