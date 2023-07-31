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
        for child in node.children: 
            self.places[child.path] = child
            self.places[child.name] = child
            if node.children: self.lookup_places(child)
    
    def initial_json(self):
        data = {}
        data['spawn'] = True
        data['player'] = {'quests':[],'npc_response':""}
        data['agents'] = []
        for i, agent in enumerate(self.agents):
            data['agents'].append({})
            data['agents'][i]['name'] = agent.name
            data['agents'][i]['status'] = agent.status
            data['agents'][i]['conversing_with'] = None
            data['agents'][i]['destination'] = {"nameId": agent.destination.name, "location": agent.destination.location}
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
            data['agents'][i]['conversing_with'] = agent.conversing_with
            data['agents'][i]['conversation'] = agent.conversation

    def update_agents(self):
        with open(Path(path + 'game_info/to_server.json'), 'r') as file: 
            front_data = json.load(file)
        for agent in self.agents:
            while front_data['player']['agent'] and front_data['player']['toAgent'] == "":
                time.sleep(.5)
                with open(Path(path + 'game_info/to_server.json'), 'r') as file: 
                    front_data = json.load(file)
            
            if front_data['player']['toAgent'] != "": self.generate_quest(front_data['player'])
            self.update_agent(agent)
        # with Pool(processes=10) as pool:
        #     pool.map(self.update_agent, self.agents)

        self.time = increase_time(self.time, self.time_step)
        

    def update_agent(self, agent):
        timeofday = get_timeofday(self.time)
        if timeofday == agent.waking_hours["up"]: 
            agent.plan_day(self.time)
            self.execute_plan(agent)
        #Call reflection if agent is going to bed, or call hour/minute plans if during waking hours
        elif timeofday == agent.waking_hours["down"]: agent.end_day(self.time)
        elif agent.waking_hours["up"] < timeofday < agent.waking_hours["down"]:
            if not self.perceive_objects(agent):
                self.perceive_agents(agent)
            if agent.busy_time <= 0:
                agent.conversation = None
                agent.conversing_with = None
                if timeofday%100 == 0: agent.plan_hour(self.time)
                else: agent.plan_next(self.time)
                self.execute_plan(agent)
            else: agent.busy_time -= self.time_step

    def perceive_objects(self,agent):
        perceived = []
        choices = []
        for place in agent.observed_objects:
            state = self.places[place].state
            # Make an observation for that thing if its state is different or newly observed
            if place not in agent.last_observed or agent.last_observed[place] != state:
                agent.last_observed[place] = state
                description = f'{place} is {state}'
                memory = Memory(self.time, description)
                agent.add_memory(memory)
                perceived.append(memory)
                choices.append(self.places[place])
        # Choose whether or not to react to each observation
        if agent.conversation == None and len(perceived) > 0:
            react, interact = agent.react(self.time, perceived)
            if react>=0: 
                agent.status = interact
                self.execute_plan(agent, choices[min(react, len(choices)-1)])
                return True
        return False
    
    def perceive_agents(self,agent):
        for other_agent in agent.observed_agents:
            # Make both agents see each other
            #TODO: prompts do not consistently produce statuses that fit with this sentence structure, e.g "Bob is check on Alice", "Alice is Alice would chat"
            description = f'{other_agent.name}\'s plan is to {other_agent.status}'
            memory = Memory(self.time, description)
            agent.add_memory(memory)
            
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
            "state": str
        }
        dictionary = prompt_until_success(prompt, expected_structure)
        agent.destination.state = dictionary['state']
    
    def choose_location(self,agent,root=None,quest=None):
        if root: location = root
        else:
            #Remaining at current location is an option at the first level of traversal
            location = agent.destination
            root = self.root

        choices = f'0: {location.name}' if not quest else ''
        for c in range(len(root.children)):  
            s = f'{c+1}: {root.children[c].name}'
            choices = '\n'.join([choices,s])
        
        query = f'Given the place(s) above, write a JSON dictionary object with "choice": int. Choice should be one of the indices shown above.'
        if quest: query = ' '.join([query,f'Make its value the index of the place which best fits the following quest description: {quest}'])
        else: query = ' '.join([query,f'Make its value the index of the place which is the most reasonable for {agent.name} to do the following activity: {agent.status}'])
        
        prompt = '\n'.join([choices, query])
        expected_structure = {
            "choice": int
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
        agent.conversing_with, other_agent.conversing_with = other_agent.name, agent.name
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
    

    def generate_quest(self,player,agent_coherence=True,use_intention=True):
        agent = self.agents[0]
        for a in self.agents:
            if a.name == player['agent']:
                agent = a
                break      

        if agent_coherence:
            if use_intention: 
                memories = agent.retrieve_memories(self.time, player['toAgent'])
                context = f'The player has an interest in the following: {player["toAgent"]}\n'
                prompt = f', and that the player would be interested in.\n'
            else: 
                memories = agent.retrieve_memories(self.time, f"Somebody is asking {agent.name} for a quest")
                context = ''
                prompt = '.\n'
            name = agent.name
            context += f'{name} is talking to the player, and remembers the following:\n'
            for m in memories: context += f'{m.description}\n'
            prompt = context + f'Generate a quest that {name} would know about or want done' + prompt
        else: 
            name = "an NPC"
            if use_intention: prompt = f'An NPC is talking to the player, who has an interest in the following: {player["toAgent"]}\nGenerate a quest that the player would be interested in.\n'
            else: prompt = f'Generate a quest for a player in a small village surrounded by a forest, a field, and a mountain.'

        prompt += f'Give your quest as a JSON dictionary object with three fields, "name": str, "type": int, and "description": str. "name" should be the quest name. "description" should be {name}\'s words describing the quest objective. "type" denotes the objective of the quest, and should be one of three numbers: 1 for grabbing an item, 2 for visiting a location, or 3 for fighting enemies.'
        expected_structure = {
            "name": str,
            "type": int,
            "description": str
        }
        quest = prompt_until_success(prompt, expected_structure)
        if not 1<=quest['type']<=3: quest['type'] = 0
        
        location = self.choose_location(None,self.root,quest['description'])
        prompt = f'The following is a quest description: {quest["description"]}\nThe following is the location where this quest should be done: {location.name}\nGiven this quest location, give a revised quest description that mentions the quest location. Give your answer as a JSON dictionary object with one field, "description": str.'
        expected_structure = {
            "description": str
        }
        dictionary = prompt_until_success(prompt, expected_structure)
        quest['description'] = dictionary['description']
        quest['location'] = location.location
        quest['source'] = agent.name
        quest['state'] = 0

        memory = Memory(self.time,f"Told the player about the following quest: {quest['description']}")
        agent.add_memory(memory)

        with open(Path(path + 'game_info/to_client.json'), 'r') as file:
            data = json.load(file)
        data['player']['quests'].append(quest)
        data['player']['npc_response'] = quest['description']
        with open(Path(path + 'game_info/to_client.json'), 'w') as file:
            json.dump(data, file)


    def get_save_index(self):
        self.save_index = get_index()

    def save(self):
        pickle_file_name = path + f'saved_games/save_state_{self.save_index}.pkl'
        with open(pickle_file_name, 'wb') as file:
            pickle.dump(self, file)
