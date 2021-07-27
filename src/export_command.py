'''
Created on 02-Jul-2021

@author: Nachiket Deo
'''

import json


class export_command:
    
    def __init__(self,Id,packageId,commandId,arguments,revisionId,properties):
        
        self.Id = Id ,
        self.packageId = packageId ,
        self.commandId = commandId ,
        self.arguments = arguments ,
        self.revisionOfId = revisionId ,
        self.properties = properties
    
    def process_package_command(self,package,command):
        
        packageId = ""
        commandID = ""
        
        if package == 'code' and command == 'code':
            packageId = 'script'
            commandID = 'python'
        elif package == 'markdown' and command == 'code':
            packageId = 'docs'
            commandID = 'markdown' 
        
        #print(packageId,commandID)
        
        return packageId,commandID
    
    def processs_arguments(self,source):
        
        arguments = dict()
        
        arguments['source'] = source
        
        return json.dumps(arguments)
        
    def return_command(self):
        
        command_out = dict()
        
        command_out['id'] = self.Id
        command_out['packageId'] = self.packageId,
        command_out['commandId']= self.commandId,
        command_out['arguments'] = self.arguments,
        command_out['revisionId'] = self.revisionOfId,
        command_out['properties'] = self.properties 
        
        #print(command_out)
        return command_out
        
            
        
        
        
    
    
    