import time
from crewai_tools import tool

from .util.selenium import get_web_driver, set_web_driver

@tool("Go back one page in browser history")
class GoBack:
    """
    This tool allows you to go back 1 page in the browser history.
    Use it in case of a mistake or if a page shows unexpected content.
    """

    def run(self):
        wd = get_web_driver()

        # Navigate back in browser history
        wd.back()

        # Wait for the page to load
        time.sleep(3)

        # Update the web driver state
        set_web_driver(wd)

        # Return success message with current URL
        return f"Success. Went back 1 page. Current URL is: {wd.current_url}"