from typing import Dict
from pydantic import Field, root_validator
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from crewai_tools import tool

from .util.selenium import get_web_driver, set_web_driver
from .util.highlights import remove_highlight_and_labels

@tool("Select options from dropdowns on the page")
class SelectDropdown:
    """
    This tool selects an option in a dropdown on the current web page based on the sequence number of the element 
    and the index of the option to select.

    Before using this tool, ensure that dropdown elements on the page are highlighted by outputting the '[highlight dropdowns]' message.
    """
    key_value_pairs: Dict[str, str] = Field(
        ...,
        description="A dictionary where the key is the sequence number of the dropdown element, "
                    "and the value is the index of the option to select.",
        examples=[{"1": 0, "2": 1}, {"3": 2}],
    )

    @root_validator(pre=True)
    def validate_key_value_pairs(cls, values):
        if not values.get("key_value_pairs"):
            raise ValueError(
                "key_value_pairs is required. Example format: "
                "key_value_pairs={'1': 0, '2': 1}"
            )
        return values

    def run(self):
        wd = get_web_driver()

        # Ensure dropdown elements are highlighted
        if "select" not in self._shared_state.get("elements_highlighted", ""):
            raise ValueError(
                "Please highlight dropdown elements on the page first by outputting '[highlight dropdowns]' message. "
                "You must output just the message without calling the tool first, so the user can respond with the screenshot."
            )

        # Retrieve all highlighted elements
        all_elements = wd.find_elements(By.CSS_SELECTOR, ".highlighted-element")

        try:
            # Iterate through key-value pairs and select the corresponding options
            for key, value in self.key_value_pairs.items():
                key = int(key)
                element = all_elements[key - 1]
                select = Select(element)
                select.select_by_index(int(value))

            result = (
                "Success. Option is selected in the dropdown. "
                "To further analyze the page, output '[send screenshot]' command."
            )
        except Exception as e:
            result = str(e)

        # Remove highlights and reset web driver state
        remove_highlight_and_labels(wd)
        set_web_driver(wd)

        return result