from model import model

class Memory:
    def __init__(self, time, description):
        self.time = time
        self.last_access = time
        self.description = description
        self.importance = self.generate_importance()

    def generate_importance(self):
        # prompt chatgpt
        prompt = "On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory.\n Memory: {self.description}\n Rating: <fill in>"
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        output = model(messages)
        number = output.split()[1]

        return int(number)

    