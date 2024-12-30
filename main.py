import base64
import re
import os
from dotenv import load_dotenv
from crewai import Agent
from tools.util.selenium import set_selenium_config, get_web_driver, set_web_driver
from tools.util.highlights import highlight_elements_with_labels, remove_highlight_and_labels
from tools.util.screenshot import get_b64_screenshot
from tools import (
    ClickElement,
    ExportFile,
    GoBack,
    ReadURL,
    Scroll,
    SelectDropdown,
    SendKeys,
    SolveCaptcha,
    WebPageSummarizer,
)
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Initialize OpenRouter LLM
openrouter_llm = ChatOpenAI(
    model="anthropic/claude-3.5-sonnet",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://www.ai-server.org/",
        "X-Title": "My Browsing Agent",
    },
    temperature=0.3,
    streaming=True,
)

class BrowsingAgent:
    SCREENSHOT_FILE_NAME = "screenshot.jpg"

    def __init__(self, selenium_config=None, **kwargs):
        """
        Initialize the BrowsingAgent with CrewAI-compatible tools and OpenRouter LLM.
        """
        self.agent = Agent(
            role="Web Browsing Assistant",
            goal="Navigate and search the web effectively for user queries.",
            backstory="An expert agent skilled in web navigation and interaction.",
            tools=[
                ClickElement(),
                ExportFile(),
                GoBack(),
                ReadURL(),
                Scroll(),
                SelectDropdown(),
                SendKeys(),
                SolveCaptcha(),
                WebPageSummarizer(),
            ],
            llm=openrouter_llm,  # Use OpenRouter for LLM interactions
            **kwargs,
        )
        if selenium_config:
            set_selenium_config(selenium_config)

        self.prev_message = ""

    def validate_response(self, message):
        """
        Validates agent responses to avoid redundancy and manage web interactions.
        """
        filtered_message = re.sub(r"\[.*?\]", "", message).strip()

        if filtered_message and self.prev_message == filtered_message:
            raise ValueError(
                "Do not repeat yourself. If stuck, try a different approach or search directly on Google."
            )

        self.prev_message = filtered_message
        return filtered_message

    def process_command(self, command):
        """
        Process specific browsing-related commands.
        """
        wd = get_web_driver()

        if command == "[send screenshot]":
            remove_highlight_and_labels(wd)
            self.take_screenshot()
            response_text = "Here is the screenshot of the current web page."

        elif command == "[highlight clickable elements]":
            highlight_elements_with_labels(
                wd, 'a, button, div[onclick], div[role="button"], div[tabindex], span[onclick], span[role="button"], span[tabindex]'
            )
            response_text = self._get_highlighted_elements_response(wd)

        elif command == "[highlight text fields]":
            highlight_elements_with_labels(wd, "input, textarea")
            response_text = self._get_highlighted_elements_response(wd)

        elif command == "[highlight dropdowns]":
            highlight_elements_with_labels(wd, "select")
            response_text = self._get_highlighted_dropdowns_response(wd)

        else:
            return command

        set_web_driver(wd)
        return response_text

    def take_screenshot(self):
        """
        Takes a screenshot of the current web page and saves it.
        """
        wd = get_web_driver()
        screenshot = get_b64_screenshot(wd)
        screenshot_data = base64.b64decode(screenshot)
        with open(self.SCREENSHOT_FILE_NAME, "wb") as screenshot_file:
            screenshot_file.write(screenshot_data)

    def _get_highlighted_elements_response(self, wd):
        """
        Generate response for highlighted elements.
        """
        all_elements = wd.find_elements_by_css_selector(".highlighted-element")
        all_element_texts = [element.text.strip() for element in all_elements if element.text]

        elements_formatted = ", ".join(
            [f"{i + 1}: {text}" for i, text in enumerate(all_element_texts)]
        )

        return (
            "Here is the screenshot of the current web page with highlighted elements. "
            f"Texts of the elements are: {elements_formatted}."
        )

    def _get_highlighted_dropdowns_response(self, wd):
        """
        Generate response for highlighted dropdowns.
        """
        all_elements = wd.find_elements_by_css_selector(".highlighted-element")
        dropdown_data = {}

        for i, element in enumerate(all_elements, start=1):
            options = [
                option.text.strip() for option in element.find_elements_by_tag_name("option")
            ]
            dropdown_data[str(i)] = options[:10]  # Limit options for clarity

        dropdowns_formatted = ", ".join(
            [f"{key}: {', '.join(values)}" for key, values in dropdown_data.items()]
        )

        return (
            "Here is the screenshot of the current web page with highlighted dropdowns. "
            f"Dropdown options are: {dropdowns_formatted}."
        )

# Test BrowsingAgent with OpenRouter
if __name__ == "__main__":
    agent = BrowsingAgent()
    print("Initialized BrowsingAgent with OpenRouter.")