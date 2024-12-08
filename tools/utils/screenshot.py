import base64
from typing import Optional

class ScreenshotUtility:
    @staticmethod
    def get_b64_screenshot(driver, element=None):
        """
        Capture screenshot of entire page or specific element
        
        :param driver: Selenium WebDriver
        :param element: Optional Selenium WebElement to screenshot
        :return: Base64 encoded screenshot
        """
        try:
            if element:
                # Screenshot of specific element
                screenshot_b64 = element.screenshot_as_base64
            else:
                # Full page screenshot
                screenshot_b64 = driver.get_screenshot_as_base64()
            
            return screenshot_b64
        except Exception as e:
            print(f"Screenshot capture error: {e}")
            return None
    
    @staticmethod
    def save_screenshot(screenshot_b64: str, filename: str = "screenshot.jpg"):
        """
        Save base64 encoded screenshot to file
        
        :param screenshot_b64: Base64 encoded screenshot
        :param filename: Output filename
        :return: Path to saved screenshot
        """
        if not screenshot_b64:
            raise ValueError("No screenshot data provided")
        
        try:
            # Decode base64 screenshot
            screenshot_data = base64.b64decode(screenshot_b64)
            
            # Save screenshot
            with open(filename, "wb") as screenshot_file:
                screenshot_file.write(screenshot_data)
            
            return filename
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return None