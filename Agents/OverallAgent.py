from llama_index.core.agent import ReActAgent
from llama_index.llms.groq import Groq
from llama_index.core.tools import FunctionTool
from Agents.KeyBoardAgent import KeyboardAgent
from Agents.VisionMouseAgent import MouseController
import os
from dotenv import load_dotenv

class MasterAgent():

    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardAgent()
        load_dotenv('Agents\.env')
        self.llm = Groq(model="llama3-70b-8192", api_key=os.environ.get('GROQ_API_KEY'),temperature = 0.6)
        pass

    def agent_res(self,query):

        tools = [
            FunctionTool.from_defaults(
                fn = self.mouse.agent_res,
                name = "mouse_agent",
                description = "This tool takes step by step mouse controlling instructions to control the mouse"
            ),
            FunctionTool.from_defaults(
                fn = self.keyboard.keyagent,
                name = "keyboard_agent",
                description = "This tool takes step by step keyboard controlling instructions to control the keyboard"
            ),
        ]

        agent = ReActAgent.from_tools(tools = tools, llm=self.llm, context="""
                Role : Computer Controlling agent.
                SYSTEM PROMPT:
                ---------------
                You are a Computer Controlling Agent (CCA) with access to two sub-agents: "mouse_agent" and "keyboard_agent". Your mission is to translate user instructions into a series of clear, step-by-step commands that leverage these agents to manipulate the computer interface.

                Tools: 
                - **mouse_agent**: Capable of viewing UI elements on screen, moving the mouse, and executing click actions.
                - **keyboard_agent**: Capable of typing text and executing keyboard shortcuts (hotkeys).

                Instructions:
                1. Break down the user's instruction into logical steps.
                2. Assign each step to either the mouse_agent or the keyboard_agent.
                3. Ensure each step is clear, sequential, and includes any necessary conditions (e.g., waiting for an element to appear).
                4. keyboard_agent accepts natural language string query as input.
                5. mouse_agent accepts natural language string query as input

                Example Usage:
                ---------------
                User Instruction: "Open spotify and play Guns for hire song"

                Step-by-Step Breakdown:
                1. **Step 1: Open spotify**
                - **Command**: `keyboard_agent("Open spotify")`

                2. **Step 3: Click on the search bar**
                - **Command**: `mouse_agent("click on the search bar")`
                                      
                3. **Step 3: Type the song name "Guns for hire" **
                - **Command**: `keyboard_agent("Type 'Guns for hire' ")`

                4. **Step 4: Locate and click the play button**
                - **Command**: `mouse_agent("click the play button")`

                ------------------------------------------------------------
                                                     
                User Instruction: "Open amazon.in on google and searc for headphones"

                Step-by-Step Breakdown:
                1. **Step 1: Open amazon.in on google**
                - **Command**: `keyboard_agent("Open amazon.in on google")`

                2. **Step 3: Click on the search bar**
                - **Command**: `mouse_agent("click on the search bar")`
                                      
                3. **Step 3: Type the product name "Headphones" **
                - **Command**: `keyboard_agent("Type 'headphones' and hit enter")`
                                      
            Secret Tips : 
            - For search in spotify use the keyboard_agent to press Ctrl+K and search for songs""", max_iterations=20)
        
        res = agent.query(query)

        return res.response
    
if __name__ == "__main__":
    agent = MasterAgent()
    try:
        while True:
            query = input("User> ")
            if query == "/q":
                print("Stopped...")
                break
            print(agent.agent_res(query))

    except KeyboardInterrupt:
        print("\nTracking stopped.")