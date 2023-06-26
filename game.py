from util import *
import json
from agent import Agent
from memory import Memory
from tree import get_all_nodes, build_tree
from character_sheets import character_sheets
import config
if config.MODE == 'debugging':
    from debugging_model import query_model  # Import for debugging mode
elif config.MODE == 'testing':
    from testing_model import query_model  # Import for testing mode

class Game:
    def __init__(self, time_step):
        self.time_step = time_step
        self.time = set_start_time(2023, 5, 24, 7, 0, 0)
        with open('world_tree.json', 'r') as file:
            self.root = build_tree(json.load(file))
        self.places = get_all_nodes(self.root) # These are all visitable places
        self.agents = self.make_agents()
        self.make_agent_info()

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
                description = f'{place.name} is {place.state}'
                memory = Memory(self.time, description)
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
        prompt = f'{agent.name} is {agent.status} at the {agent.object.name}. Generate a JSON dictionary object with a single field, "state": string, which describes the state the {agent.object.name} is in.'
        response_text = query_model(prompt)
        # Extract the contents between the brackets
        response_text = brackets(response_text)
        # TODO: Ensure it's a json or reprompt
        if response_text == 'error':
            agent.object.state = 'error'
            print('error in executing plan')
        else:
            agent.object.state = json.loads(response_text)['state']
        agent.destination = {"x":agent.object.x, "y":agent.object.y, "z":agent.object.z}
    
    def choose_location(self,agent,root=None):
        if not root: root = self.root
        choices = ''
        for c in range(len(root.children)): 
            # This is one indexed
            s = f'{c+1}: {root.children[c].name}'
            choices = '\n'.join([choices,s])
        query = f'Given the place(s) above, write a JSON dictionary object with "choice": int. Choice should be one of the indexes shown above. Make its value the index of the place which is the most reasonable for {agent.name} to do the following activity: {agent.status}'
        prompt = '\n'.join([choices, query])
        response_text = 'error'
        while response_text == 'error':
            response_text = query_model(prompt)
            # TODO: Ensure it's a json or reprompt
            # Extract the contents between the brackets
            response_text = brackets(response_text)
        dictionary = json.loads(response_text)
        # Un-one index it
        if 'choice' not in dictionary.keys():
            index = 0
            print('Choice set to default')
        else:
            index = dictionary['choice'] - 1
        if index > len(root.children) - 1 or index < 0:
            index = 0
            print(f'Choice set to default')
        location = root.children[index]
        if not location.children: return location
        return self.choose_location(agent,location)

    def update(self, data):
        for i, agent in enumerate(self.agents):
            data['agents'][i]['status'] = agent.status
            data['agents'][i]['destination'] = agent.destination
            data['agents'][i]['conversation'] = agent.conversation

    def conversation(self, agent, other_agent):
        # Every conversation will be 5 minutes
        agent.busy_time = 5 * 60
        other_agent.busy_time = 5*60

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
        response_text = query_model(message)
        return response_text
