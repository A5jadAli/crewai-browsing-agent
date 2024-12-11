import time
from typing import Dict
from pydantic import Field, root_validator
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from crewai_tools import tool

from .util.selenium import get_web_driver, set_web_driver
from .util.highlights import remove_highlight_and_labels

@tool("Send keys to input fields on the page")
class SendKeys:
    """
    This tool sends keys into input fields on the current webpage based on the description of that element and the text to be typed. 
    It then clicks "Enter" on the last element to submit the form.

    Before using this tool, ensure that input elements on the page are highlighted by outputting the '[highlight text fields]' message.
    """
    elements_and_texts: Dict[int, str] = Field(
        ...,
        description="A dictionary where the key is the element number and the value is the text to be typed.",
        examples=[
            {52: "johndoe@gmail.com", 53: "password123"},
            {3: "John Doe", 4: "123 Main St"},
        ],
    )

    @root_validator(pre=True)
    def validate_elements_and_texts(cls, values):
        if not values.get("elements_and_texts"):
            raise ValueError(
                "elements_and_texts is required. Example format: "
                "elements_and_texts={1: 'John Doe', 2: '123 Main St'}"
            )
        return values

    def run(self):
        wd = get_web_driver()

        # Ensure input fields are highlighted
        if "input" not in self._shared_state.get("elements_highlighted", ""):
            raise ValueError(
                "Please highlight input elements on the page first by outputting '[highlight text fields]' message. "
                "You must output just the message without calling the tool first, so the user can respond with the screenshot."
            )

        # Retrieve all highlighted elements
        all_elements = wd.find_elements(By.CSS_SELECTOR, ".highlighted-element")

        try:
            for i, (key, value) in enumerate(self.elements_and_texts.items()):
                key = int(key)
                element = all_elements[key - 1]

                # Click, clear, and send keys to the input field
                try:
                    element.click()
                    element.send_keys(Keys.CONTROL + "a")  # Select all text
                    element.send_keys(Keys.DELETE)
                    element.clear()
                except Exception:
                    pass
                element.send_keys(value)

                # Press Enter on the last field
                if i == len(self.elements_and_texts) - 1:
                    element.send_keys(Keys.RETURN)
                    time.sleep(3)

            result = (
                f"Sent input to elements and pressed Enter. Current URL is {wd.current_url}. "
                "To further analyze the page, output '[send screenshot]' command."
            )
        except Exception as e:
            result = str(e)

        # Cleanup highlights and reset driver state
        remove_highlight_and_labels(wd)
        set_web_driver(wd)

        return result