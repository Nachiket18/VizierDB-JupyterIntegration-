'''
Created on 11-May-2021

@author: Nachiket Deo
'''
import ast
from _ast import Is


class visitAST(ast.NodeVisitor):
    
    
    
    def __init__(self):
        
        self.line_dict_left = {}
        self.line_dict_right = {}
    
    def generic_visit(self,node):
        #print(node.__class__.__name__)
        if isinstance(node,ast.Name):  
            if (isinstance(node.ctx,ast.Store)):
                self.line_dict_left[node.lineno] = node.id
                
            elif(isinstance(node.ctx,ast.Load)):
                self.line_dict_right[node.lineno] = node.id
                      
        
        ast.NodeVisitor.generic_visit(self,node)
    
    def display_left_dict(self):
        return self.line_dict_left
    
    def display_right_dict(self):
        return self.line_dict_right
    
            
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
    
    vis = visitAST()
    vis.visit(tree)
    print(vis.line_dict_left)
    print(vis.line_dict_right)
    #for node in ast.walk(tree):
    #    line_dict = {}
    #    print(node.__class__.__name__)
    
    g = Graph()
    
    for i in range(len(vis.line_dict_left)):
        g.addVertex(i)
     
    dependency_list = {}
     
    for key,value in vis.line_dict_right.items():
        for key_1,value_1 in vis.line_dict_left.items():
            if value == value_1 and key_1 < key:
                dependency_list[key_1] = (key,value)
     
    for key,value in dependency_list.items():
        elem_1,elem_2 = value
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