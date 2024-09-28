#!/usr/bin/env python3
import json
from treelib import Tree
import graphviz
import pathlib
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape

from bigtree import Node, tree_to_dot


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

def append_tree(root:Node, parent:Node, children:list[dict]):
    for child in children:
        title = titlefy(child['title'])
        id = idify(child['title'])
        
        duplicates_count = 0
        
        while True:
            try:
                n = Node(title, parent=parent)
                break                
            except:
                pass
            duplicates_count += 1         
            title = f"{title}_{duplicates_count}"
            
        if child['children']:
            append_tree(root, n, child['children'])

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
    root = Node("root")
    
    for module in modules:

        n = Node(titlefy(module['title']), parent=root)
        if module['children']:
            append_tree(root, n, module['children'])

    root.show()
    graph = tree_to_dot(root, node_shape="rectangle", rankdir="LR")
    graph.write_png("modules.png")
    graph.write_svg("modules.svg")
    graph.write_dot("modules.dot")
    graph.to_string()
 
def flatten_modules(modules:list[dict], parent_path = "") -> list[dict]:
    output = []
    for module in modules:
        if module['children']:
            output.extend(flatten_modules(module['children'], parent_path + " > " + module['title']))
            
        
        del module["children"]
        module["path"] = parent_path
        output.append(module)
        
    return output
 
# def dependency_tree(modules):
#     tree = []
    
#     for module in modules:
#         if not "Voraussetzung f\u00fcr die Teilnahme" in module:
#             tree.append(module)
#     print(tree)    

def compareable(a:str) -> str:
    return re.sub(r"[^a-z]", "", a.lower(), count=0)

def get_dependnecies(dependency_str: str, module_titles:list[str]) -> (list[str]):

    module_titles = [compareable(m) for m in module_titles]
    print(module_titles)
    exit(0)
    dependencies = re.findall(r'["„][^"]+"', dependency_str)
    if dependencies:
        dependencies = [d[1:-1] for d in dependencies]
        for dependency in dependencies:
            if compareable(dependency) in module_titles:
                print("found:", dependency)
            else:
                print("not found:", dependency)
                print(dependency_str)

        
        
    #print(dependency_str)
    
    return dependencies

def create_dependency(modules):
    # print("create_dependency:", modules)
    output = []
    module_titles = [m["title"] for m in modules]
    for module in modules:
        dependencies = None
        if "details" not in module:
            continue
        for detail in module["details"]:
            if detail["title"] == "Voraussetzung f\u00fcr die Teilnahme":
                dependencies = detail["details"]
                break
                            
        if dependencies is None:
            output.append({"title": module['title'], "empfolen": [], "voraussetzung": []})
            continue
        get_dependnecies(dependencies, module_titles)
        

        module = {"title": module['title'], "empfolen": [], "voraussetzung": []}

 

def get_specific_detail(name:str, details:list[dict], delete:bool=True) -> str:
    to_return = None
    for index , detail in enumerate(details):
        if compareable(detail["title"]) == compareable(name):
            to_return = detail["details"]
            break
    if to_return is None:
        return ""
    if delete:
        details.remove(detail)
    return to_return


def bold_qutes(text:str) -> str:
    qutes = re.findall(r'["„][^"]+"', text)
    for qute in qutes:
        text = text.replace(qute, f"<b>{qute}</b>")
    return text

    
def generate_pretty_html(modules: list[dict]) -> str:
    modules_to_render = []
    for module in modules:
        if not "details" in module:
            # print("no details in module:", module)
            continue
        
        new_module = {}
        # print(module["details"])
        
        module["name"]  = module["title"]
        module["short_name"] = get_specific_detail("Anzeige im Stundenplan", module["details"])
        module["path"] = module["path"]
        module["cp"] = get_specific_detail("Credits", module["details"])
        module["dependency"] = bold_qutes(get_specific_detail("Voraussetzung f\u00fcr die Teilnahme", module["details"]))
        module["lehrinhalte"] = get_specific_detail("Lehrinhalte", module["details"])
        module["qualifikationsziele"] = get_specific_detail("Qualifikationsziele", module["details"]) + get_specific_detail("Qualifikationsziele / Lernergebnisse", module["details"])
        module["ergaenzung"]  = get_specific_detail("Erg\u00e4nzung zur Pr\u00fcfungsform", module["details"])
        module["termine"] = get_specific_detail("Kurstermine", module["details"])
        module["sonstiges"] = module["details"]
        modules_to_render.append(module)
    
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape()
    )

    template = env.get_template("module_template.html")
    

    # print(template.render(modules=modules_to_render))
    # print(modules_to_render)
    return template.render(modules=modules_to_render)
    

 
def main():
    with open('modules.json', 'r') as f:
        modules = json.load(f)
    
    flattened_modules = flatten_modules(modules.copy())
    with open('modules_flattened.json', 'w') as f:
        json.dump(flattened_modules, f, indent=4)
        


    html = generate_pretty_html(flattened_modules.copy())
    with open('modules.html', 'w') as f:
        f.write(html)

    # create_dependency(flattened_modules.copy())

        
    # dependency_tree(flattened_modules.copy())
    
        
    # make_tree(modules)

if __name__ == '__main__':
    # graph = graphviz.Source.from_file('modules.gv', encoding='utf-8')
    # graph.render('modules', format='svg', cleanup=True)
    main()
        
    
