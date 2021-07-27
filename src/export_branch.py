'''
Created on 02-Jul-2021

@author: Nachiket Deo
'''

import json

class export_branch:
    
    def __init__(self,Id,createdAt,lastModifiedAt,sourceBranch,sourceWorkflow,isDefault,properties,workflows):
        
        self.id = Id,
        self.createdAt = createdAt,
        self.lastModifiedAt = lastModifiedAt,
        self.sourceBranch = sourceBranch,
        self.sourceWorkflow = sourceWorkflow,
        self.isDefault = isDefault,
        self.properties = properties,
        self.workflows = workflows
    
    def return_branch(self):
        
        branch = {}
        
        branch['Id'] = self.id ,
        branch['createdAt'] = self.createdAt,
        branch['lastModifiedAt'] = self.lastModifiedAt ,
        branch['sourceBranch'] = self.sourceBranch,
        branch['sourceWorkflow'] = self.sourceWorkflow ,
        branch['isDefault'] = self.isDefault,
        branch['properties'] = self.properties,
        branch['workflows'] = self.workflows
        
        return branch
        
        
        
        
        
