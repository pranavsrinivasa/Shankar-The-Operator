import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
from Agents.OverallAgent import MasterAgent

class TerminalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shankar-The-Operator")
        
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=80)
        self.text_area.pack(padx=10, pady=10)
        self.text_area.config(state=tk.DISABLED)
        
        self.entry = tk.Entry(root, width=80)
        self.entry.pack(padx=10, pady=5)
        self.entry.bind("<Return>", self.process_query)
        
        self.original_stdout = sys.stdout  # Store original stdout
        
        # Display welcome message
        self.append_text("Hello, I am Shankar-the-Operator. How may I help you?\n")

    def process_query(self, event=None):
        query = self.entry.get()
        if query.strip():
            self.entry.delete(0, tk.END)
            self.append_text(f"> {query}\n")
            threading.Thread(target=self.run_operator, args=(query,), daemon=True).start()
    
    def run_operator(self, query):
        sys.stdout = self 
        self.operator(query)
        sys.stdout = self.original_stdout 
    
    def operator(self, query):
        master = MasterAgent()
        master.agent_res(query)
        print("Task completed.")
    
    def write(self, message):
        self.append_text(message)
    
    def flush(self):
        pass
    
    def append_text(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.yview(tk.END)
        self.text_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    gui = TerminalGUI(root)
    root.mainloop()
