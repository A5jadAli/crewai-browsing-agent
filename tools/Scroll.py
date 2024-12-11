from typing import Literal
from pydantic import Field
from crewai_tools import tool

from .util.selenium import get_web_driver, set_web_driver

@tool("Scroll the current web page")
class Scroll:
    """
    This tool allows you to scroll the current web page up or down by 1 screen height.
    """
    direction: Literal["up", "down"] = Field(..., description="Direction to scroll.")

    def run(self):
        wd = get_web_driver()

        # Get the screen height of the browser window
        height = wd.get_window_size()["height"]

        # Get the zoom level of the page
        zoom_level = wd.execute_script("return document.body.style.zoom || '1';")
        zoom_level = (
            float(zoom_level.strip("%")) / 100 if "%" in zoom_level else float(zoom_level)
        )

        # Adjust the height based on the zoom level
        adjusted_height = height / zoom_level

        # Get current scroll position and total scroll height
        current_scroll_position = wd.execute_script("return window.pageYOffset;")
        total_scroll_height = wd.execute_script("return document.body.scrollHeight;")

        result = ""

        # Scroll up logic
        if self.direction == "up":
            if current_scroll_position == 0:
                result = "Reached the top of the page. Cannot scroll up any further.\n"
            else:
                wd.execute_script(f"window.scrollBy(0, -{adjusted_height});")
                result = (
                    "Scrolled up by 1 screen height. Make sure to output '[send screenshot]' command to analyze the page after scrolling."
                )

        # Scroll down logic
        elif self.direction == "down":
            if current_scroll_position + adjusted_height >= total_scroll_height:
                result = "Reached the bottom of the page. Cannot scroll down any further.\n"
            else:
                wd.execute_script(f"window.scrollBy(0, {adjusted_height});")
                result = (
                    "Scrolled down by 1 screen height. Make sure to output '[send screenshot]' command to analyze the page after scrolling."
                )

        # Update the web driver state
        set_web_driver(wd)

        return result