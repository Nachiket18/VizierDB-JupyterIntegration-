'''
Created on 17-May-2021

@author: Nachiket Deo
'''

import nbformat as nb 
import ast
import os
from collections import deque,defaultdict
from src.ast_parse import Visitast,Graph
from itertools import groupby

import pickle

 
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
            
            #print(vertex_id,id_vertex_child)
            
            if id_vertex_child in max_path_dict:
                path_length = max_path_dict[id_vertex_child]
            else:
                
                path_length = rec_find_child_nodes(g,id_vertex_child,max_depth,max_path_dict)
                    
            if path_length > depth:
                if vertex_id[0] != id_vertex_child[0]:
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
## Fetches the Maximum Length Path by calculating the path from each vertex in Dependency Graph
## Calculates the degree of parallelism possible - max_depth+path / total_number_cells
## Input: Dependency graph (g)

def calc_degree_parallelism(g):
    
    max_path_dict = {}
    max_depth = 0
    cell_dependency_structure_for_parallelism = {}
    
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
                 
                     #print("Max_Path",nbr.getId(),max_path_dict)    
#                     if iter_code_structures in cell_dependency_structure_for_parallelism.keys():
#                          
#                         if nbr.getId()[0] not in cell_dependency_structure_for_parallelism[iter_code_structures]: 
#                             cell_dependency_structure_for_parallelism[iter_code_structures].append(nbr.getId()[0])
#                      
#                     else:   
#                         cell_dependency_structure_for_parallelism[iter_code_structures] = [nbr.getId()[0]]
                        
                    path_length = rec_find_child_nodes(g,nbr.getId(),max_depth,max_path_dict)
                    iter_code_structures += 1
                    
                    if path_length > max_depth:
                        max_depth = path_length
                        max_path_dict[v.getId()] = path_length
                        
                    
                     
    print("Max Depth:",max_depth)
    
    vertices = g.getVertices()
    
    #print("Vertices",vertices)
    
    cells = getCellCount(vertices)
    
    total_cells = len(cells)
    
    print("Total_Cells:",total_cells)
    
    #print("depth_tree",max_path_dict)
    
    parallelism_test = max_depth / total_cells
    print("Test for Parallelism",parallelism_test)
    
    print("cell_dependency_structure",cell_dependency_structure_for_parallelism)
    
    
    print_dependency_graph(g)
    
    return (max_depth,total_cells) 
    


def print_dependency_graph(g):
    
        for v in g:
            if not v.getConnections():
                print(v.getId())
            else:
                for nbr in v.getConnections():
                    print(v.getId(),"->",nbr.getId(),"on",v.getWeight(nbr))  



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
    
    print("Pickled_dependency_dictionary",dependency_dict)
    
    infile.close()


##
## Not used.
##

def calc_input_provenance(source):
    
    vis = Visitast()        
    
    in_built_functions = ['print','int','float','min','udiff','input','len','NotImplementedError','max','ValueError','round','nop','sigmoid','logic_gate','test','open','sum','list','collections.defaultdict']
        
    removal_list = ['%matplotlib','notebook','inline']
    
    tree = ast.parse(source)
    vis.visit(tree)
    
    main_flow_left_dict = vis.display_left_dict()
    
    inverted_left_dict = defaultdict(list)
                
    input_provenance_variable = list()            
            
    for k, v in main_flow_left_dict.items():
        for elem in v:
            inverted_left_dict[elem].append(k)
    
    
    for key,value in vis.display_right_dict().items():
        
        for j in value:    
                if j not in inverted_left_dict:  
                    ## Suggesting that the variable was not defined or declared in the current cell
                    input_provenance_variable.append(j)
                    
    
    for key_line,dict_loop in vis.display_loop_dictionaries().items():
                    
        dict_left = dict_loop[0]
        dict_right = dict_loop[1]                
                    
        inverted_loop_left_dict  = defaultdict(list) 
        for k, v in dict_left.items():                
            for elem in v:
                inverted_loop_left_dict[elem].append(k)
                    
        for key,value in dict_right.items():
            for j in value:    
                if (j not in inverted_loop_left_dict) and (j not in inverted_left_dict):
                    input_provenance_variable.append(j)
                                
    
    for key_line,dict_loop in vis.display_func_dictionaries().items():
                    
        dict_left_func = dict_loop[0]
        dict_right_func = dict_loop[1]                
                    
        inverted_func_left_dict  = defaultdict(list) 
        for k, v in dict_left_func.items():
            for elem in v:
                inverted_func_left_dict[elem].append(k)                    
        
        for key,value in dict_right_func.items():            
            for j in value:
                if (j not in inverted_func_left_dict) and (j not in inverted_left_dict):
                    input_provenance_variable.append(j)
    
    
    for key_line,dict_loop in vis.display_control_flow_dictionaries().items():
                    
        dict_left_control = dict_loop[0]
        dict_right_control = dict_loop[1]                
                    
        inverted_control_left_dict  = defaultdict(list) 
        for k, v in dict_left_control.items():
            for elem in v:
                inverted_control_left_dict[elem].append(k)
        
        for key,value in dict_right_control.items():            
            for j in value:
                if (j not in inverted_control_left_dict) and (j not in inverted_left_dict):
                    input_provenance_variable.append(j)    

    print(input_provenance_variable)
    



##
## The following code inside main function parses the jupyter notebook and generates the dependency graph
##


def parse_notebook(out):
    
    in_built_functions = ['print','int','float','min','udiff','input','len','NotImplementedError','max','ValueError','round','nop','sigmoid','logic_gate','test','open','sum','list','collections.defaultdict']
    
    g = Graph()
    
    cell_dict = dict()
    
    funct_cell_Dict = {}
    
    cell_dict_control_flow = dict()
    
    cell_execution_count_manual = 1
    
    input_provenance_variable = {} 
    
    
    
    for cell in out.cells:
        if cell.cell_type == 'code':
            input_provenance_variable[cell_execution_count_manual] = []
            vis = Visitast()        
            
            removal_list = ['%matplotlib','notebook','inline']
            
            for word in removal_list:
                cell.source = cell.source.replace(word, "")
            
            
            tree = ast.parse(cell.source)
            vis.visit(tree)
        
            
            #print("Control Flow Assignments",control_flow_dict.items())
            

            if len(vis.display_left_dict()) != 0:
                
                print("Right dict",vis.display_right_dict())
                print("Left dict",vis.display_left_dict())
                print("function Dict",vis.display_func_dictionaries())
                print("Loop dictionary",vis.display_loop_dictionaries())
                
                
                for key,value in vis.display_left_dict().items():
                                 
                    for j in value:
                            
                        if j not in cell_dict: 
                            cell_dict[j] = [(cell_execution_count_manual,key)] 
                        else:
                            cell_dict[j].append((cell_execution_count_manual,key))        
                        
                    cell_dict[j].sort(reverse = True)
                
            
        
                left_dict = vis.display_left_dict()
                inverted_left_dict = defaultdict(list)
                
                
            
                for k, v in vis.display_left_dict().items():
                    for elem in v:
                        inverted_left_dict[elem].append(k)
                
                
                for key,value in vis.display_right_dict().items():
                    
                    for j in value:
                        
                        key_left_dict = []
                        if j in inverted_left_dict: 
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
                        #print("Key,Key_left",key,key_left_dict,isOrphan)    
                        #print(j,left_dict.values(),isOrphan)
                        
                        if ((j not in left_dict.values() or isOrphan == True) and (j not in in_built_functions)):
                            
                            if j not in input_provenance_variable[cell_execution_count_manual]:
                                input_provenance_variable[cell_execution_count_manual].append(j)
                            
                            if j in cell_dict:
                                references = cell_dict[j] 
                                #print("References",references,j)
                            
    
                                for data in references:
                                    if data != (cell_execution_count_manual,key) and not (data[0] == cell_execution_count_manual and data[1] > key ):
                                        #print("Func dep data",data,(cell_execution_count_manual,key),j)
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
                        
                
                        if j in funct_cell_Dict.keys():
                            
                            
                            dependency_main_program_dict = funct_cell_Dict[j]
                            
                            
                            for dependency_elem in dependency_main_program_dict:
                            
                                previous_cell_dependency_details_cell = dependency_elem[0]
                                previous_cell_dependency_details_var = dependency_elem[1]
                                 
                                g.addEdge((previous_cell_dependency_details_cell[0],previous_cell_dependency_details_cell[1]),(cell_execution_count_manual,key),previous_cell_dependency_details_var)
                             
                             
                for key_line,dict_loop in vis.display_func_dictionaries().items():
                    
                    dict_left_func = dict_loop[0]
                    dict_right_func = dict_loop[1]                
                    
                    inverted_func_left_dict  = defaultdict(list) 
                    for k, v in dict_left_func.items():
                        for elem in v:
                            inverted_func_left_dict[elem].append(k)
                    
                                
                    for key,value in dict_right_func.items():
                        #print("Value",value)
                        for j in value:
                            #print("j",j)
                            key_left = inverted_func_left_dict.get(j, None)
                            if key_left is not None:
                                for key_left_dict in key_left:
                                    if key_left_dict < key: 
                                        g.addEdge((cell_execution_count_manual,key_left_dict),(cell_execution_count_manual,key),j)
                            
                            elif key_left is None:
                                key_left_main = inverted_left_dict.get(j,None)
                                
                                if j not in input_provenance_variable[cell_execution_count_manual]:
                                    input_provenance_variable[cell_execution_count_manual].append(j)
                                
                                if key_left_main: 
                                    for k in key_left_main:
                                        if k < key:
                                            g.addEdge((cell_execution_count_manual,k),(cell_execution_count_manual,key),j)
                                
                                elif j in cell_dict:
                                    print("Inside func_dependency:",key_line,j)
                                    references = cell_dict[j] 
                                    funct_cell_Dict[key_line] = []
                                    
                                    for data in references:
                                        if data != (cell_execution_count_manual,key) and not (data[0] == cell_execution_count_manual and data[1] > key ):
                                            
                                            funct_cell_Dict[key_line].append((data,j)) 
                                            
                                            g.addEdge(data,(cell_execution_count_manual,key),j)
                                        
                                            try:
                                                (cell,line) = cell_dict_control_flow[j]
                                            except KeyError:
                                                break
                                         
                                            if (cell == data[0]) and (data[1] == line):
                                                continue
                                            else:
                                                break              
                            
                            
                            
                            
                            
                for key_line,dict_loop in vis.display_loop_dictionaries().items():
                    
                    dict_left = dict_loop[0]
                    dict_right = dict_loop[1]                
                    
                    inverted_loop_left_dict  = defaultdict(list) 
                    for k, v in dict_left.items():
                        for j in v:
                            
                            if j not in cell_dict: 
                                cell_dict[j] = [(cell_execution_count_manual,key)] 
                            else:
                                cell_dict[j].append((cell_execution_count_manual,key))        
                        
                        cell_dict[j].sort(reverse = True)
                    
                        for elem in v:
                            inverted_loop_left_dict[elem].append(k)
            
            
                    for key,value in dict_right.items():
                        print("Value",value)
                        for j in value: #and (j not in in_built_functions):
                            #print("j",j)
                            key_left = inverted_loop_left_dict.get(j, None)
                            if key_left is not None:
                                for key_left_dict in key_left:
                                    if key_left_dict < key: 
                                        g.addEdge((cell_execution_count_manual,key_left_dict),(cell_execution_count_manual,key),j)
                            
                            elif key_left is None:
                                if j not in input_provenance_variable[cell_execution_count_manual]:
                                    key_left_main = inverted_left_dict.get(j,None)
                                input_provenance_variable[cell_execution_count_manual].append(j)
                                if key_left_main: 
                                    for k in key_left_main:
                                        if k < key:
                                            g.addEdge((cell_execution_count_manual,k),(cell_execution_count_manual,key),j)
                                
                
                                

                for key_line,dict_loop in vis.display_control_flow_dictionaries().items():
                    
                    dict_left_control = dict_loop[0]
                    dict_right_control = dict_loop[1]                
                    
                    inverted_control_left_dict  = defaultdict(list) 
                    for k, v in dict_left_control.items():
                        for elem in v:
                            inverted_control_left_dict[elem].append(k)
            
            
                    for key,value in dict_right_control.items():
                        #print("Value",value)
                        for j in value:
                            #print("j",j)
                            key_left = inverted_control_left_dict.get(j, None)
                            if key_left is not None:
                                for key_left_dict in key_left:
                                    if key_left_dict < key: 
                                        g.addEdge((cell_execution_count_manual,key_left_dict),(cell_execution_count_manual,key),j)
                            
                            elif key_left is None:
                                key_left_main = inverted_left_dict.get(j,None)
                                if j not in input_provenance_variable[cell_execution_count_manual]:
                                    input_provenance_variable[cell_execution_count_manual].append(j)
                                if key_left_main: 
                                    for k in key_left_main:
                                        if k < key:
                                            g.addEdge((cell_execution_count_manual,k),(cell_execution_count_manual,key),j)                                        
                
                
                
            cell_execution_count_manual += 1 
                                        
            #print(cells.source)
            #print(vis.display_left_dict())
            #print(vis.display_right_dict())
            #print(cell_dict)
    
    print("Input provenance details",input_provenance_variable)    
    #infile = pickle_export(g)
    #pickle_read_dependency(infile)
    
    print(funct_cell_Dict)
    
    return calc_degree_parallelism(g)    

##
## Ignore - WAs used for development and testing
##

def main():
    #out = nb.read("D:/VizierDB-JupyterIntegration/src/test_vizier.ipynb",as_version=4)
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Discontinuous Galerkin Method/dg_elastic_hetero_1d.ipynb",as_version=4) 
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Discontinuous Galerkin Method/dg_elastic_homo_1d.ipynb",as_version=4) 
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Discontinuous Galerkin Method/dg_elastic_homo_1d_solution.ipynb",as_version=4) 
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Discontinuous Galerkin Method/dg_scalar_advection_1d.ipynb",as_version=4) 
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/ac1d_optimal_operator.ipynb",as_version=4) 
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/ac1d_optimal_operator_with_solutions.ipynb",as_version=4) 
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_ac1d.ipynb",as_version=4) 
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_ac1d_with_solutions.ipynb",as_version=4) 
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_ac2d_heterogeneous.ipynb",as_version=4) 
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_ac2d_heterogeneous_solutions.ipynb",as_version=4) 
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_ac2d_homogeneous.ipynb",as_version=4) 
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_ac2d_homogeneous_solutions.ipynb",as_version=4) 
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_ac3d_homogeneous.ipynb",as_version=4)
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_ac3d_homogeneous_solutions.ipynb",as_version=4)

    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_advection_1d.ipynb",as_version=4)
    
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_advection_1d_solutions.ipynb",as_version=4)
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_advection_diffusion_reaction.ipynb",as_version=4)
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_advection_diffusion_reaction_solution.ipynb",as_version=4)
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_elastic1d_staggered.ipynb",as_version=4)
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_elastic1d_staggered_solution.ipynb",as_version=4)
    
    out = nb.read("D:/Workspace/PythonAST/notebooks/test_notebooks/Week10_Text-Word_Vectors_HW.ipynb",as_version=4)
    
    parse_notebook(out)
    
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_seismometer_solution.ipynb",as_version=4)
    
    #out = nb.read("D:/VizierDB-JupyterIntegration/test_notebooks/002db2f3c193fa87be97b1fac814d577b6f1aa/002db2f3c193fa87be97b1fac814d577b6f1aa/notebooks/Computational Seismology/The Finite-Difference Method/fd_taylor_operators.ipynb",as_version=4)
    
    
    
    
    
    
            
if __name__ == '__main__':
    main() 
    







#print(json.load(out))

#print(pickle.load("D:/Workspace/PythonAST/src/Index.ipynb"))

#print(type(out))

