'''
Created on 02-Jul-2021

@author: Nachiket Deo
'''

import json

class export_branch:
    
    def __init__(self,Id,createdAt,lastModifiedAt,isDefault,properties,workflows):
        
        self.id = Id
        self.createdAt = createdAt
        self.lastModifiedAt = lastModifiedAt
        self.isDefault = isDefault
        self.properties = properties
        self.workflows = workflows
    
    def return_branch(self):
        
        branch = {}
        
        branch['id'] = self.id 
        branch['createdAt'] = self.createdAt
        branch['lastModifiedAt'] = self.lastModifiedAt 
 
        branch['isDefault'] = self.isDefault
        branch['properties'] = self.properties
        branch['workflows'] = self.workflows
        
        return branch
        
        
        
        
        
