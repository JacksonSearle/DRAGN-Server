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

def get_all_nodes(root):
    nodes = []
    if root:
        if root.children == []:
            nodes.append(root)
        for child in root.children:
            nodes += get_all_nodes(child)
    return nodes

temp_places = {
        'name': 'World',
        'position': None,
        'children': [
            {
                'name': 'Frank\'s House',
                'position': None,
                'children': [
                    {
                        'name': 'Dining Room',
                        'position': None,
                        'children': [
                            {
                                'name': 'Chair 1',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'Chair 2',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'Table',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                        ]
                    },
                    {
                        'name': 'Bedroom',
                        'position': None,
                        'children': [
                            {
                                'name': 'Bed',
                                'position': [-2015, -3356, 500],
                                'children': []
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Bob\'s house',
                'position': None,
                'children': [
                    {
                        'name': 'Dining Room',
                        'position': None,
                        'children': [
                            {
                                'name': 'Chair 1',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'Chair 2',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'Table',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                        ]
                    },
                    {
                        'name': 'Bedroom',
                        'position': None,
                        'children': [
                            {
                                'name': 'Bob\'s Bed',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'Alice\'s Bed',
                                'position': [-2015, -3356, 500],
                                'children': []
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Cafe',
                'position': None,
                'children': [
                    {
                        'name': 'Cafe Seating',
                        'position': None,
                        'children': [
                            {
                                'name': 'Seat 1',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'Seat 2',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'Seat 3',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'Seat 4',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                        ]
                    },
                    {
                        'name': 'Bathroom',
                        'position': None,
                        'children': [
                            {
                                'name': 'toilet',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                            {
                                'name': 'sink',
                                'position': [-2015, -3356, 500],
                                'children': []
                            },
                        ]
                    }
                ]
            },
            {
                'name': 'Lake',
                'position': None,
                'children': [
                    {
                        'name': 'Swimmable Area',
                        'position': [-2015, -3356, 500],
                        'children': []
                    },
                    {
                        'name': 'Fishable Area',
                        'position': [-2015, -3356, 500],
                        'children': []
                    }
                ]
            },
            {
                'name': 'Park',
                'position': [-2015, -3356, 500],
                'children': []
            },
        ]
    }