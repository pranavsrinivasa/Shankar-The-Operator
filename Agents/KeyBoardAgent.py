import pyautogui
from llama_index.core.agent import ReActAgent
from llama_index.llms.groq import Groq
from llama_index.core.tools import FunctionTool
from pydantic import BaseModel
from typing import List
from llama_index.core.llms import ChatMessage, ChatResponse
import os
from dotenv import load_dotenv


class HotkeySchema(BaseModel):
    keys: List[str]

class KeyboardAgent:
    def __init__(self):
        load_dotenv('Agents\.env')
        self.llm = Groq(model="llama3-70b-8192", api_key=os.environ.get('GROQ_API_KEY'),temperature = 0.6)
    
    def type_text(self, text:str)->str:
        """Types normal text in a text field."""
        pyautogui.write(text, interval=0.05)
        return f"Typed: {text}"
    
    def press_hotkey(self, keys:List)->str:
        """Presses a Windows hotkey combination."""
        pyautogui.hotkey(keys)
        return f"Pressed: {keys}"
    
    def large_content(self,prompt:str)->str:
        """Used for type large amount of content based on the prompt"""
        res = self.llm.chat(messages=[
                ChatMessage(
                    role="system", content="You are helpful typing assistant."
                ),
                ChatMessage(role="user", content=prompt)
            ])
        self.type_text(str(res))
        return f"Typed: {str(res)}"

    
    def keyagent(self,query):
        tools = [
            FunctionTool.from_defaults(
                fn=self.type_text,
                name = "type_text",
                description= "This is used to type normal text"
            ),
            FunctionTool.from_defaults(
                fn=self.press_hotkey,
                name = "press_hotkey",
                description= "This is used to excecute hotkey shortcuts in windows. Eg: press_hotkey('alt','tab')",
                fn_schema=HotkeySchema,
            ),
            FunctionTool.from_defaults(
                fn=self.large_content,
                name = "large_content",
                description= "This is used to type large body of content by passing an input prompt according to user query",
                fn_schema=HotkeySchema,
            ),
        ]

        agent = ReActAgent.from_tools(llm = self.llm,
                context="""
                Role : Keyboard Agent
                Instructions:
                - You control the keyboard of a computer
                - You are supposed to excecute commands and write text according to user query
                - You have the tools press_hotkey, type_text and large_content
                - press_hotkey is used to excecute shortcuts keys or special keys, here are instructions for press_hotkey usage:
                    1. Use this tool to excecute shortcuts that are relevant to user query
                    2. Example Usage : press_hotkey(['Enter'])
                    3. Example Usage : press_hotkey(['Ctrl','S'])
                    4. Example Usage : press_hotkey(['Ctrl','Shift','S'])
                    5. Use only windows relevant keys.
                - type_text is used to type normal text into a text box.
                - large_content is used to get large body of content. Here is example usage:
                    1. Query : type a research paper
                       large_content('type a research paper')

                - Pass a prompt to large_content that will inform it to type according to user query.
                - Do not hallucinate tool names
                - Do not deviate from instructions
                - Follow Instructions carefully
                
                Examples :
                Query : Open Google Chrome
                Steps : - Open windows search bar : press_hotkey('WIN')
                        - Search for google chrome : type_text('google chrome')
                        - Open google chrome : press_hotkey('Enter')""", tools=tools, max_iterations=20,verbose=True)

        res = agent.query(query)
        print("Done")
        print(type(res.response))
        return str(res.response)

# Example Usage
if __name__ == "__main__":
    keyboard = KeyboardAgent()
    try:
        while True:
            query = input("User> ")
            if query == "/q":
                print("Stopped...")
                break
            print(keyboard.keyagent(query))

    except KeyboardInterrupt:
        print("\nTracking stopped.")
