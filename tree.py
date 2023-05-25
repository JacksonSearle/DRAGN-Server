class Node:
    def __init__(self, name, path, x=None, y=None):
        self.name = name
        self.x = x
        self.y = y
        self.path = path
        self.state = 'is idle'
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def description(self):
        return f'({self.path}) {self.name} {self.state}'

def build_tree(data, parent=None, path=''):
    x, y = map(int, data['position'].split(',')) if data['position'] != None else (None, None)
    path = path + '/' + data['name'] if path else data['name']
    node = Node(data['name'], path, x, y)
    if parent:
        parent.add_child(node)
    for child in data['children']:
        build_tree(child, node, path)

    return node

def get_all_nodes(root):
    nodes = []
    if root:
        if root.x != None:
            nodes.append(root)
        for child in root.children:
            nodes += get_all_nodes(child)
    return nodes

places = {
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
                                'position': '0, 7',
                                'children': []
                            },
                            {
                                'name': 'Chair 2',
                                'position': '2, 7',
                                'children': []
                            },
                            {
                                'name': 'Table',
                                'position': '1, 7',
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
                                'position': '0, 9',
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
                                'position': '7, 7',
                                'children': []
                            },
                            {
                                'name': 'Chair 2',
                                'position': '8, 7',
                                'children': []
                            },
                            {
                                'name': 'Table',
                                'position': '9, 7',
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
                                'position': '9, 9',
                                'children': []
                            },
                            {
                                'name': 'Alice\'s Bed',
                                'position': '8, 9',
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
                                'position': '0, 2',
                                'children': []
                            },
                            {
                                'name': 'Seat 2',
                                'position': '2, 2',
                                'children': []
                            },
                            {
                                'name': 'Seat 3',
                                'position': '0, 1',
                                'children': []
                            },
                            {
                                'name': 'Seat 4',
                                'position': '2, 1',
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
                                'position': '0, 3',
                                'children': []
                            },
                            {
                                'name': 'sink',
                                'position': '1, 3',
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
                        'position': '0, 9',
                        'children': []
                    },
                    {
                        'name': 'Fishable Area',
                        'position': '0, 7',
                        'children': []
                    }
                ]
            },
            {
                'name': 'Park',
                'position': '4, 4',
                'children': []
            },
        ]
    }