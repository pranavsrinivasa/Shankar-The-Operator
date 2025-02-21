# Shankar-The-Operator

**Shankar-The-Operator** is a multi AI agent system designed to control a computer based on user queries. The system uses a hierarchical agent structure to break down complex tasks into simpler actions handled by specialized agents.

## Architecture

- **Master Agent**  
  The central controller that interprets user queries and delegates tasks to the subordinate agents. It coordinates the overall workflow and ensures that each task is executed in the proper sequence.

- **Subordinate Agents**  
  These agents perform the actual operations on the computer:
  - **Keyboardagent**  
    Handles all keyboard-related tasks, including typing text and executing hotkeys.
  - **Vision Mouse Agent**  
    Manages mouse operations and screen analysis. It has two main methods:
    - **Pytesseract OCR**: Detects and locates text on the screen by returning its (x, y) coordinates, enabling precise mouse navigation.
    - **Vision Language Model (e.g., llama 3.2 90B vision)**: Verifies that the executed actions are accurately reflected on the screen, adding an extra layer of confirmation.

## Usage Instructions

1. **Clone the Project**:  
   Clone the repository to your local machine.

2. **API Key Setup**:  
   Create a `.env` file in the project directory and enter your API key.

3. **System-Specific Configuration**:  
   If you're using a system other than Windows, open `Tools/ScreentoXML_OCR.py` and comment out line 8 (this line is specific to Windows systems).

4. **Install Dependencies**:  
   Run the following command to install all necessary packages:
   ```bash
   pip install -r requirements.txt
5. **Run Program**:
   ```bash
   python GUI.py

## Summary

Shankar-The-Operator leverages a master-subordinate architecture to efficiently manage and execute computer control tasks. With its dual-method screen analysis and dedicated agents for keyboard and mouse control, the system is designed for accuracy and ease of use.
