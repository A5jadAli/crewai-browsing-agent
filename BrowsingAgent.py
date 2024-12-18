import os
from crewai import Agent, Crew, Task
from crewai_tools import SeleniumScrapingTool, WebsiteSearchTool
import re
import base64
import openai

class CrewAIBrowsingAgent:
    def __init__(self, openai_api_key=None, selenium_config=None):
        """
        Initialize the CrewAI Browsing Agency
        
        :param openai_api_key: OpenAI API key for vision capabilities
        :param selenium_config: Optional Selenium configuration dictionary
        """
        # Set API keys
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Initialize tools
        self.web_search_tool = WebsiteSearchTool()
        self.selenium_tool = SeleniumScrapingTool(
            config=selenium_config or {}
        )
        
        # Define browsing agent
        self.browsing_agent = self._create_browsing_agent()
        
        # Shared state for tracking
        self.prev_message = ""
        self.screenshot_file_name = "screenshot.jpg"
    
    def _create_browsing_agent(self):
        """
        Create the primary browsing agent with specialized tools and instructions
        """
        return Agent(
            role='Web Browsing Specialist',
            goal='Navigate and search the web effectively while following strict browsing protocols',
            backstory='An expert web navigator who follows precise instructions for web interaction, '
                      'ensuring methodical and controlled web browsing',
            verbose=True,
            memory=True,
            tools=[
                self.web_search_tool,
                self.selenium_tool
            ],
            allow_delegation=False
        )
    
    def create_browsing_task(self, objective):
        """
        Create a task for web browsing with specific objective
        
        :param objective: The specific web browsing task to accomplish
        :return: CrewAI Task object
        """
        return Task(
            description=objective,
            agent=self.browsing_agent,
            tools=[self.web_search_tool, self.selenium_tool]
        )
    
    def validate_message(self, message):
        """
        Validate and process special browsing commands
        
        :param message: Input message to validate
        :return: Processed message or raise special command handler
        """
        # Remove content in square brackets
        filtered_message = re.sub(r"\[.*?\]", "", message).strip()
        
        # Prevent message repetition
        if filtered_message and self.prev_message == filtered_message:
            raise ValueError(
                "Do not repeat yourself. If you are stuck, try a different approach or search in Google."
            )
        
        self.prev_message = filtered_message
        
        # Special command handlers
        special_commands = {
            "[send screenshot]": self._handle_screenshot,
            "[highlight clickable elements]": self._highlight_clickable_elements,
            "[highlight text fields]": self._highlight_text_fields,
            "[highlight dropdowns]": self._highlight_dropdowns
        }
        
        # Check for special commands
        for command, handler in special_commands.items():
            if command.lower() in message.lower():
                return handler()
        
        return message
    
    def _handle_screenshot(self):
        """
        Take and process a screenshot
        """
        # Placeholder for screenshot logic
        # In actual implementation, this would use Selenium to capture screenshot
        screenshot_path = self.screenshot_file_name
        
        with open(screenshot_path, "rb") as file:
            file_id = self._upload_file_to_vision(file)
        
        return {
            "type": "image_response",
            "content": [
                {"type": "text", "text": "Here is the screenshot of the current web page:"},
                {"type": "image_file", "image_file": {"file_id": file_id}}
            ]
        }
    
    def _highlight_clickable_elements(self):
        """
        Highlight and process clickable elements
        """
        # Placeholder for element highlighting logic
        return "Clickable elements highlighting not implemented in this version"
    
    def _highlight_text_fields(self):
        """
        Highlight and process text fields
        """
        # Placeholder for text field highlighting logic
        return "Text fields highlighting not implemented in this version"
    
    def _highlight_dropdowns(self):
        """
        Highlight and process dropdown elements
        """
        # Placeholder for dropdown highlighting logic
        return "Dropdown highlighting not implemented in this version"
    
    def _upload_file_to_vision(self, file):
        """
        Upload file for vision processing
        
        :param file: File object to upload
        :return: File ID from OpenAI
        """
        return openai.File.create(
            file=file,
            purpose="vision"
        ).id
    
    def execute_browsing_task(self, objective):
        """
        Execute a browsing task
        
        :param objective: Browsing task objective
        :return: Task execution result
        """
        # Create crew with the browsing agent and task
        browsing_crew = Crew(
            agents=[self.browsing_agent],
            tasks=[self.create_browsing_task(objective)]
        )
        
        # Execute the crew
        return browsing_crew.kickoff()

def main():
    # Example usage
    browsing_agency = CrewAIBrowsingAgent(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        # Optional Selenium configuration
        selenium_config={
            # Add any specific Selenium configurations
        }
    )
    
    # Example task
    result = browsing_agency.execute_browsing_task(
        "Search for information about artificial intelligence trends in 2024"
    )
    print(result)

if __name__ == "__main__":
    main()