from util import *
import json
from agent import Agent
from memory import Memory
from tree import get_all_nodes, build_tree, places
from character_sheets import character_sheets
import config
if config.MODE == 'debugging':
    from debugging_model import model  # Import for debugging mode
elif config.MODE == 'testing':
    from testing_model import model  # Import for testing mode

class Game:
    def __init__(self, time_step):
        self.time_step = time_step
        self.time = set_start_time(2023, 5, 24, 7, 0, 0)
        self.root = build_tree(places)
        self.places = get_all_nodes(self.root) # These are all visitable places
        self.agents = self.make_agents()
        self.make_agent_info()
    
    def make_agents(self):
        agents = []
        for character_sheet in character_sheets:
            agents.append(Agent(character_sheet, self.time))
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
        self.perceive_objects(agent)
        self.perceive_agents(agent)
        #Call day plan if agent is just waking up, call reflection if agent is going to bed, or call hour/minute plans if during waking hours
        timeofday = get_timeofday(self.time)
        if timeofday == agent.waking_hours["up"]: 
            agent.plan_day(self.time)
            self.execute_plan(agent)
        elif timeofday == agent.waking_hours["down"]: agent.reflect(self.time)
        elif agent.waking_hours["up"] < timeofday < agent.waking_hours["down"]:
            if agent.busy_time <= 0:
                if timeofday%100 == 0: agent.plan_hour(self.time)
                else: agent.plan_next(self.time)
                self.execute_plan(agent)
            else: agent.busy_time -= self.time_step

    def perceive_objects(self,agent):
        for place in self.places:
            if agent.is_within_range(place.x, place.y, place.z):
                # Make an observation for that thing
                memory = Memory(self.time, place.state)
                agent.add_memory(memory)
                # Choose whether or not to react to each observation
                react, interact = agent.react(self.time, memory)
                if react: 
                    agent.status = interact
                    self.execute_plan(agent)
    
    def perceive_agents(self,agent):
        for j, other_agent in enumerate(self.agents):
            # Make sure an agent isn't talking to themselves
            if agent is not other_agent and agent.is_within_range(other_agent.x, other_agent.y, other_agent.z):
                # Make both agents see eachother
                description = f'{other_agent.name} is {other_agent.status}'
                memory = Memory(self.time, description)
                agent.memory_stream.append(memory)
                
                # Choose whether or not to react to each observation
                react, interact = agent.react(self.time, memory)
                if react:
                    agent.status = interact
                    # make a memory for the person they are talking to
                    description = f'{agent.name} is {agent.status}'
                    memory = Memory(self.time, description)
                    other_agent.add_memory(memory)
                    other_agent.status = description
                    # generate dialogue
                    self.conversation(agent, other_agent)
    
    def execute_plan(self,agent):
        if agent.object: agent.object.state = "idle"
        agent.object = self.choose_location(agent)
        #TODO: Prompt model for detailed state of object based on agent's current action on it.
        agent.object.state = "in use"
        agent.destination = {"x":object.x, "y":object.y, "z":object.z}
    
    def choose_location(self,agent,root=None):
        if not root: root = self.root
        choices = ''
        for c in range(len(root.children)): 
            s = f'{c}: {root.children[c].name}'
            choices = '\n'.join([choices,s])
        query = f'Given the places above, write a JSON dictionary object with "choice": int. Make its value the index of the place which is the most reasonable for {agent.name} to do the following activity: {agent.status}'
        prompt = '\n'.join([choices, query])
        response_text = self.query_model(prompt)
        # TODO: Ensure it's a json or reprompt
        dictionary = json.loads(response_text)
        location = root.children[dictionary['choice']]
        if not location.children: return location
        return self.choose_location(agent,location)

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
    
    def query_model(self,prompt):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        return model(messages)

    def conversation(self, agent, other_agent):
        # Generate the conversation
        dialogue_history = ""
        continue_conversation = True
        i = 0
        while True:
            continue_conversation, response = agent.respond(dialogue_history, other_agent, self.time)
            dialogue_history += f'\n{agent.name}: {response}'
            i += 1
            if continue_conversation == False or i > 9:
                break
            continue_conversation, response = other_agent.respond(dialogue_history, agent, self.time)
            dialogue_history += f'\n{other_agent.name}: {response}'
            i += 1
            if continue_conversation == False or i > 9:
                break

        # Set conversation for each agent and set destination and status to null
        # TODO: could we set their destination to a halfway point between the agents?
        agent.conversation, other_agent.conversation = dialogue_history, dialogue_history
        agent.destination, other_agent.destination = None, None

        # Put the conversation description into memory stream
        conversation_description = self.create_conversation_description(dialogue_history)
        shared_memory = Memory(self.time, conversation_description)
        agent.add_memory(shared_memory)
        other_agent.add_memory(shared_memory)
    
    def create_conversation_description(self, dialogue_history):
        message = f'Generate a one sentence description of the following dialogue history:\n {dialogue_history}'
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
        response_text = model(messages)
        return response_text
