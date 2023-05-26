import math
from util import *

class Agent:
    def __init__(self, character_sheet):
        self.memory_stream = []
        self.name = character_sheet['name']
        self.x, self.y = character_sheet['position']
        self.description = character_sheet['description']
        self.vision_radius = character_sheet['vision_radius']
        self.destination = None
        self.status = None
        self.conversation = None

    def is_within_range(self, x2, y2):
        x1, y1 = self.x, self.y
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance <= self.vision_radius

    def prompt(self):
        return self.summary_description +'\n'+ format_time(self.time) +'\n'+ self.status +'\n'+ self.memory_stream[-1].description() +'\n'+ self.revelant_context_summary