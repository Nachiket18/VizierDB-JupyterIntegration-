'''
Created on 17-May-2021

@author: Nachiket Deo
'''

import nbformat as nb 
import ast


from src.ast_parse import visitAST,Graph


def main():
    out = nb.read("D:/Workspace/PythonAST/src/Index.ipynb",as_version=4)
    #print(out)
    
    g = Graph()
    
    cell_dict = dict()
    for cell in out.cells:
        if cell.cell_type == 'code':
    
            vis = visitAST()        
            tree = ast.parse(cell.source)
            
            print(ast.dump(tree, indent=4))
            
            vis.visit(tree)
            
            for key,value in vis.display_left_dict().items():
      
                if value not in cell_dict: 
                    cell_dict[value] = [(cell.execution_count,key)]
                     
                else:
                    cell_dict[value].append((cell.execution_count,key))        
            
            for key,value in vis.display_right_dict().items():
                left_dict = vis.display_left_dict()
                keys = [key for key, val in left_dict.items() if val == value]
                
                isOrphan = False
                
                for elem in keys:
                    if key <= elem:
                        isOrphan = True
                
                if value not in left_dict.values() or isOrphan == True:
                    references = cell_dict[value]
                    for data in references:
                        if data != (cell.execution_count,key):
                            g.addEdge(data,(cell.execution_count,key),value)
                
                else:

                    for elem in keys:
                        if elem != key: 
                            g.addEdge((cell.execution_count,elem),(cell.execution_count,key),value)
                    
                        
            #print(cells.source)
            print(vis.display_left_dict())
            print(vis.display_right_dict())
            print(cell_dict)
    
    for v in g:
        if not v.getConnections():
            print(v.getId())
        else:
            for nbr in v.getConnections():
                print(v.getId(),"->",nbr.getId(),"on",v.getWeight(nbr))        
            

                
            
            
                
if __name__ == '__main__':
    main() 
    
    







#print(json.load(out))

#print(pickle.load("D:/Workspace/PythonAST/src/Index.ipynb"))

#print(type(out))

