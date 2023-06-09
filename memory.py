from model import model

class Memory:
    def __init__(self, time, description):
        self.time = time
        self.last_access = time
        self.description = description
        self.importance = self.generate_importance()

    def generate_importance(self):
        # prompt chatgpt
        prompt = f'On the scale of 0 to 9, where 0 is purely mundane (e.g., brushing teeth, making bed) and 9 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory, or give a 0 if it is difficult to determine.\n Memory: {self.description}\n Rating: <fill in>'
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        output = model(messages)
        number = output.split()[1][0]

        return int(number)

    