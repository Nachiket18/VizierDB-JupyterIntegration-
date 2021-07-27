'''
Created on 02-Jul-2021

@author: Nachiket Deo
'''

import json 
import nbformat as nb 
import datetime
import ntpath
from src.export_module import export_module
from src.export_command import export_command
from src.export_workflow import export_workflow
from src.export_branch import export_branch



class export_project:
    
    
    def __init__(self,properties = None,defaultBranch = None,files = None,modules = None,branches = None,createdAt = None,lastModifiedAt = None):
        
        self.properties = dict(),
        self.defaultBranch = int,
        self.files = list(),
        self.modules = dict(),
        self.branches = dict(),
        self.createdAt = datetime,
        self.lastModifiedAt = datetime
    
    def return_json_project(self,properties = None,defaultBranch = None,files = None,modules = None,branches = None,createdAt = None,lastModifiedAt = None):
        
        project_out = dict()
        
        project_out['properties'] = properties,
        project_out['defaultBranch']  = defaultBranch,
        project_out['files'] = files,
        project_out['modules'] = modules,
        project_out['branches'] = branches,
        project_out['createdAt'] = createdAt,
        project_out['lastModifiedAt'] = lastModifiedAt
        
        return json.dumps(project_out)  
    
    def path_leaf(self,path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)    
        
def main():
    
    workflows = {}
    branches = {}
    
    path = "D:/VizierDB-JupyterIntegration/src/test_vizier.ipynb"
    out = nb.read(path,as_version=4)
    
    cell_id = 1
    
    modules= {}
    
    for cell in out.cells:
        
        arguments = {}
        Id = cell_id
        state = 4
        text = None
        
        ##
        ## Getting the JSON for 'command' object
        ##
        
        command_default = export_command(id,None,None,None,None,None)
        
        #print(cell.cell_type)
        
        package_id,command_id = command_default.process_package_command(package = cell.cell_type,command = 'code')
        
        arguments['source'] = cell.source
        
        command_placeholder = export_command(Id,package_id,command_id,arguments,None,None)
        
        command = command_placeholder.return_command()
        
        #print(command)
        
        timestamp = {}
        
        cureent_date = datetime.datetime.now() 
        
        cureent_date = str(cureent_date)
         
        timestamp['createdAt'] = cureent_date
        timestamp['startedAt'] = None
        timestamp['finishedAt'] = None
        timestamp['lastModifiedAt'] = cureent_date
         
        #timestamps = json.dumps(timestamp)
        
        #print(timestamp) 
        
        module_placeholder = export_module()
        module = module_placeholder.return_module(Id,state,command,text,timestamp)
        
        #print(module) 
        modules[Id] = module
        cell_id +=1
     
    workflow_id = 1
    workflow_placeholder = export_workflow(workflow_id,str(datetime.datetime.now()),'create',None,None,None,modules)    
    workflow = workflow_placeholder.return_workflow()    
    workflows[workflow_id] = workflow
     
    branch_id = 1
     
    branch_placeholder = export_branch(branch_id,str(datetime.datetime.now()),str(datetime.datetime.now()),None,None,isDefault = True,properties = None,workflows = workflows)
    branch = branch_placeholder.return_branch()
    
    branches['Id'] = branch
    
    head, tail = ntpath.split(path)
    filename = tail  
    
    properties = {}
    
    properties['name'] = filename
     
    project_placeholder = export_project()
    
    project = project_placeholder.return_json_project(properties,1,None,modules,branches,cureent_date,cureent_date)
    
    print(project)
    
    with open('D:\Workspace\PythonAST\src\project.json', 'w') as outfile:
        json.dump(project, outfile)
    
    
    
         
        
        

if __name__ == '__main__':
    main() 

