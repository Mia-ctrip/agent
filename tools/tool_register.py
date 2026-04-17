'''
注册工具函数
'''
from typing import Any, Dict

class ToolRegistry:

    def __init__(self):
        self.tools : Dict[str, Dict] = {}

    def register(self,
                 type:str,
                 name:str,
                 description:str,
                 params:dict,
                 func:callable
                 ):
        self.tools[name] = {
            "type": type,
            "description": description,
            "params": params,
            "func": func
        }

    def get_openai_function_definitions(self):
        function_definitions = []
        for name, tool in self.tools.items():
            function_definitions.append({
                "type": tool["type"],
                "function":{
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["params"]
                }
            })
        return function_definitions    

    def get_anthropic_function_definitions(self):
        function_definitions = []
        for name, tool in self.tools.items():
            function_definitions.append({
                "name": name,
                "description": tool["description"],
                "input_schema": tool["params"]
            })
        return function_definitions
    
    def call_function(self,name,**kwargs):
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        tool = self.tools[name]
        return tool["func"](**kwargs)
    

    

    