import time
from pydantic import Field
from selenium.webdriver.common.by import By
from crewai_tools import tool

from .util.selenium import get_web_driver, set_web_driver
from .util.highlights import remove_highlight_and_labels

@tool("Click on a highlighted element")
class ClickElement:
    """
    This tool clicks on an element on the current web page based on its number.

    Before using this tool, ensure that clickable elements on the page are highlighted by outputting the '[highlight clickable elements]' message.
    """
    element_number: int = Field(
        ...,
        description="The number of the element to click on. The element numbers are displayed on the page after highlighting elements."
    )

    def run(self):
        wd = get_web_driver()

        # Ensure elements are highlighted before clicking
        if "button" not in self._shared_state.get("elements_highlighted", ""):
            raise ValueError(
                "Please highlight clickable elements on the page first by outputting '[highlight clickable elements]' message. "
                "You must output just the message without calling the tool first, so the user can respond with the screenshot."
            )

        # Retrieve all highlighted elements
        all_elements = wd.find_elements(By.CSS_SELECTOR, ".highlighted-element")

        try:
            # Validate element number and click
            element_text = all_elements[self.element_number - 1].text
            element_text = element_text.strip() if element_text else ""
            try:
                all_elements[self.element_number - 1].click()
            except Exception as e:
                if "element click intercepted" in str(e).lower():
                    wd.execute_script("arguments[0].click();", all_elements[self.element_number - 1])
                else:
                    raise e

            time.sleep(3)

            result = (
                f"Clicked on element {self.element_number}. Text on clicked element: '{element_text}'. "
                f"Current URL is {wd.current_url}. To further analyze the page, output '[send screenshot]' command."
            )
        except IndexError:
            result = "Element number is invalid. Please try again with a valid element number."
        except Exception as e:
            result = str(e)

        # Clean up highlights and reset state
        wd = remove_highlight_and_labels(wd)
        wd.execute_script("document.body.style.zoom='1.5'")
        set_web_driver(wd)

        self._shared_state.set("elements_highlighted", "")

        return result