from tree_sitter import Language, Parser
import tree_sitter_languages

# only works for javascript. needs refactoring so that each language has its own handler

file_path = "my_code.js"
source_code = """
function add(a, b) {
  return a + b;
}
function subtract(a, b) {
  return a - b;
}
class Calculator {
  constructor() {
    this.value = 0;
  }
  add(a, b) {
    return a + b;
  }
  subtract(a, b) {
    return a - b;
  }
}
"""

file_path = "example.py"
source_code = """
def global_function(x, y):
    return x + y

class SampleClass:
    def __init__(self, value):
        self._property = value

    @property
    def sample_property(self):
        return self._property

    @sample_property.setter
    def sample_property(self, value):
        self._property = value

    def sample_method(self, a, b):
        return a * b
"""

file_path = "example.cs"
source_code = """
using System;

class ExampleClass
{
    private int _property;

    public ExampleClass(int value)
    {
        _property = value;
    }

    public int Property
    {
        get { return _property; }
        set { _property = value; }
    }

    public int Add(int a, int b)
    {
        return a + b;
    }

    public int Multiply(int x, int y)
    {
        return x * y;
    }
}

static class Program
{
    static void Main()
    {
        Console.WriteLine("Hello, World!");
    }
}

"""


parser = tree_sitter_languages.get_parser("c_sharp")
tree = parser.parse(bytes(source_code, "utf8"))
root_node = tree.root_node

entities = []

def get_function_signature(node):
    if node.type == 'method_definition':
        name = ''
        params = ''
        for child in node.children:
            if child.type == 'property_identifier':
                name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'formal_parameters':
                params = source_code[child.start_byte:child.end_byte]
        return f"{name}{params}"
    else:
        name = ''
        params = ''
        for child in node.children:
            if child.type == 'identifier':
                name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'formal_parameters':
                params = source_code[child.start_byte:child.end_byte]
        return f"{name}{params}"

def find_entities(node, parent=None):
    entity = None
    
    if node.type == 'function_declaration':
        signature = get_function_signature(node)
        entity = {'type': 'function', 'name': signature, 'children': []}

    elif node.type == 'method_definition':
        signature = get_function_signature(node)
        entity = {'type': 'method', 'name': signature, 'children': []}
    
    elif node.type == 'class_declaration':
        name = None
        for child in node.children:
            if child.type == 'identifier':
                name = source_code[child.start_byte:child.end_byte]
        entity = {'type': 'class', 'name': name, 'children': []}
    
    if entity:
        if parent:
            parent['children'].append(entity)
        else:
            entities.append(entity)
    else:
        entity = parent
    
    for child in node.children:
        find_entities(child, entity)

find_entities(root_node)

def print_tree(entity, indent='', last=True):
    symbol = '└─' if last else '├─'
    type_display = 'method' if entity['type'] == 'method' else entity['type']
    print(indent + f"{symbol} {type_display}: {entity['name']}")
    indent += '   ' if last else '│  '
    for i, child in enumerate(entity['children']):
        print_tree(child, indent, i == len(entity['children']) - 1)

print(file_path)
for i, entity in enumerate(entities):
    print_tree(entity, '', i == len(entities) - 1)
