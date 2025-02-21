from Tools.mouse import Mousepy
from pydantic import BaseModel
from llama_index.core.agent import ReActAgent
from llama_index.llms.groq import Groq
from llama_index.core.tools import FunctionTool
from typing import Tuple, Optional
import time
import os
from dotenv import load_dotenv

class MoveToSchema(BaseModel):
    x: int
    y: int

class TrackPositionSchema(BaseModel):
    time: int

class MouseController:
    def __init__(self):
        self.mouse = Mousepy()
        
        # Initialize Ollama LLM
        load_dotenv('Agents\.env')
        self.llm = Groq(model="llama3-70b-8192", api_key=os.environ.get('GROQ_API_KEY'),temperature = 0.6)  

    def agent_res(self, query):
        self.tools = [
            FunctionTool.from_defaults(
                fn=self.click_left,
                name="click_left",
                description="Performs a left mouse click at the current position"
            ),
            FunctionTool.from_defaults(
                fn=self.click_right,
                name="click_right",
                description="Performs a right mouse click at the current position"
            ),
            FunctionTool.from_defaults(
                fn=self.get_position,
                name="get_position",
                description="Gets the current mouse position as (x, y) coordinates"
            ),
            FunctionTool.from_defaults(
                fn=self.move_to,
                name="move_to",
                description="Moves the mouse to specified x, y coordinates",
                fn_schema=MoveToSchema  # Use the Pydantic model instead of a dictionary
            ),
            FunctionTool.from_defaults(
                fn=self.track_position,
                name="track_position",
                description="Check the movements of the mouse for the time given as input ",
                fn_schema=TrackPositionSchema  # Use the Pydantic model instead of a dictionary
            ),
        ]

        context = """ Role : Mouse Controller Agent
        Instructions:
        - You are supposed to analyze the query and perform any relevant mouse tasks necessary.
        - Only perform mouse controlling tasks.
        - You have the tools : click_left, click_right, get_position, move_to.
        - Only use the above tools to perform mouse tasks.
        - Do not deviate from the instructions.
        - Strictly Follow the instructions.
        - Only use tools that are relevant to user prompt.
        - Do not use tools that are not relevant to user prompt.
        - Do not use tools that are not mentioned by the user.
        """
        
        # Initialize ReAct agent
        agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=self.llm,
            context=context,
            verbose=True,
            max_iterations=100
        )
        res = agent.query(query)
        print("Done")
        print(type(res.response))
        return str(res.response)

    def click_left(self,*args,**kwargs) -> str:
        """Perform a left mouse click"""
        self.mouse.mouse_left_click()
        return "Left click performed"
        
    def click_right(self,*args,**kwargs) -> str:
        """Perform a right mouse click"""
        self.mouse.mouse_right_click()
        return "Right click performed"
        
    def get_position(self,*args,**kwargs) -> str:
        """Get current mouse position"""
        x, y, pixel_color = self.mouse.mouse_position()
        return f"Current mouse position is ({x}, {y})"
        
    def move_to(self, x: int, y: int,*args,**kwargs) -> str:
        """Move mouse to specified coordinates"""
        self.mouse.move_mouse_to(x, y)
        return f"Mouse moved to ({x}, {y})"
    def track_position(self, time:int) -> str:
        """Check the movements of the mouse for the time of "time" """
        record = self.mouse.track_mouse_position(time)
        res = "\nTime\tPosition\n"
        for i in record.keys():
            res += f"{i}\t{record[i][0]},{record[i][1]}\n"
        return res

# Example usage
if __name__ == "__main__":
    mouse = MouseController()
    try:
        while True:
            query = input("User> ")
            if query == "/q":
                print("Stopped...")
                break
            print(mouse.agent_res(query))

    except KeyboardInterrupt:
        print("\nTracking stopped.")