# CrewAI Browsing Agent

A highly customizable browsing automation framework designed to navigate websites, interact with elements, and perform tasks such as extracting data, solving captchas, and summarizing content. This project leverages CrewAI with OpenRouter integration for advanced language model interactions.

## Features
- Navigate and interact with web pages programmatically
- Highlight and interact with clickable elements, text fields, and dropdowns
- Extract and summarize content from web pages
- Solve captchas and handle complex browsing scenarios
- Easily customizable for additional tasks and workflows

## Setup Instructions

### Prerequisites
1. Python 3.8+
2. pip (included with Python installation)
3. Google Chrome
4. ChromeDriver (automatically managed by the script using `webdriver-manager`)

### Installation

1. Clone or download the repository and navigate to its directory

2. Create and activate a virtual environment:

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your OpenRouter API key:
   - Create a `.env` file in the project root
   - Add your API key: `OPENROUTER_API_KEY=your_openrouter_api_key`

5. Run tests:
```bash
python browsing_agent_test.py
```

## Usage

### Using Predefined Tasks
1. Open `browsing_agent_test.py`
2. Modify the tasks as needed
3. Run: `python browsing_agent_test.py`

### Defining New Tasks
You can create custom browsing tasks by:
1. Opening `main.py`
2. Adding or modifying commands in the `process_command` method
3. Using tools like `ClickElement`, `ReadURL`, and `WebPageSummarizer`

## Project Structure

```
crewai-browsing-agent/
│
├── tools/                 # Tools for interacting with web pages
│   └── util/             # Utility functions
├── .env                  # Environment variables file
├── .gitignore           # Git ignore file
├── browsing_agent_test.py # Test script for predefined tasks
├── client_req.txt       # Client requirements file
├── LICENSE              # License file
├── main.py             # Main logic for the browsing agent
├── README.md           # Documentation
└── requirements.txt    # Python dependencies
```