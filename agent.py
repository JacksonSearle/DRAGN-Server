import math
import json
import numpy as np
import re
from model import model
from numpy.linalg import norm
from util import *
from sentence_embed import embed
from time import mktime
from memory import Memory

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
        self.dayplan = None
        self.hourplans = ['Sleeping.']
        self.yesterday_summary = None
        self.destination = None
        self.status = None
        self.conversation = None
        self.summary_description = None

    def prep_seeds(self, time):
        seeds = self.seed_memories.split(';')
        for seed in seeds:
            memory = Memory(time, seed)
            self.memory_stream.append(memory)


    def is_within_range(self, x2, y2, z2):
        x1, y1, z1 = self.x, self.y, self.z
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        return distance <= self.vision_radius

    def prompt(self):
        return self.summary_description +'\n'+ format_time(self.time) +'\n'+ self.status +'\n'+ self.memory_stream[-1].description() +'\n'+ self.revelant_context_summary
    
    def query_model(self,prompt):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        return model(messages)

    def retrieve_memories(self,time,query,k=4):
        score = []
        arec = 1
        aimp = 1
        arel = 1
        query = embed([query])
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
        response_text = self.query_model(prompt)
        self.dayplan = response_text
        return self.plan_hour(time)
        
    
    def plan_hour(self,time):
        dayplan = '{self.name}\'s daily plan: ' + self.dayplan
        lastplan = '{self.name}\'s plan for the last hour: ' + self.hourplans[-1]
        query = f'Given the context above, what does {self.name} plan to do this hour?'
        prompt = '\n'.join([dayplan, lastplan, query])
        response_text = self.query_model(prompt)
        self.hourplans.append(response_text)
        return self.plan_next(time)
        

    def plan_next(self,time):
        hourplan = '{self.name}\'s plan this hour: ' + hourplan
        status = '{self.name}\'s status right now: ' + self.status
        query = f'Given the context above, what does {self.name} plan to do right now, and for how long? Give your answer as a json dictionary object with "plan": string and "duration": int, and make the duration either 5, 10, or 15 minutes.'
        prompt = '\n'.join([time_prompt(time), hourplan, status, query])
        response_text = self.query_model(prompt)
        # TODO: Ensure it's a json or reprompt
        dictionary = json.loads(response_text)
        return dictionary['plan'], dictionary['duration']
    
    
    def reflect(self,time):
        self.yesterday_summary = self.summarize_day(set_start_time(time.tm_year,time.tm_month,time.tm_mday,0,0,0))
        for m in self.memory_stream:
            if m.type == "Observation": self.memory_stream.remove(m)

        relevant_context = '\n'.join([memory.description for memory in self.memory_stream[-100:]])
        question = f'Given only the information above, what are 3 most salient high-level questions we can answer about the subjects in the statements?'
        prompt = '\n'.join([relevant_context, question])
        response_queries = self.query_model(prompt)
        response_queries = self.find_responses(response_queries,3)

        statements = f"Statements about {self.name}\n"
        for query in response_queries:
            memories = self.retrieve_memories(time, query)
            statements += '\n'.join([memory.description for memory in memories])
        question = "What 5 high-level insights can you infer from the above statements?"
        prompt = '\n'.join([statements, question])
        response_text = self.query_model(prompt)
        response_text = self.find_responses(response_text,5)
        for r in response_text: self.memory_stream.append(Memory(time, r, "Reflection"))

    def find_responses(s,i):
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

        self.summary_description = '\n'.join(name, 
                                             innate_traits, 
                                             core_characteristics, 
                                             daily_occupation, 
                                             recent_progress_in_life)

    def summary_description_prompt(self, time, text, k=4):
        # Generate prompt
        query = f'How would one describe {self.name}\'s {text} given the following statements?'
        memories = self.retrieve_memories(time, query, k)
        prompt = '\n'.join([query] + [memory.description for memory in memories])
        response_text = self.query_model(prompt)
        return response_text

    def format_status(self):
        return f'{self.name}\'s status: {self.status}'
    
    def format_description(self):
        return f'Observation: {self.name}'
    
    def react(self, time, memory):
        # Generate prompt
        memories = self.retrieve_memories(time, memory.description)
        relevant_context = '\n'.join([memory.description for memory in memories])
        question = f'Based on the context above, give a json dictionary object with "react": bool and "interact": string. It will decide whether the character should react to the observation, and if they reacted, how they would interact with the object'
        prompt = '\n'.join([self.summary_description, time_prompt(time), self.format_status(), memory.format_description(), relevant_context, question])
        response_text = self.query_model(prompt)

        # TODO: Ensure it's a json or reprompt
        
        # Parse output to json
        dictionary = json.loads(response_text)

        return dictionary['react'], dictionary['interact']