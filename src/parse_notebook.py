'''
Created on 17-May-2021

@author: Nachiket Deo
'''

import nbformat as nb 
import ast
from collections import deque,defaultdict
from src.ast_parse import Visitast,Graph
from itertools import groupby


 
##
## Function calculates the path length in Dependency Graph which is a DAG.
## Input - Dependency Graph, Vertex in the Dependency Graph , max_depth - variable to store maximum path length,max_path_dict - a Dynamic Programming data structure
## Output - Depth of the subgraph from the given node in the input

def rec_find_child_nodes(g,node_id,max_depth,max_path_dict):
    
    #print("Tree:",node_id)
    vertex = g.getVertex(node_id)
    vertex_id = vertex.getId()
    
    if not vertex.getConnections():
            return 1
    
    else:
        
        depth = 0
        for child in vertex.getConnections():
            #print("Child befor passing to function call",child)
            id_vertex_child = child.getId()
            print(vertex_id,id_vertex_child)
            
            try:
                max_path_dict[id_vertex_child]
                path_length = max_path_dict[id_vertex_child]
            except KeyError:
                path_length = rec_find_child_nodes(g,id_vertex_child,max_depth,max_path_dict)
                max_path_dict[id_vertex_child] = path_length
                
        
            if path_length > max_depth:
                max_depth = path_length
            
            if path_length > depth:
                if vertex_id[0] != id_vertex_child[0]:
                    depth = path_length
                else:
                    depth = path_length - 1
        
        return 1 + depth
            
            

##
## Calculates the number of cells in notebook from the generated Dependency graph
##

def getCellCount(vertices):
    
    f = lambda x:x[0]
    return ([next(g) for _, g in groupby(sorted(vertices, key=f), key=f)])
    
    

##
## Fetches the Maximum Length Path by calculating the path from each vertex in Dependency Graph
## Calculates the degree of parallelism possible - max_depth+path / total_number_cells
## Input: Dependency graph (g)

def calc_degree_parallelism(g):
    
    max_path_dict = {}
    max_depth = 0    
    for v in g:
        
        if not v.getConnections():
            #print("Tree No connections:",v.getId())
            max_path_dict[v.getId()] = 1

        else:
            #print("Tree with connections:",v.getId())
            for nbr in v.getConnections():
                #print("Tree:",nbr.getId())
                
                path_length = rec_find_child_nodes(g,nbr.getId(),max_depth,max_path_dict)
                if path_length > max_depth:
                    max_depth = path_length
        
        
    print("Max Depth",max_depth)
    
    vertices = g.getVertices()
    
    #print("Vertices",vertices)
    
    cells = getCellCount(vertices)
    
    total_cells = len(cells)
    
    print(total_cells)
    
    #print("depth_tree",max_path_dict)
    
    parallelism_test = max_depth / total_cells
    print("Test for Parallelism",parallelism_test) 
    

##
## The following code inside main function parses the jupyter notebook and generates the dependency graph
##

def main():
    out = nb.read("D:/VizierDB-JupyterIntegration/src/test_vizier.ipynb",as_version=4)
    #print(out)
    
    g = Graph()
    
    cell_dict = dict()
    
    cell_dict_control_flow = dict()
    
    cell_execution_count_manual = 1
    
    
    for cell in out.cells:
        if cell.cell_type == 'code':
    
            vis = Visitast()        
            tree = ast.parse(cell.source)
        
            
            vis.visit(tree)
            
            control_flow_dict = vis.display_control_flow_dictionaries()
            
            print("Control Flow Assignments",control_flow_dict.items())
            
            for key,value in vis.display_left_dict().items():
                
#                 if control_flow_dict is not None:
#                     control_flow_bondaries = list(control_flow_dict.items())[control_flow_loop_counter]
#                     print("Control Flow Boundaries",control_flow_bondaries[0],control_flow_bondaries[1])
                
                for j in value:
                        
                    if j not in cell_dict: 
                        cell_dict[j] = [(cell_execution_count_manual,key)] 
                    else:
                        cell_dict[j].append((cell_execution_count_manual,key))        
                    
                cell_dict[j].sort(reverse = True)
            
            for key,value in control_flow_dict.items():
                
                cell_dict_control_flow[value] = ((cell_execution_count_manual,key))
               
            
            left_dict = vis.display_left_dict()
            inverted_left_dict = defaultdict(list)
            
            
            
#             for key,value in control_flow_dict.items():
#                 cell_dict_control_flow[]
            
            
        
            for k, v in vis.display_left_dict().items():
                for elem in v:
                    inverted_left_dict[elem].append(k)
            
            #inverted_left_dict[elem].sort(reverse = True)
            print("Inverted List",inverted_left_dict)
            
        
            for key,value in vis.display_right_dict().items():
                #print(key,value)
#                 loop_boundaries = list(control_flow_dict.items())[iter_i_control_flow_keys]
#                 if key > loop_boundaries[0] :
#                     if key > loop_boundaries[1]:
#                         iter_i_control_flow_keys += 1
                
                for j in value:
                    key_left_dict = inverted_left_dict[j]
                    isOrphan = False
    
                    for elem in key_left_dict:
                        if key <= elem:
                            ##
                            ## The element was accessed before it was assigned. 
                            ## Suggesting that the variable was assigned value in previous cells
                            ##
                            isOrphan = True
                            break
                    print("Key,Key_left",key,key_left_dict,isOrphan)    
                    print(j,left_dict.values(),isOrphan)
                    
                    if j not in left_dict.values() or isOrphan == True:
                            references = cell_dict[j]
                            print("references",references)
                            
                            for data in references:
                                if data != (cell_execution_count_manual,key) and not (data[0] == cell_execution_count_manual and data[1] > key ):
                                    print(data,(cell_execution_count_manual,key),j)
                                    g.addEdge(data,(cell_execution_count_manual,key),j)
                                    
                                    try:
                                        (cell,line) = cell_dict_control_flow[j]
                                    except KeyError:
                                        break
                                     
                                    if (cell == data[0]) and (data[1] == line):
                                            continue
                                    else:
                                        break
                                
                    else:

                        for elem in key_left_dict:
                            if elem != key: 
                                #print((cell.execution_count,elem),(cell.execution_count,key),j)
                                g.addEdge((cell_execution_count_manual,elem),(cell_execution_count_manual,key),j)
                                try:
                                    (cell,line) = cell_dict_control_flow[j]
                                except KeyError:
                                        break
                                     
                                if (cell == cell_execution_count_manual) and (elem == line):
                                    continue
                                else:
                                    break
                                
            
            for key_line,dict_loop in vis.display_loop_dictionaries().items():
                
                dict_left = dict_loop[0]
                dict_right = dict_loop[1]                
                
                inverted_loop_left_dict  = defaultdict(list) 
                for k, v in dict_left.items():
                    for elem in v:
                        inverted_loop_left_dict[elem].append(k)
        
        
                for key,value in dict_right.items():
                    #print("Value",value)
                    for j in value:
                        #print("j",j)
                        key_left = inverted_loop_left_dict.get(j, None)
                        if key_left is not None:
                            for key_left_dict in key_left:
                                if key_left_dict < key: 
                                    g.addEdge((cell_execution_count_manual,key_left_dict),(cell_execution_count_manual,key),j)
                        
                        elif key_left is None:
                            key_left_main = inverted_left_dict.get(j,None)
                            if key_left_main: 
                                for k in key_left_main:
                                    if k < key:
                                        g.addEdge((cell_execution_count_manual,k),(cell_execution_count_manual,key),j)
                            
                            
            
            cell_execution_count_manual += 1 
                                        
            #print(cells.source)
            #print(vis.display_left_dict())
            #print(vis.display_right_dict())
            #print(cell_dict)
    
    for v in g:
        if not v.getConnections():
            print(v.getId())
        else:
            for nbr in v.getConnections():
                print(v.getId(),"->",nbr.getId(),"on",v.getWeight(nbr))        
            

    
    
    calc_degree_parallelism(g)            
            
            
                
if __name__ == '__main__':
    main() 
    
    







#print(json.load(out))

#print(pickle.load("D:/Workspace/PythonAST/src/Index.ipynb"))

#print(type(out))

