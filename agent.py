import math
import json
import numpy as np
from model import model
from numpy.linalg import norm
from util import *
from sentence_embed import embed
from time import mktime

class Agent:
    def __init__(self, character_sheet):
        self.memory_stream = []
        self.name = character_sheet['name']
        self.age = character_sheet['age']
        self.x, self.y, self.z = character_sheet['position']['x'], character_sheet['position']['y'], character_sheet['position']['z']
        self.innate_traits = character_sheet['innate_traits']
        self.description = character_sheet['description']
        self.vision_radius = character_sheet['vision_radius']
        self.destination = None
        self.status = None
        self.conversation = None
        self.summary_description = None

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
        k = 3
        for m in self.memory_stream:
            decay = 0.99
            recency = (1-decay)**((mktime(time)-mktime(m.last_access))/3600)
            
            importance = m.importance#get ChatGPT to rate the memory's description with a prompt like this:
            #"On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory.\nMemory: "+m.description+"\nRating: <fill in>"
            
            emb, que = embed([m.description,query])
            relevance = np.dot(emb,que)/(norm(emb)*norm(que))
            score.append(arec*recency + aimp*importance + arel*relevance)
        retrieve = []
        idx = sorted(range(len(score)), key = lambda i: score[i])[-k:]
        for i in idx: 
            self.memory_stream[i].last_access = time
            retrieve.append(self.memory_stream[i])
        return retrieve