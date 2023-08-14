class Node:
    def __init__(self, name, path, location=None):
        self.name = name
        self.location = location
        self.path = path
        self.state = 'idle'
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def description(self):
        return f'({self.path}) {self.name} {self.state}'

def build_tree(data, parent=None, path=''):
    x, y, z = data['position'] if data['position'] else (None, None, None)
    location = {"x": x, "y": y, "z": z}
    path = path + '/' + data['name'] if path else data['name']
    node = Node(data['name'], path, location)
    for child in data['children']: build_tree(child, node, path)
    if parent: parent.add_child(node)
    else: return node
