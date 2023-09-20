#!/usr/bin/env python3
import json
from treelib import Node, Tree
import graphviz
import pathlib
import re


duplicates = [
]
duplicates_count = 0

def idify(id: str) -> str:
    o = id



    id = id.replace(", ", "_").replace(" ", "_").replace("/", "_").replace("-", "_").replace(",", "_")
    if id in duplicates:
        global duplicates_count
        id = f"{id}_{duplicates_count}"
        duplicates_count += 1

    id = re.sub(r'(\d{2})_(\d{2})_(\d{4})(_\w{2})?_',"", id)
    id = re.sub(r'(\d{2})_(\w{2})_(\d{4})_',"", id)

    if id.startswith("18_de_2060"):
        print("id:",id,"\noriginal:", o)
    
    return id

def titlefy(title: str):


    title= re.sub(r'(\d{2})-(\d{2})-(\d{4})(/\w{2})?', "", title)
    if (title.startswith("3D Scanning")):
        title = "3D_Scanning"
    return title.strip()

def append_tree(tree:Tree, parent:str, children:list[dict]):
    for child in children:
        title = titlefy(child['title'])
        id = idify(child['title'])
        duplicates_count = 0
        while id in tree:
            duplicates_count += 1            
            id = f"{id}_{duplicates_count}"
            
        if child['children']:
            tree.create_node(title, id, parent=parent)
            append_tree(tree, id, child['children'])
        else:

            tree.create_node(title, id, parent=parent)

def alter_file(filename, content):
    with open(filename, 'r+') as f:
        # Read the existing contents of the file
        contents = f.read()

        # Insert a new line after the first line
        new_contents = contents.split('\n')

        new_contents.insert(1, content)
        new_contents = '\n'.join(new_contents)

        # Write the new contents back to the file
        f.seek(0)
        f.write(new_contents)
        f.truncate()

def make_tree(modules):
    tree = Tree()
    
    tree.create_node("", "root", data=modules)
    
    for module in modules:

        tree.create_node(titlefy(module['title']), idify(module['title']), parent="root")
        if module['children']:
            append_tree(tree, idify(module['title']), module['children'])
    tree.to_graphviz("modules.gv",shape="rectangle")
    
    
    #alter_file("modules.gv", '\tlayout=circo')
    
    graph = graphviz.Source.from_file('modules.gv')
    
    #graph.render('modules', format="png", cleanup=True)



    #tree.render('modules.gv', view=True)
    tree.show()
 
def main():
    with open('modules.json', 'r') as f:
        modules = json.load(f)
        
    make_tree(modules)

if __name__ == '__main__':
    # graph = graphviz.Source.from_file('modules.gv', encoding='utf-8')
    # graph.render('modules', format='svg', cleanup=True)
    main()
        
    
