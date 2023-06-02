import math
import numpy as np
from numpy.linalg import norm
from util import *

class Agent:
    def __init__(self, character_sheet):
        self.memory_stream = []
        self.name = character_sheet['name']
        self.x, self.y, self.z = character_sheet['position']['x'], character_sheet['position']['y'], character_sheet['position']['z']
        self.description = character_sheet['description']
        self.vision_radius = character_sheet['vision_radius']
        self.destination = None
        self.status = None
        self.conversation = None

    def is_within_range(self, x2, y2, z2):
        x1, y1, z1 = self.x, self.y, self.z
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        return distance <= self.vision_radius

    def prompt(self):
        return self.summary_description +'\n'+ format_time(self.time) +'\n'+ self.status +'\n'+ self.memory_stream[-1].description() +'\n'+ self.revelant_context_summary
    
    def retrieve_memories(self,time,query):
        score = []
        arec = 1
        aimp = 1
        arel = 1
        for m in self.memory_stream:
            decay = 0.99
            recency = (1-decay)**(time.hour-m.last_access.hour)
            
            importance = 1#get ChatGPT to rate the memory's description with a prompt like this:
            #"On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory.\nMemory: "+m.description+"\nRating: <fill in>"
            
            emb = [1,1] #embedding(m.description), using the language model. 'query' passed into this function is an embedding vector already
            relevance = np.dot(emb,query)/(norm(emb)*norm(query))
            score.append(arec*recency + aimp*importance + arel*relevance)
        k = 3
        retrieve = sorted(range(len(score)), key = lambda i: score[i])[-k:]
        for m in self.memory_stream[retrieve]: m.last_access = time
        return self.memory_stream[retrieve]
