from Tools.mouse import Mousepy
from pydantic import BaseModel
from llama_index.core.agent import ReActAgent
from llama_index.llms.groq import Groq
from llama_index.core.tools import FunctionTool
from groq import Groq as Gq
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, load_index_from_storage,StorageContext
from llama_index.core.node_parser import SentenceSplitter
from Tools.ScreentoXML_OCR import stx
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
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
        self.stx = stx()
        load_dotenv('Agents\.env')
        self.llm = Groq(model="llama3-70b-8192", api_key=os.environ.get('GROQ_API_KEY'),temperature = 0.6)
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
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
            FunctionTool.from_defaults(
                fn=self.screen_information,
                name="screen_info",
                description="Based on given information in the query, approximate positions ui elements",
                fn_schema=TrackPositionSchema  # Use the Pydantic model instead of a dictionary
            ),
            FunctionTool.from_defaults(
                fn=self.vision_agent,
                name="vision_agent",
                description="Based on given information in the query, it gives information about whats on screen",
                fn_schema=TrackPositionSchema  # Use the Pydantic model instead of a dictionary
            )
        ]

        context = """ Role : Mouse Controller Agent
        Instructions:
        - You are supposed to analyze the query and perform any relevant mouse tasks necessary.
        - Only perform mouse controlling tasks.
        - You have the tools : click_left, click_right, get_position, move_to, track_position, screen_info, vision_agent.
        - Only use the above tools to perform mouse tasks.
        - Use screen_info tool for estimating location of ui elements on screen.
        - Do not hallucinate location of ui elements on screen
        - Use Vision agent to get information about the information on screen
        - Usage Instructions for screen_info tool:
            1. Get basic information about current mouse position and pass it along with query to screen_info tool.
                Eg: what is the position of the minimize button.
            2. Use screen_info tool to get approximate location of screen ui elements
            3. screen_info tool only accepts natural language query, pass all information in query field along with question.
        - Use vision_agent after each mouse move action to verify location of mouse with respect to target.
            Example: "Is the mouse on the Icon?"
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
    def vision_agent(self, query:str)->str:
        client = Gq(api_key="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")
        base64_image = self.mouse.capture_screenshot_with_cursor()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{query}. The mouse is considered as the Red Mouse on screen."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-90b-vision-preview",
        )

        return chat_completion.choices[0].message.content

    def screen_information(self,query:str) -> str:
        self.stx.extract_all_ui_elements_to_xml()
        docs = SimpleDirectoryReader(input_files=[self.stx.filename]).load_data()
        splitter = SentenceSplitter(chunk_size=100,chunk_overlap=10)
        nodes = splitter.get_nodes_from_documents(docs)
        vector_index = VectorStoreIndex(nodes=nodes,embed_model=self.embed_model)
        query_engine = vector_index.as_query_engine(llm=self.llm)
        response = query_engine.query(query)
        response_text = str(response)
        return response_text

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