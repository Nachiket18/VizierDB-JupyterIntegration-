'''
Created on 17-May-2021

@author: Nachiket Deo
'''

import nbformat as nb 
import ast
import os
import queue 
from collections import deque,defaultdict
from ast_parse import Graphprocess, Visitast,Graph
from itertools import groupby,chain

import pickle


class parse_notebook:
    

    def __init__(self):
        self.input_provenance_variable = {} 


    def display_input_provenance(self):
        return self.input_provenance_variable


    ##
    ## Function calculates the path length in Dependency Graph which is a DAG.
    ## Input - Dependency Graph, Vertex in the Dependency Graph , max_depth - variable to store maximum path length,max_path_dict - a Dynamic Programming data structure
    ## Output - Depth of the subgraph from the given node in the input
    ##

    def rec_find_child_nodes(g,node_id,max_path_dict,vertices):
    
        vertex = g.getVertex(node_id)
        vertex_id = vertex.getId()
    
        vertices_current_cell = []

    #print(vertex_id)

        if not vertex.getConnections():        
            return 1

        else:
        
            depth = 0
        
            for child in vertex.getConnections():
            #print("Child befor passing to function call",child)
            
                id_vertex_child = child.getId()
            
            #print(vertex_id,id_vertex_child)
            
                if id_vertex_child in max_path_dict:
                    path_length = max_path_dict[id_vertex_child]
            
                else:
                    path_length = parse_notebook.rec_find_child_nodes(g,id_vertex_child,max_path_dict,vertices)
                    
                if path_length > depth:
                    if vertex_id != id_vertex_child:
                        depth = path_length
                    
                    else:
                        depth = path_length - 1
                
                    max_path_dict[id_vertex_child] = depth
                
                else:
                    max_path_dict[id_vertex_child] = path_length


            return 1 + depth
            
            

##
## Calculates the number of cells in notebook from the generated Dependency graph
##

    def getCellCount(vertices):
    
        f = lambda x:x[0]
        return ([next(g) for _, g in groupby(sorted(vertices, key=f), key=f)])


##
## The original graph has nodes of format (cell_no,line_no) --> (cell_no_2,line_no_2). 
## We need the dependency graph as (cell_no) --> (cell_no_2) for calculating metric for parallelism on graph 
##

## (1,2) --> (2,3) x
## (2,4) --> (4,3) y 

## 1 -> 2 
## 2 -> 4


    def processGraph(g):

        g_prime = Graphprocess()
    
        for v in g:
        
            new_vertex = v.getId()
        
            if new_vertex[0] not in g_prime.getVertices():
                g_prime.addVertex(new_vertex[0])
        
            if not v.getConnections():
                continue
        
            else:
                
                for nbr in v.getConnections():

                    if nbr.getId()[0] not in g_prime.getVertices():
                        g_prime.addVertex(nbr.getId()[0])    

                    if nbr.getId()[0] != new_vertex[0]:
                        g_prime.addEdge(v.getId()[0],nbr.getId()[0], v.getWeight(nbr) )
                 
        return g_prime
    
##
## Fetches the Maximum Length Path by calculating the path from each vertex in Dependency Graph
## Calculates the degree of parallelism possible - max_depth+path / total_number_cells
## Input: Dependency graph (g)

    def calc_degree_parallelism(g):
    
        max_path_dict = {}
        max_depth = 0
        cell_dependency_structure_for_parallelism = {}
        vertices = g.getVertices

        for v in g:
        
            iter_code_structures = 1
        
            if not v.getConnections():
            #print("Tree No connections:",v.getId())
                if (v.getId()) not in max_path_dict:
                    max_path_dict[v.getId()] = 1
            

            else:
            #print("Tree with connections:",v.getId())
                for nbr in v.getConnections():
                #print("Tree:",nbr.getId())
                
                    if (nbr.getId()) not in max_path_dict:
                 
                        path_length = parse_notebook.rec_find_child_nodes(g,nbr.getId(),max_path_dict,vertices)
                        iter_code_structures += 1
                    
                        if path_length > max_depth:
                            max_depth = path_length
                            max_path_dict[v.getId()] = path_length


                for length_max_node in max_path_dict:

                    if  max_path_dict[length_max_node] > max_depth:
                        max_depth =  max_path_dict[length_max_node]             
                    
                     
        #print("Max Depth:",max_depth)
        #print("Max Dictionary",max_path_dict)
    
        vertices = g.getVertices()
    
    #print("Vertices",vertices)
    
    #cells = getCellCount(vertices)
    
        total_cells = max(vertices)
    
    #len(cells)
    
    #print("Total_Cells:",total_cells)
    
    #print("depth_tree",max_path_dict)
    
        parallelism_test = max_depth / total_cells
    #print("Test for Parallelism",parallelism_test)
    
    #print("cell_dependency_structure",cell_dependency_structure_for_parallelism)
    
    
    #print_dependency_graph(g)
    
        return (max_depth,total_cells) 
    


    def print_dependency_graph(g):
    
        for v in g:
            if not v.getConnections():
                print(v.getId())
            else:
                for nbr in v.getConnections():
                    print(v.getId(),"->",nbr.getId(),"on",v.getWeight(nbr))  


    def BFS(g:Graph,source):
        
        q = queue.Queue()
        visited = []

        #print(source.getId())
        q.put(source)

        visited.append(source.getId())

        #print("visited",visited)

        while( q.empty() == False):
            v = q.get()
    
            vertex = g.getVertex(v)

            for nbr in v.getConnections():
                if nbr.getId() not in visited:
                    q.put(nbr)
                    visited.append(nbr.getId())

        return visited
    

    def make_graph_undirected(g:Graph):
        
        for v in g:
            if not v.getConnections():
                continue
            else:
                for nbr in v.getConnections():
                    g.addEdge(nbr.getId(),v.getId(),v.getWeight(nbr))
                    #print(v.getId(),"->",nbr.getId(),"on",v.getWeight(nbr))
        return g
    
    
    
    def connectivity_metric(g:Graph,source):
        
        visited_connectivity = []
        connected_components = 0


        g_undirected = parse_notebook.make_graph_undirected(g)

        
        visited_connectivity = parse_notebook.BFS(g_undirected,source)

        #print("Visited_first",visited_connectivity)

        if len(visited_connectivity) == g_undirected.numVertices:
            #print("In If")ṁ
            connected_components = 1
            
        else:
            
            for vertex in g_undirected:
                
                if vertex.getId() not in visited_connectivity:
                    print("In loop")
                    
                    output_visited = parse_notebook.BFS(g,vertex)
                    print("Visited_loop",output_visited)

                    visited_connectivity = list(set(chain(visited_connectivity, output_visited)))
                    
                    print("Visited_connectivity",visited_connectivity)
                    connected_components = connected_components + 1
                    
                    if len(visited_connectivity) == g_undirected.numVertices:
                        break
        #print("connected_components",connected_components)
        return connected_components

    def pickle_export(g):
    
        filename = 'cell_export_details'
        outfile = open(filename,'wb')
    
        output_dict_pickle = {}
    
        for v in g:
            if not v.getConnections():
                continue
            else:
                for nbr in v.getConnections():
                    if v.getId()[0] not in output_dict_pickle:
                        output_dict_pickle[v.getId()[0]]  = [v.getWeight(nbr)]
                    else:
                        if v.getWeight(nbr) not in output_dict_pickle[v.getId()[0]]:
                            output_dict_pickle[v.getId()[0]].append(v.getWeight(nbr))
                        
                    #print(v.getId(),"->",nbr.getId(),"on",v.getWeight(nbr))  
    
        pickle.dump(output_dict_pickle,outfile)
        outfile.close()
    
        cwd_path = os.getcwd()
    
        output_file_path = os.path.abspath(os.path.join(cwd_path, filename))
    
        return output_file_path



    def pickle_read_dependency(infile):
    
        infile = open(infile,'rb')
    
        dependency_dict = pickle.load(infile)
    
    #print("Pickled_dependency_dictionary",dependency_dict)
    
        infile.close()


    def parse_notebook(out):
    
        in_built_functions = ['print','int','float','min','udiff','input','len','NotImplementedError','max','ValueError','round','nop','sigmoid','logic_gate','test','open','sum','list','collections.defaultdict']
    
        g = Graph()
    
        cell_dict = dict()
    
        funct_cell_Dict = {}
    
        cell_dict_control_flow = dict()
        cell_index = 1
        
        input_provenance_variable = {}
        output_provenance_variable = {} 
    
        
        for cell in out.cells:
            if cell.cell_type == 'code':
                input_provenance_variable[cell_index] = []
                output_provenance_variable[cell_index] = []
                vis = Visitast()        
            
                removal_list = ['%matplotlib','notebook','inline']
            
                for word in removal_list:
                    cell.source = cell.source.replace(word, "")
               
                tree = ast.parse(cell.source)
                vis.visit(tree)
        

                if len(vis.display_store_dict()) != 0 or len(vis.display_load_dict()) != 0 or len(vis.display_func_dictionaries()) != 0:        
                
                #print("Loop",vis.display_loop_dictionaries())

                    for key,value in vis.display_store_dict().items():
                                 
                        for j in value:
                            
                            if j not in cell_dict: 
                                cell_dict[j] = [(cell_index,key)] 
                            else:
                                cell_dict[j].append((cell_index,key))        
                        
                        cell_dict[j].sort(reverse = True)
                
            
        
                    store_dict = vis.display_store_dict()
                    inverted_store_dict = defaultdict(list)

                    for key,value in store_dict.items():
                        output_provenance_variable[cell_index].append(value)

                
            
                    for k, v in vis.display_store_dict().items():
                        for elem in v:
                            inverted_store_dict[elem].append(k)
                        
                
                
                    for key,value in vis.display_load_dict().items():
                    
                        for j in value:
                        
                            key_store_dict = []
                            if j in inverted_store_dict: 
                                key_store_dict = inverted_store_dict[j]
                        
                                isOrphan = False
        
                                for elem in key_store_dict:
                                    if key <= elem:
                                    ##
                                    ## The element was accessed before it was assigned. 
                                    ## Suggesting that the variable was assigned value in previous cells
                                    ##
                                        isOrphan = True
                                        break
                        #print("Key,Key_left",key,key_store_dict,isOrphan)    
                        #print(j,store_dict.values(),isOrphan)
                        
                            if ((j not in store_dict.values() or isOrphan == True) and (j not in in_built_functions)):
                            
                        
                                if j in cell_dict:
                                    references = cell_dict[j] 
                                    #print("References",references,j)
                                    tmp_references = references[0]

                                    if j not in input_provenance_variable[cell_index] and tmp_references[0] != cell_index:
                                        input_provenance_variable[cell_index].append(j)    
    
                                    for data in references:
                                        if data != (cell_index,key) and not (data[0] == cell_index and data[1] > key ):
                                        #print("Func dep data",data,(cell_index,key),j)
                                            g.addEdge(data,(cell_index,key),j)

                                            try:
                                                (cell,line) = cell_dict_control_flow[j]
                                            except KeyError:
                                                break
                                         
                                            if (cell == data[0]) and (data[1] == line):
                                                continue
                                            else:
                                                break
                            
    
                            else:
    
                                for elem in key_store_dict:
                                    if elem != key: 
                                    #print((cell.execution_count,elem),(cell.execution_count,key),j)
                                        g.addEdge((cell_index,elem),(cell_index,key),j)
                                        try:
                                            (cell,line) = cell_dict_control_flow[j]
                                        except KeyError:
                                            break
                                         
                                        if (cell == cell_index) and (elem == line):
                                            continue
                                        else:
                                            break
                        
                
                            if j in funct_cell_Dict.keys():
                            
                            
                                dependency_main_program_dict = funct_cell_Dict[j]
                            
                            
                                for dependency_elem in dependency_main_program_dict:
                            
                                    previous_cell_dependency_details_cell = dependency_elem[0]
                                    previous_cell_dependency_details_var = dependency_elem[1]
                                 
                                    g.addEdge((previous_cell_dependency_details_cell[0],previous_cell_dependency_details_cell[1]),(cell_index,key),previous_cell_dependency_details_var)
                             
                             
                    for key_line,dict_loop in vis.display_func_dictionaries().items():
                    
                        dict_store_func = dict_loop[0]
                        dict_load_func = dict_loop[1]                
                    
                        inverted_func_store_dict  = defaultdict(list) 
                        for k, v in dict_store_func.items():
                            for elem in v:
                                inverted_func_store_dict[elem].append(k)
                    
                        if key_line not in cell_dict: 
                            cell_dict[key_line] = [(cell_index,1)] 

                        for key,value in dict_store_func.items():
                            output_provenance_variable[cell_index].append(value)
                                
                        for key,value in dict_load_func.items():
                        #print("Value",value)
                            for j in value:
                            #print("j",j)
                                key_left = inverted_func_store_dict.get(j, None)
                                if key_left is not None:
                                    for key_store_dict in key_left:
                                        if key_store_dict < key: 
                                            g.addEdge((cell_index,key_store_dict),(cell_index,key),j)
                            
                                elif key_left is None:
                                    key_left_main = inverted_store_dict.get(j,None)
                                
                            
                                    if key_left_main: 
                                        for k in key_left_main:
                                            if k < key:
                                                g.addEdge((cell_index,k),(cell_index,key),j)
                                
                                    elif j in cell_dict:
                                    #print("Inside func_dependency:",key_line,j)
                                        references = cell_dict[j] 
                                        funct_cell_Dict[key_line] = []
                                    
                                        if j not in input_provenance_variable[cell_index]:
                                            input_provenance_variable[cell_index].append(j)

                                        for data in references:
                                            if data != (cell_index,key) and not (data[0] == cell_index and data[1] > key ):
                                            
                                                funct_cell_Dict[key_line].append((data,j)) 
                                            
                                                g.addEdge(data,(cell_index,key),j)
                                        
                                                try:
                                                    (cell,line) = cell_dict_control_flow[j]
                                                except KeyError:
                                                    break
                                         
                                                if (cell == data[0]) and (data[1] == line):
                                                    continue
                                                else:
                                                    break              
                            
                            
                            
                            
                            
                    for key_line,dict_loop in vis.display_loop_dictionaries().items():
                    
                        dict_store = dict_loop[0]
                        dict_load = dict_loop[1]                
                    
                        inverted_loop_store_dict  = defaultdict(list) 
                        for k, v in dict_store.items():
                            for j in v:
                            
                                if j not in cell_dict: 
                                    cell_dict[j] = [(cell_index,key)] 
                                else:
                                    cell_dict[j].append((cell_index,key))        
                        
                            cell_dict[j].sort(reverse = True)
                    
                            for elem in v:
                                inverted_loop_store_dict[elem].append(k)

                        for key,value in dict_store.items():
                            output_provenance_variable[cell_index].append(value)
                        

                        for key,value in dict_load.items():
                        #print("Value",value)
                            for j in value: #and (j not in in_built_functions):
                            #print("j",j)
                                key_left = inverted_loop_store_dict.get(j, None)
                                if key_left is not None:
                                    for key_store_dict in key_left:
                                        if key_store_dict < key: 
                                            g.addEdge((cell_index,key_store_dict),(cell_index,key),j)
                            
                                elif key_left is None:
                                
                                    key_left_main = inverted_store_dict.get(j,None)
                                
                                    if key_left_main: 
                                        for k in key_left_main:
                                            if k < key:
                                                g.addEdge((cell_index,k),(cell_index,key),j)
                                
                                    elif j in cell_dict:
                                    #print("Inside func_dependency:",key_line,j)
                                        references = cell_dict[j] 

                                        if j not in input_provenance_variable[cell_index]:
                                            input_provenance_variable[cell_index].append(j)

                                        for data in references:
                                            if data != (cell_index,key) and not (data[0] == cell_index and data[1] > key ):
                                        
                                                g.addEdge(data,(cell_index,key),j)
                
                                
                    for key_line,dict_loop in vis.display_control_flow_dictionaries().items():
                    
                        dict_store_control = dict_loop[0]
                        dict_load_control = dict_loop[1]                
                    
                        inverted_control_store_dict  = defaultdict(list) 
                        for k, v in dict_store_control.items():
                            for elem in v:
                                inverted_control_store_dict[elem].append(k)

                        for key,value in dict_store_control.items():
                            output_provenance_variable[cell_index].append(value)
            
                        for key,value in dict_load_control.items():
                        #print("Value",value)
                            for j in value:
                            #print("j",j)
                                key_left = inverted_control_store_dict.get(j, None)
                                if key_left is not None:
                                    for key_store_dict in key_left:
                                        if key_store_dict < key: 
                                            g.addEdge((cell_index,key_store_dict),(cell_index,key),j)
                            
                                elif key_left is None:
                                    key_left_main = inverted_store_dict.get(j,None)
                                
                                    if key_left_main: 
                                        for k in key_left_main:
                                            if k < key:
                                                g.addEdge((cell_index,k),(cell_index,key),j)                                        
                
                
                
                cell_index += 1 
                                        
            #print(cells.source)
            #print(vis.display_store_dict())
            #print(vis.display_load_dict())
            #print(cell_dict)
    

        g_prime = parse_notebook.processGraph(g)

        #parse_notebook.print_dependency_graph(g)
        parse_notebook.print_dependency_graph(g_prime)
        
        return g_prime   

##
## The following code inside main function parses the jupyter notebook and generates the dependency graph
##


    def parse_notebook_test(out):
    
        in_built_functions = ['print','int','float','min','udiff','input','len','NotImplementedError','max','ValueError','round','nop','sigmoid','logic_gate','test','open','sum','list','collections.defaultdict']
    
        g = Graph()
    
        cell_dict = dict()
    
        funct_cell_Dict = {}
    
        cell_dict_control_flow = dict()
        cell_index = 1
        
        input_provenance_variable = {} 
    
        
        for cell in out.cells:
            if cell.cell_type == 'code':
                input_provenance_variable[cell_index] = []
                vis = Visitast()        
            
                removal_list = ['%matplotlib','notebook','inline']
            
                for word in removal_list:
                    cell.source = cell.source.replace(word, "")
            
            ##
            ##      
                tree = ast.parse(cell.source)
                vis.visit(tree)
        

                if len(vis.display_store_dict()) != 0 or len(vis.display_load_dict()) != 0 or len(vis.display_func_dictionaries()) != 0:        
                
                #print("Loop",vis.display_loop_dictionaries())

                    for key,value in vis.display_store_dict().items():
                                 
                        for j in value:
                            
                            if j not in cell_dict: 
                                cell_dict[j] = [(cell_index,key)] 
                            else:
                                cell_dict[j].append((cell_index,key))        
                        
                        cell_dict[j].sort(reverse = True)
                
            
        
                    store_dict = vis.display_store_dict()
                    inverted_store_dict = defaultdict(list)
                
                
            
                    for k, v in vis.display_store_dict().items():
                        for elem in v:
                            inverted_store_dict[elem].append(k)
                        
                
                
                    for key,value in vis.display_load_dict().items():
                    
                        for j in value:
                        
                            key_store_dict = []
                            if j in inverted_store_dict: 
                                key_store_dict = inverted_store_dict[j]
                        
                                isOrphan = False
        
                                for elem in key_store_dict:
                                    if key <= elem:
                                    ##
                                    ## The element was accessed before it was assigned. 
                                    ## Suggesting that the variable was assigned value in previous cells
                                    ##
                                        isOrphan = True
                                        break
                        #print("Key,Key_left",key,key_store_dict,isOrphan)    
                        #print(j,store_dict.values(),isOrphan)
                        
                            if ((j not in store_dict.values() or isOrphan == True) and (j not in in_built_functions)):
                            
                        
                                if j in cell_dict:
                                    references = cell_dict[j] 
                                    #print("References",references,j)
                                    tmp_references = references[0]

                                    if j not in input_provenance_variable[cell_index] and tmp_references[0] != cell_index:
                                        input_provenance_variable[cell_index].append(j)    
    
                                    for data in references:
                                        if data != (cell_index,key) and not (data[0] == cell_index and data[1] > key ):
                                        #print("Func dep data",data,(cell_index,key),j)
                                            g.addEdge(data,(cell_index,key),j)

                                            try:
                                                (cell,line) = cell_dict_control_flow[j]
                                            except KeyError:
                                                break
                                         
                                            if (cell == data[0]) and (data[1] == line):
                                                continue
                                            else:
                                                break
                            
    
                            else:
    
                                for elem in key_store_dict:
                                    if elem != key: 
                                    #print((cell.execution_count,elem),(cell.execution_count,key),j)
                                        g.addEdge((cell_index,elem),(cell_index,key),j)
                                        try:
                                            (cell,line) = cell_dict_control_flow[j]
                                        except KeyError:
                                            break
                                         
                                        if (cell == cell_index) and (elem == line):
                                            continue
                                        else:
                                            break
                        
                
                            if j in funct_cell_Dict.keys():
                            
                            
                                dependency_main_program_dict = funct_cell_Dict[j]
                            
                            
                                for dependency_elem in dependency_main_program_dict:
                            
                                    previous_cell_dependency_details_cell = dependency_elem[0]
                                    previous_cell_dependency_details_var = dependency_elem[1]
                                 
                                    g.addEdge((previous_cell_dependency_details_cell[0],previous_cell_dependency_details_cell[1]),(cell_index,key),previous_cell_dependency_details_var)
                             
                             
                    for key_line,dict_loop in vis.display_func_dictionaries().items():
                    
                        dict_store_func = dict_loop[0]
                        dict_load_func = dict_loop[1]                
                    
                        inverted_func_store_dict  = defaultdict(list) 
                        for k, v in dict_store_func.items():
                            for elem in v:
                                inverted_func_store_dict[elem].append(k)
                    
                        if key_line not in cell_dict: 
                            cell_dict[key_line] = [(cell_index,1)] 

                                
                        for key,value in dict_load_func.items():
                        #print("Value",value)
                            for j in value:
                            #print("j",j)
                                key_left = inverted_func_store_dict.get(j, None)
                                if key_left is not None:
                                    for key_store_dict in key_left:
                                        if key_store_dict < key: 
                                            g.addEdge((cell_index,key_store_dict),(cell_index,key),j)
                            
                                elif key_left is None:
                                    key_left_main = inverted_store_dict.get(j,None)
                                
                            
                                    if key_left_main: 
                                        for k in key_left_main:
                                            if k < key:
                                                g.addEdge((cell_index,k),(cell_index,key),j)
                                
                                    elif j in cell_dict:
                                    #print("Inside func_dependency:",key_line,j)
                                        references = cell_dict[j] 
                                        funct_cell_Dict[key_line] = []
                                    
                                        if j not in input_provenance_variable[cell_index]:
                                            input_provenance_variable[cell_index].append(j)

                                        for data in references:
                                            if data != (cell_index,key) and not (data[0] == cell_index and data[1] > key ):
                                            
                                                funct_cell_Dict[key_line].append((data,j)) 
                                            
                                                g.addEdge(data,(cell_index,key),j)
                                        
                                                try:
                                                    (cell,line) = cell_dict_control_flow[j]
                                                except KeyError:
                                                    break
                                         
                                                if (cell == data[0]) and (data[1] == line):
                                                    continue
                                                else:
                                                    break              
                            
                                                        
                    for key_line,dict_loop in vis.display_loop_dictionaries().items():
                    
                        dict_store = dict_loop[0]
                        dict_load = dict_loop[1]                
                    
                        inverted_loop_store_dict  = defaultdict(list) 
                        for k, v in dict_store.items():
                            for j in v:
                            
                                if j not in cell_dict: 
                                    cell_dict[j] = [(cell_index,key)] 
                                else:
                                    cell_dict[j].append((cell_index,key))        
                        
                            cell_dict[j].sort(reverse = True)
                    
                            for elem in v:
                                inverted_loop_store_dict[elem].append(k)
            
            
                        for key,value in dict_load.items():
                        #print("Value",value)
                            for j in value: #and (j not in in_built_functions):
                            #print("j",j)
                                key_left = inverted_loop_store_dict.get(j, None)
                                if key_left is not None:
                                    for key_store_dict in key_left:
                                        if key_store_dict < key: 
                                            g.addEdge((cell_index,key_store_dict),(cell_index,key),j)
                            
                                elif key_left is None:
                                
                                    key_left_main = inverted_store_dict.get(j,None)
                                
                                    if key_left_main: 
                                        for k in key_left_main:
                                            if k < key:
                                                g.addEdge((cell_index,k),(cell_index,key),j)
                                
                                    elif j in cell_dict:
                                    #print("Inside func_dependency:",key_line,j)
                                        references = cell_dict[j] 

                                        if j not in input_provenance_variable[cell_index]:
                                            input_provenance_variable[cell_index].append(j)

                                        for data in references:
                                            if data != (cell_index,key) and not (data[0] == cell_index and data[1] > key ):
                                        
                                                g.addEdge(data,(cell_index,key),j)
                
                                

                    for key_line,dict_loop in vis.display_control_flow_dictionaries().items():
                    
                        dict_store_control = dict_loop[0]
                        dict_load_control = dict_loop[1]                
                    
                        inverted_control_store_dict  = defaultdict(list) 
                        for k, v in dict_store_control.items():
                            for elem in v:
                                inverted_control_store_dict[elem].append(k)
            
            
                        for key,value in dict_load_control.items():
                        #print("Value",value)
                            for j in value:
                            #print("j",j)
                                key_left = inverted_control_store_dict.get(j, None)
                                if key_left is not None:
                                    for key_store_dict in key_left:
                                        if key_store_dict < key: 
                                            g.addEdge((cell_index,key_store_dict),(cell_index,key),j)
                            
                                elif key_left is None:
                                    key_left_main = inverted_store_dict.get(j,None)
                                
                                    if key_left_main: 
                                        for k in key_left_main:
                                            if k < key:
                                                g.addEdge((cell_index,k),(cell_index,key),j)                                        
                           
                cell_index += 1 
                                        
            #print(cells.source)
            #print(vis.display_store_dict())
            #print(vis.display_load_dict())
            #print(cell_dict)
    

        g_prime = parse_notebook.processGraph(g)

        #print("G_Prime")
        #parse_notebook.print_dependency_graph(g_prime)

        #print(input_provenance_variable)

        #return input_provenance_variable 
        
        (max_depth,total_cells) = parse_notebook.calc_degree_parallelism(g_prime) 
        #print (max_depth,total_cells)
        
        g_undirected = parse_notebook.make_graph_undirected(g_prime)

        parse_notebook.print_dependency_graph(g_undirected)

        
        connected_components = parse_notebook.connectivity_metric(g_prime,g_prime.getVertex(1))
        
        #connected_components = 1
    
        #print("visited",parse_notebook.BFS(g_prime,g_prime.getVertex(1)))

        print("Connected Components",connected_components)
        parse_notebook.print_dependency_graph(g_prime)

        return  (max_depth, total_cells,connected_components)


    


#print(json.load(out))

#print(pickle.load("D:/Workspace/PythonAST/src/Index.ipynb"))

#print(type(out))

