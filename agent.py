import math
import json
import numpy as np
import re
from numpy.linalg import norm
from util import *
from sentence_embed import embed
from time import mktime
from memory import Memory
import config

if config.MODE == 'debugging':
    from debugging_model import query_model  # Import for debugging mode
elif config.MODE == 'testing':
    from testing_model import query_model  # Import for testing mode

class Agent:
    def __init__(self, character_sheet, time):
        self.memory_stream = []
        self.name = character_sheet['name']
        self.age = character_sheet['age']
        self.x, self.y, self.z = character_sheet['position']['x'], character_sheet['position']['y'], character_sheet['position']['z']
        self.innate_traits = character_sheet['innate_traits']
        self.seed_memories = character_sheet['seed_memories']
        self.prep_seeds(time)
        self.vision_radius = character_sheet['vision_radius']
        self.waking_hours = character_sheet['waking_hours']

        self.busy_time = 0
        self.dayplan = ''
        self.hourplans = ['Sleeping.']
        self.yesterday_summary = ''

        self.destination = None
        self.status = 'idle'
        self.last_observed = {}
        self.object = None
        self.conversation = None
        self.summary_description = None
        self.update_summary_description(time)
        self.reflect_buffer = 0
        self.summary_description_buffer = 0

    def add_memory(self, memory):
        self.memory_stream.append(memory)
        # Update buffers
        self.reflect_buffer += memory.importance
        self.summary_description_buffer += memory.importance
        # Check buffers
        if self.reflect_buffer > 150:
            self.reflect_buffer = 0
            self.reflect(memory.time)
        if self.summary_description_buffer > 40:
            self.summary_description_buffer = 0
            self.update_summary_description(memory.time)

    def prep_seeds(self, time):
        seeds = self.seed_memories.split(';')
        for seed in seeds:
            description = self.name + seed
            memory = Memory(time, description)
            self.memory_stream.append(memory)

    def is_within_range(self, x2, y2, z2):
        x1, y1, z1 = self.x, self.y, self.z
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        return distance <= self.vision_radius

    def prompt(self):
        return self.summary_description +'\n'+ format_time(self.time) +'\n'+ self.status +'\n'+ self.memory_stream[-1].description() +'\n'+ self.revelant_context_summary

    def retrieve_memories(self,time,query,k=4):
        score = []
        arec = 1
        aimp = 1
        arel = 1
        query = embed(query)
        for m in self.memory_stream:
            decay = 0.99
            recency = (1-decay)**min(0,((mktime(time)-mktime(m.last_access))/3600))
            importance = m.importance
            relevance = np.dot(m.emb,query)/(norm(m.emb)*norm(query))
            score.append(arec*recency + aimp*importance + arel*relevance)
        retrieve = []
        idx = sorted(range(len(score)), key = lambda i: score[i])[-k:]
        for i in idx: 
            self.memory_stream[i].last_access = time
            retrieve.append(self.memory_stream[i])
        return retrieve
    
    
    def summarize_day(self,time):
        return self.summary_description_prompt(time, 'day', 50)

    def plan_day(self,time):
        query = f'It is {format_time(time)}. What are {self.name}\'s plans today, given the following summary of what he did yesterday?'
        prompt = '\n'.join([self.summary_description, query, self.yesterday_summary])
        response_text = query_model(prompt)
        self.dayplan = response_text
        self.plan_hour(time) 
    
    def plan_hour(self,time):
        dayplan = f'{self.name}\'s daily plan: ' + self.dayplan
        lastplan = f'{self.name}\'s plan for the last hour: ' + self.hourplans[-1]
        query = f'Given the context above, what does {self.name} plan to do this hour?'
        prompt = '\n'.join([dayplan, lastplan, query])
        response_text = query_model(prompt)
        self.hourplans.append(response_text)
        self.plan_next(time)  

    def plan_next(self,time):
        hourplan = f'{self.name}\'s plan this hour: ' + self.hourplans[-1]
        status = f'{self.name}\'s status right now: '+ self.status
        query = f'Given the context above, what does {self.name} plan to do right now, and for how long? Give your answer as a json dictionary object with "plan": string and "duration": int, and make the duration either 5, 10, or 15 minutes. Describe plan in 8 words or less.'
        prompt = '\n'.join([time_prompt(time), hourplan, status, query])
        response_text = query_model(prompt)
        # TODO: Ensure it's a json or reprompt
        response_text = brackets(response_text)
        dictionary = json.loads(response_text)
        self.status, self.busy_time = dictionary['plan'], dictionary['duration']*60
    
    def end_day(self,time):
        self.yesterday_summary = self.summarize_day(set_start_time(time.tm_year,time.tm_month,time.tm_mday,0,0,0))
        for m in self.memory_stream:
            if m.type == "Observation": self.memory_stream.remove(m)
        self.reflect(time)
        

    def reflect(self,time):
        relevant_context = '\n'.join([memory.description for memory in self.memory_stream[-100:]])
        question = f'Given only the information above, what are 3 most salient high-level questions we can answer about the subjects in the statements?'
        prompt = '\n'.join([relevant_context, question])
        response_queries = query_model(prompt)
        response_queries = self.find_responses(response_queries,3)

        statements = f"Statements about {self.name}\n"
        for query in response_queries:
            memories = self.retrieve_memories(time, query)
            statements += '\n'.join([memory.description for memory in memories])
        question = "What 5 high-level insights can you infer from the above statements?"
        prompt = '\n'.join([statements, question])
        response_text = query_model(prompt)
        response_text = self.find_responses(response_text,5)
        for r in response_text: self.add_memory(Memory(time, r, "Reflection"))

    def find_responses(self, s, i):
        responses=[]
        for _ in range(i):
            match = re.search(r'\d. ', s)
            if match: s = s[match.end():]
            match = re.search(r'\?', s)
            if match: responses.append(s[:match.end()])
            else: return None
            s = s[match.end():]
        return responses

    
    def update_summary_description(self,time):
        # Name
        name = f'Name: {self.name} (age: {self.age})'

        # Innate traits
        innate_traits = f'Innate traits: {self.innate_traits}'

        # Core characteristics
        core_characteristics = self.summary_description_prompt(time, 'core characteristics')

        # Current daily occupation
        daily_occupation = self.summary_description_prompt(time, 'current daily occupation')

        # Feelings about his recent progress in life
        recent_progress_in_life = self.summary_description_prompt(time, 'feelings about his recent progress in life')

        self.summary_description = '\n'.join([name,
                                            innate_traits,
                                            core_characteristics,
                                            daily_occupation,
                                            recent_progress_in_life])

    def summary_description_prompt(self, time, text, k=4):
        # Generate prompt
        query = f'How would one describe {self.name}\'s {text} given the following statements?'
        memories = self.retrieve_memories(time, query, k)
        prompt = '\n'.join([query] + [memory.description for memory in memories])
        response_text = query_model(prompt)
        return response_text

    def format_status(self):
        return f'{self.name}\'s status: {self.status}'
    
    def react(self, current_time, memory):
        # Generate prompt
        memories = self.retrieve_memories(current_time, memory.description)
        relevant_context = "Relevant Context:\n"
        relevant_context += '\n'.join([memory.description for memory in memories])
        question = f'Based on the context above, give a json dictionary object with "react": bool, "interact": string and "duration": int. The react bool will show if {self.name} should react to the observation. The interact string will show how {self.name} would interact to the observation. The duration int shows how long {self.name} would interact with that object. Duration should be in minutes, somewhere between 5 and 15 minutes. If the observation is that something is idle, do not react.'
        prompt = '\n'.join([self.summary_description, time_prompt(current_time), self.format_status(), memory.format_description(), relevant_context, question])
        response_text = query_model(prompt)

        # TODO: Ensure it's a json or reprompt
        
        # Parse output to json
        response_text = brackets(response_text)
        dictionary = json.loads(response_text)

        if dictionary['react']:
            self.status = dictionary['interact']
            self.duration = dictionary['duration'] * 60
        else:
            dictionary['interact'] = ""

        return dictionary['react'], dictionary['interact']
    
    def converse(self, other_agent, current_time):
        recent_memory = self.memory_stream[-1]
        relevant_memories = self.retrieve_memories(current_time, recent_memory.description)
        other_memories = other_agent.retrieve_memories(current_time, other_agent.memory_stream[-1].description)
        relevant_memories = f'{self.name} remembers the following: {[memory.description for memory in relevant_memories]}'
        other_memories = f'{other_agent.name} remembers the following: {[m.description for m in other_memories]}'
        question = f'What should {self.name} and {other_agent.name} say to each other? Give your response as a JSON object with one field, conversation: str.'
        prompt = '\n'.join([
            self.summary_description,
            time_prompt(current_time),
            recent_memory.format_description(),
            relevant_memories,
            other_memories,
            f'{self.name}\'s status is: {self.status}',
            question
        ])
        response_text = query_model(prompt)
        response_text = brackets(response_text)
        # Parse continue_conversation and response, then return that
        try: dictionary = json.loads(response_text)
        except: dictionary = {'conversation': f'{self.name}: Hey.\n{other_agent.name}: Hey.'}
        return dictionary['conversation']

    