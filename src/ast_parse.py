'''
Created on 11-May-2021
@author: Nachiket Deo
'''

import ast
from collections import deque,defaultdict
from builtins import isinstance




class Visitast(ast.NodeVisitor):
        
    
    def __init__(self):
        
        self.line_dict_left = defaultdict(list)
        self.line_dict_right = defaultdict(list)
        self.scope_dict_stack = deque()
        self.control_flow_stack = deque()  
        self.output_loop_dicts = defaultdict(list) 
        self.output_control_flow_dicts = defaultdict(list)
        self.output_func_dicts = defaultdict(list)
        self.import_block = False
        self.function_scope_dict_stack = deque()
        
    def generic_visit(self,node):
        #print(node.__class__.__name__)            
        if isinstance(node,ast.Name):     
            
            if not (self.scope_dict_stack or self.control_flow_stack or self.function_scope_dict_stack):
                
                if (isinstance(node.ctx,ast.Store)):
                    self.line_dict_left[node.lineno].append(node.id)
                
                elif(isinstance(node.ctx,ast.Load)):
                    self.line_dict_right[node.lineno].append(node.id)    
            
            elif self.scope_dict_stack:
                
                line_no_control = self.scope_dict_stack[0]
                
                output_control = self.output_loop_dicts[line_no_control]
                
                left_dict_control = output_control[0]
                right_dict_control = output_control[1]
                
                if (isinstance(node.ctx,ast.Store)):
                    left_dict_control[node.lineno] = (node.id)
                
                elif(isinstance(node.ctx,ast.Load)):
                    right_dict_control[node.lineno].append(node.id) 
                
                self.output_loop_dicts[line_no_control] = (left_dict_control,right_dict_control)
            
            elif self.control_flow_stack:
                
                line_no_control = self.control_flow_stack[0]
                
                output_control = self.output_control_flow_dicts[line_no_control]
                
                left_dict_control = output_control[0]
                right_dict_control = output_control[1]
                
                if (isinstance(node.ctx,ast.Store)):
                    left_dict_control[node.lineno] = (node.id)
                
                elif(isinstance(node.ctx,ast.Load)):
                    right_dict_control[node.lineno].append(node.id) 
                
                self.output_control_flow_dicts[line_no_control] = (left_dict_control,right_dict_control)
                  
                
                    
            elif self.function_scope_dict_stack:
                
                line_no_func = self.function_scope_dict_stack[0]
                
                out_loop_func = self.output_func_dicts[line_no_func]
                
                left_dict  = out_loop_func[0]
                right_dict = out_loop_func[1] 
                
                if (isinstance(node.ctx,ast.Store)):
                    left_dict[node.lineno].append(node.id)
                
                elif(isinstance(node.ctx,ast.Load)):
                    right_dict[node.lineno].append(node.id)  
                
                self.output_func_dicts[line_no_func] = (left_dict,right_dict)   
            
            
            else:
                
                line_no = self.scope_dict_stack[0] 
                out_loop = self.output_loop_dicts[line_no]  
                
                left_dict = out_loop[0]
                right_dict = out_loop[1]
            
                
#                 if (isinstance(node.ctx,ast.Store)):
#                     left_dict[node.lineno].append(node.id)
#                 elif(isinstance(node.ctx,ast.Load)):
#                     right_dict[node.lineno].append(node.id)
                
                self.output_loop_dicts[line_no] = (left_dict,right_dict)
                
                
                
           
        elif isinstance(node,(ast.arg)) and self.function_scope_dict_stack:
            
    
            func_lineno = self.function_scope_dict_stack[0]
            
            out_func_dict =  self.output_func_dicts[func_lineno]
            
            left_dict = out_func_dict[0]
            right_dict = out_func_dict[1]
            
            left_dict[node.lineno].append(node.arg)
                
            self.output_func_dicts[func_lineno] = (left_dict,right_dict)
      
            
        elif isinstance(node,(ast.FunctionDef)):
            
            dict_loop_left  = defaultdict(list)
            dict_loop_right = defaultdict(list)
            self.function_scope_dict_stack.append(node.name)
            self.output_func_dicts[node.name] = (dict_loop_left,dict_loop_right)
                          
        
        elif isinstance(node,(ast.For,ast.While)):
            
            dict_loop_left  = defaultdict(list)
            dict_loop_right = defaultdict(list)
            self.scope_dict_stack.append(node.lineno)
            self.output_loop_dicts[node.lineno] = (dict_loop_left,dict_loop_right)
        
        elif isinstance(node,ast.If):
            
            dict_loop_left  = defaultdict(list)
            dict_loop_right = defaultdict(list)
            self.control_flow_stack.append(node.lineno)
            self.output_control_flow_dicts[node.lineno] = (dict_loop_left,dict_loop_right) 
        
        elif isinstance(node,(ast.Import,ast.ImportFrom)):
            self.import_block = True
        
    
        elif self.import_block == True:
            if node.asname != None:
                self.line_dict_left[0].append(node.asname)
            else:
                self.line_dict_left[0].append(node.name)
                
        
        #if isinstance(node,ast.Call):           
            
        
        
        ast.NodeVisitor.generic_visit(self,node)
            
        
        if isinstance(node,(ast.For,ast.While)):
            self.scope_dict_stack.pop()
        
        elif isinstance(node,(ast.If)):
            self.control_flow_stack.pop()
        
        elif isinstance(node,(ast.Import,ast.ImportFrom)):
            self.import_block = False
        
        elif isinstance(node,(ast.FunctionDef)):
            self.function_scope_dict_stack.pop()
        
    
    def display_left_dict(self):
        return self.line_dict_left
    
    def display_right_dict(self):
        return self.line_dict_right
    
    def display_loop_dictionaries(self):
        return self.output_loop_dicts
    
    def display_control_flow_dictionaries(self):
        return self.output_control_flow_dicts
    
    def display_func_dictionaries(self):
        return self.output_func_dicts
            
            
class Vertex:
    def __init__(self,key):
        self.id = key
        self.connectedTo = {}

    def addNeighbor(self,nbr,dep_object = ''):
        self.connectedTo[nbr] = dep_object

    def __str__(self):
        return str(self.id) + ' connectedTo: ' + str([x.id for x in self.connectedTo])

    def getConnections(self):
        return self.connectedTo.keys()

    def getId(self):
        return self.id

    def getWeight(self,nbr):
        return self.connectedTo[nbr]

class Graph:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertList[key] = newVertex
        return newVertex

    def getVertex(self,n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertList

    def addEdge(self,f,t,dep_object=''):
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList:
            nv = self.addVertex(t)
        self.vertList[f].addNeighbor(self.vertList[t], dep_object)

    def getVertices(self):
        return self.vertList.keys()

    def __iter__(self):
        return iter(self.vertList.values())    


def main():
    
    with open("D:/Workspace/PythonAST/src/example.py", "r") as source:
        tree = ast.parse(source.read())
    
    #tree = ast.parse("x = 1; y=1; y=y+2; x = y+5")
    
    print(ast.dump(tree, indent=4))
    
    vis = Visitast()
    vis.visit(tree)
    print(vis.display_left_dict())
    print(vis.display_right_dict())
    print(vis.display_loop_dictionaries())
    print("Func",vis.display_func_dictionaries())
    #for node in ast.walk(tree):
    #    line_dict = {}
    #    print(node.__class__.__name__)
    
    g = Graph()
    
    for key,value in vis.display_left_dict().items():
        g.addVertex(key)
    
    for key,value in vis.display_loop_dictionaries().items():
        dict_left = value[0]
        dict_right = value[1]
        for key,value in dict_left.items():
            g.addVertex(key)
            
        for key,value in dict_right.items():
            if g.getVertex(key) == None:
                g.addVertex(key)
                
    dependency_list = defaultdict(list)
    
    inverted_left_dict = defaultdict(list)
     
    for k, v in vis.display_left_dict().items():
            for elem in v:
                inverted_left_dict[elem].append(k)
        
#     for key,value in vis.line_dict_right.items():
#         for key_1,value_1 in vis.line_dict_left.items():
#             if value == value_1 and key_1 < key:
#                 dependency_list[key_1] = (key,value)
    
    print("D2",inverted_left_dict)
     
    for key,value in vis.display_right_dict().items():
            for j in value:
                key_left = inverted_left_dict[j]
                key_left.sort(reverse = True)
                if isinstance(key_left,list):
                    for k in key_left:
                        if k < key:
                            dependency_list[k].append((key,j))
                            break
    #print(dependency_list) 
    for key_line,dict_loop in vis.display_loop_dictionaries().items():
             
            dict_left = dict_loop[0]
            dict_right = dict_loop[1]
            
            d3 = defaultdict(list) 
            for k, v in dict_left.items():
                for elem in v:
                    d3[elem].append(k)
        
            
            print("d3",d3)
            for key,value in dict_right.items():
                    print("Value",value)
                    for j in value:
                        print("j",j)
                        key_left = d3.get(j, None)
                        if key_left is not None:
                            for key_left_dict in key_left:
                                if key_left_dict < key: 
                                    dependency_list[key_left_dict].append((key,j))
                        
                        elif key_left is None:
                            key_left_main = inverted_left_dict.get(j,None)
                            print("Key",key_left_main,key_left)
                            if key_left_main: 
                                for k in key_left_main:
                                    if k < key:
                                        dependency_list[k].append((key,j))
                                    
                    
    
    
    
    for key,value in dependency_list.items():
        for data in value:
            elem_1,elem_2 = data
            g.addEdge(key,elem_1,elem_2) 
    
    
    #print(dependency_list)
     
    for v in g:
        if not v.getConnections():
            print(v.getId())
        else:
            for nbr in v.getConnections():
                print(v.getId(),"->",nbr.getId(),"on",v.getWeight(nbr))
            
        

if __name__ == '__main__':
    main() 