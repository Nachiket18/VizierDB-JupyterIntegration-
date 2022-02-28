'''
Created on 02-Jul-2021

@author: Nachiket Deo
'''

import json



class export_module:
    
    
    def return_module(self,Id: int,state: int,command,text:dict,timestamps):
        
        module = dict(id= 0,state = 0,command = 0,text= {},timestamps= {})
        module['id'] = Id
        module['state'] = state
        module['command'] = command
        module['text'] = text
        module['timestamps'] = timestamps

        return module
        
        
        
        
        
        
        
        
