'''
Created on 02-Jul-2021

@author: Nachiket Deo
'''

import json 
import nbformat as nb 
import datetime
import ntpath
from export_module import export_module
from export_command import export_command
from export_workflow import export_workflow
from export_branch import export_branch
from parse_notebook import parse_notebook


class export_project:
    
    
    def __init__(self,properties = None,defaultBranch = None,files = None,modules = None,branches = None,createdAt = None,lastModifiedAt = None):
        
        self.properties = dict()
        self.defaultBranch = str
        self.files = list()
        self.modules = dict()
        self.branches = dict()
        self.createdAt = datetime
        self.lastModifiedAt = datetime
    
    def return_json_project(self,properties = None,defaultBranch = None,files = None,modules = None,branches = None,createdAt = None,lastModifiedAt = None):
        
        project_out = dict()
        
        project_out['properties'] = [properties]
        project_out['defaultBranch']  = defaultBranch
        project_out['files'] = files
        project_out['modules'] = modules
        project_out['branches'] = branches
        project_out['createdAt'] = createdAt
        project_out['lastModifiedAt'] = lastModifiedAt
        
        return project_out  
    
    def path_leaf(self,path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)    
        
def main():
    
    workflows = []
    branches = []
    input_variance = {}

    ##path = "/home/nachiket/python_data_notebooks/extracted_python/final_notebooks_dataset/script221.ipynb"
    
    path = "/home/nachiket/test_notebooks_parallel/Merge.ipynb"
    out = nb.read(path,as_version=4)
    
    cell_id = 1
    
    modules= {}
    

    g_prime = parse_notebook.parse_notebook(out)

    #print(g_prime.getVertices())

    #print(input_variance)

    for cell in out.cells:
        
        if cell.cell_type == 'code':
            #print(cell.source)
            arguments = {}
            Id = cell_id
            state = 4
            text = "null"
        
    
            ##
            ## Getting the JSON for 'command' object
            ##
        
            command_default = export_command(id,None,None,None,None,None)        
            package_id,command_id = command_default.process_package_command(package = cell.cell_type,command = 'code')
            command_properties = {}
            #vertex_list = g_prime.getVertices()
            vertex = g_prime.getVertex(cell_id)

            #print(vertex)
            #print("Source",cell.source)
            #print(vertex.getConnections())
            
            processed_source_pre  = ""
            processed_source_post = "\n"
            
            if vertex is not None:
                tmp_input_provenance_list = []
                vertices_list_input_provenance = list(vertex.getBackConnections())
                for v in vertices_list_input_provenance:
                    if v.getWeight(vertex) not in tmp_input_provenance_list:
                        tmp_input_provenance_list.append(v.getWeight(vertex))
                        processed_source_pre +=  v.getWeight(vertex) + " = vizierdb[" "'" + v.getWeight(vertex) + "'" "]" + "\n"
                command_properties['input_provenance'] = tmp_input_provenance_list
            else:
                command_properties['input_provenance'] = []
            #vertex.getBackConnections()
            if vertex is not None:
                vertices_list_output_provenance = list(vertex.getConnections())
                tmp_output_provenance_list = []
                output_provenance_len = len(vertices_list_output_provenance)-1
                for v in vertices_list_output_provenance:
                    if vertex.getWeight(v) not in tmp_output_provenance_list:
                        tmp_output_provenance_list.append(vertex.getWeight(v))
                        if vertices_list_output_provenance.index(v) == output_provenance_len:
                            processed_source_post += "vizierdb[" "'"  + vertex.getWeight(v) + "'" "] = " + vertex.getWeight(v)    
                        else:
                            processed_source_post += "vizierdb[" "'"  + vertex.getWeight(v) + "'" "] = " + vertex.getWeight(v) + "\n"
                command_properties['output_provenance'] = tmp_output_provenance_list
                 
            else:
                command_properties['output_provenance'] = []
            #vertex.getConnections()
            arguments['id'] = 'source'
            arguments['value'] = processed_source_pre + cell.source + processed_source_post
            #print("id:",Id)
            #print(arguments['source'])
            command_placeholder = export_command(str(Id),package_id,command_id,[arguments],None,command_properties)
            command = command_placeholder.return_command()
        
            #print(command)
        
            timestamp = {}
        
            cureent_date = datetime.datetime.utcnow().isoformat() 
        
            cureent_date = str(cureent_date)
         
            timestamp['createdAt'] = cureent_date
            timestamp['startedAt'] = None
            timestamp['finishedAt'] = None
            timestamp['lastModifiedAt'] = cureent_date

            

        #timestamps = json.dumps(timestamp)
        
        #print(timestamp) 
        
            module_placeholder = export_module()
            module = module_placeholder.return_module(str(Id),state,command,str(text),timestamp)
        
        #print(module) 
            modules[Id] = module
        
            cell_id +=1
     
    
    modules_data = [ str(i) for i in range(1,cell_id)]
    workflow_placeholder = export_workflow(str(1),str(datetime.datetime.now().isoformat()),'create',"null","null","null",modules_data)    
    workflow = workflow_placeholder.return_workflow()    
    workflows.append(workflow)

    properties = {}
    
    head, tail = ntpath.split(path)
    filename = tail 

    properties['key'] = 'name'
    properties['value'] = filename

    branch_id = str(1)
     
    branch_placeholder = export_branch(branch_id,str(datetime.datetime.now().isoformat()),str(datetime.datetime.now().isoformat()),isDefault = True,properties = [properties],workflows = workflows)
    branch = branch_placeholder.return_branch()
    
    branches.append(branch)
    
    project_placeholder = export_project()
    
    project = project_placeholder.return_json_project(properties,"1", [] ,modules,branches,cureent_date,cureent_date)
    
    with open('project_Merge.json', 'w') as outfile:
        json.dump(project, outfile)
    
        

if __name__ == '__main__':
    main() 

