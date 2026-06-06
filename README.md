# AI Handwritten Automata Simulator & Visualizer

An interactive Streamlit application that uses AI vision to classify handwritten Finite Automata diagrams (DFAs/NFAs), maps their state transition matrices, and renders clean, interactive digital blueprints using Graphviz.

## 🚀 Local Setup Instructions

Follow these step-by-step instructions to configure and run the project on your local machine.

### Prerequisites
Ensure you have the following installed on your system:
* **Python 3.10 or higher** (Ensure it is added to your system PATH)
* **Graphviz System Binaries**: 
  * **Windows**: Download and install the executable from [Graphviz Downloads](https://graphviz.org/download/). During installation, make sure to check the box that says **"Add Graphviz to the system PATH for all users"**.
  * **macOS**: Install via Homebrew: `brew install graphviz`
  * **Linux (Ubuntu/Debian)**: `sudo apt-get install graphviz`

---

### Step 1: Initialize a Virtual Environment
Navigate to the project root directory using your terminal or command prompt and run:

```bash
# Create a virtual environment named 'env'
python -m venv env

# Activate the virtual environment
# On Windows (Command Prompt):
env\Scripts\activate
# On Windows (PowerShell):
.\env\Scripts\activate
# On macOS/Linux:
source env/bin/activate

Step 2: Install Project Dependencies
With the virtual environment active, install all required Python modules:

pip install -r requirements.txt

Step 3: Configure Your Gemini API Key
The application utilizes the Gemini API via the google-genai SDK to analyze handwritten state diagrams.

Obtain a free API Key from Google AI Studio.

Create a file named .env in the root folder of this project.

Add your key inside the file like this:
GEMINI_API_KEY=your_actual_api_key_here

Step 4: 🏃 Run the Project:
Execute the following command in your terminal to launch the web interface:

streamlit run app.py




