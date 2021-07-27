'''
Created on 02-Jul-2021

@author: Nachiket Deo
'''

import json

class export_workflow:
    
    def __init__(self,Id,createdAt,action,packageId,commandId,actionModule,modules):
        
        self.id = Id,
        self.createdAt = createdAt,
        self.action = action,
        self.packageId = packageId,
        self.commandId = commandId,
        self.actionModule = actionModule,
        self.modules = modules
    
    def return_workflow(self):
        
        workflow = {}
        workflow['id'] = self.id,
        workflow['createdAt'] = self.createdAt,
        workflow['action'] = self.action,
        workflow['packageId'] = self.packageId,
        workflow['commandId'] = self.commandId,
        workflow['actionModule'] = self.actionModule,
        workflow['modules'] = self.modules
        
        return workflow
        
        
        
        
        
