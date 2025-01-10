# import base64
# import time
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.expected_conditions import (
#     frame_to_be_available_and_switch_to_it,
#     presence_of_element_located,
# )
# from selenium.webdriver.support.wait import WebDriverWait
# from crewai_tools import tool
# from crewai.utils import get_openai_client

# from .util.selenium import get_web_driver
# from .util import get_b64_screenshot, remove_highlight_and_labels

# @tool("Solve reCAPTCHA challenges")
# class SolveCaptcha:
#     """
#     This tool asks a human to solve captcha on the current webpage. Make sure that the captcha is visible before running it.
#     """

#     def run(self):
#         wd = get_web_driver()

#         # Locate and click the reCAPTCHA checkbox
#         try:
#             WebDriverWait(wd, 10).until(
#                 frame_to_be_available_and_switch_to_it(
#                     (By.XPATH, "//iframe[@title='reCAPTCHA']")
#                 )
#             )

#             element = WebDriverWait(wd, 3).until(
#                 presence_of_element_located((By.ID, "recaptcha-anchor"))
#             )

#             wd.execute_script("arguments[0].scrollIntoView(true);", element)
#             time.sleep(1)
#             wd.execute_script("arguments[0].click();", element)
#         except Exception as e:
#             return f"Could not click captcha checkbox: {str(e)}"

#         # Verify if the captcha checkbox was successfully checked
#         try:
#             WebDriverWait(wd, 3).until(
#                 lambda d: d.find_element(
#                     By.CLASS_NAME, "recaptcha-checkbox"
#                 ).get_attribute("aria-checked") == "true"
#             )
#             return "Success. Captcha solved."
#         except Exception:
#             pass

#         wd.switch_to.default_content()
#         client = get_openai_client()

#         # Handle reCAPTCHA challenge
#         WebDriverWait(wd, 10).until(
#             frame_to_be_available_and_switch_to_it(
#                 (By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']")
#             )
#         )
#         time.sleep(2)

#         attempts = 0
#         while attempts < 5:
#             tiles = wd.find_elements(By.CLASS_NAME, "rc-imageselect-tile")
#             tiles = [tile for tile in tiles if not tile.get_attribute("class").endswith("rc-imageselect-dynamic-selected")]

#             image_content = []
#             for i, tile in enumerate(tiles, start=1):
#                 screenshot = get_b64_screenshot(wd, tile)
#                 image_content.append(
#                     {"type": "text", "text": f"Image {i}:"},
#                     {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot}", "detail": "high"}},
#                 )

#             task_text = wd.find_element(By.CLASS_NAME, "rc-imageselect-instructions").text.strip().replace("\n", " ")
#             task_text = task_text.replace("Click verify", "Output 0").replace("click skip", "Output 0")
#             continuous_task = "once there are none left" in task_text.lower()

#             additional_info = (
#                 "Keep in mind that all images are part of a bigger image in a 4x4 grid. "
#                 if len(tiles) > 9 else ""
#             )

#             messages = [
#                 {"role": "system", "content": f"You are an AI supporting visually impaired users. {additional_info}"},
#                 {"role": "user", "content": [*image_content, {"type": "text", "text": f"{task_text}. Only output numbers separated by commas. Output 0 if there are none."}]},
#             ]

#             response = client.chat.completions.create(
#                 model="gpt-4o",
#                 messages=messages,
#                 max_tokens=1024,
#                 temperature=0.0,
#             )

#             message_text = response.choices[0].message.content
#             if "0" in message_text and "10" not in message_text:
#                 wd.find_element(By.ID, "recaptcha-verify-button").click()
#                 if self.verify_checkbox(wd):
#                     return "Success. Captcha solved."
#             else:
#                 numbers = [int(n.strip()) for n in message_text.split(",") if n.strip().isdigit()]
#                 for number in numbers:
#                     wd.execute_script("arguments[0].click();", tiles[number - 1])
#                     time.sleep(0.5)

#                 if not continuous_task:
#                     wd.find_element(By.ID, "recaptcha-verify-button").click()
#                     if self.verify_checkbox(wd):
#                         return "Success. Captcha solved."

#             attempts += 1

#         remove_highlight_and_labels(wd)
#         wd.switch_to.default_content()
#         return "Could not solve captcha."

#     def verify_checkbox(self, wd):
#         wd.switch_to.default_content()
#         try:
#             WebDriverWait(wd, 10).until(
#                 frame_to_be_available_and_switch_to_it(
#                     (By.XPATH, "//iframe[@title='reCAPTCHA']")
#                 )
#             )
#             return WebDriverWait(wd, 5).until(
#                 lambda d: d.find_element(
#                     By.CLASS_NAME, "recaptcha-checkbox"
#                 ).get_attribute("aria-checked") == "true"
#             )
#         except Exception:
#             return False


import base64
import time
import os
from typing import Optional
import openai
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    frame_to_be_available_and_switch_to_it,
    presence_of_element_located,
)
from selenium.webdriver.support.wait import WebDriverWait
from crewai_tools import tool

from .util.selenium import get_web_driver
from .util import get_b64_screenshot, remove_highlight_and_labels

@tool("Solve reCAPTCHA challenges")
class SolveCaptcha:
    """
    This tool asks a human to solve captcha on the current webpage. Make sure that the captcha is visible before running it.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-vision-preview"):
        """
        Initialize the SolveCaptcha tool with optional API key and model name.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to use OPENAI_API_KEY from environment.
            model: OpenAI model to use for vision tasks. Defaults to GPT-4 Vision.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either through constructor or OPENAI_API_KEY environment variable")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model

    def run(self):
        wd = get_web_driver()

        # Locate and click the reCAPTCHA checkbox
        try:
            WebDriverWait(wd, 10).until(
                frame_to_be_available_and_switch_to_it(
                    (By.XPATH, "//iframe[@title='reCAPTCHA']")
                )
            )

            element = WebDriverWait(wd, 3).until(
                presence_of_element_located((By.ID, "recaptcha-anchor"))
            )

            wd.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            wd.execute_script("arguments[0].click();", element)
        except Exception as e:
            return f"Could not click captcha checkbox: {str(e)}"

        # Verify if the captcha checkbox was successfully checked
        try:
            WebDriverWait(wd, 3).until(
                lambda d: d.find_element(
                    By.CLASS_NAME, "recaptcha-checkbox"
                ).get_attribute("aria-checked") == "true"
            )
            return "Success. Captcha solved."
        except Exception:
            pass

        wd.switch_to.default_content()

        # Handle reCAPTCHA challenge
        try:
            WebDriverWait(wd, 10).until(
                frame_to_be_available_and_switch_to_it(
                    (By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']")
                )
            )
            time.sleep(2)
        except Exception as e:
            return f"Could not find captcha challenge frame: {str(e)}"

        attempts = 0
        while attempts < 5:
            try:
                tiles = wd.find_elements(By.CLASS_NAME, "rc-imageselect-tile")
                tiles = [tile for tile in tiles if not tile.get_attribute("class").endswith("rc-imageselect-dynamic-selected")]

                image_content = []
                for i, tile in enumerate(tiles, start=1):
                    try:
                        screenshot = get_b64_screenshot(wd, tile)
                        image_content.extend([
                            {"type": "text", "text": f"Image {i}:"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot}", "detail": "high"}},
                        ])
                    except Exception as e:
                        print(f"Warning: Could not capture screenshot for tile {i}: {e}")
                        continue

                task_text = wd.find_element(By.CLASS_NAME, "rc-imageselect-instructions").text.strip().replace("\n", " ")
                task_text = task_text.replace("Click verify", "Output 0").replace("click skip", "Output 0")
                continuous_task = "once there are none left" in task_text.lower()

                additional_info = (
                    "Keep in mind that all images are part of a bigger image in a 4x4 grid. "
                    if len(tiles) > 9 else ""
                )

                messages = [
                    {"role": "system", "content": f"You are an AI supporting visually impaired users. {additional_info}"},
                    {"role": "user", "content": [*image_content, {"type": "text", "text": f"{task_text}. Only output numbers separated by commas. Output 0 if there are none."}]},
                ]

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.0,
                )

                message_text = response.choices[0].message.content
                if "0" in message_text and "10" not in message_text:
                    wd.find_element(By.ID, "recaptcha-verify-button").click()
                    if self.verify_checkbox(wd):
                        return "Success. Captcha solved."
                else:
                    numbers = [int(n.strip()) for n in message_text.split(",") if n.strip().isdigit()]
                    for number in numbers:
                        if 0 < number <= len(tiles):  # Validate tile index
                            wd.execute_script("arguments[0].click();", tiles[number - 1])
                            time.sleep(0.5)

                    if not continuous_task:
                        wd.find_element(By.ID, "recaptcha-verify-button").click()
                        if self.verify_checkbox(wd):
                            return "Success. Captcha solved."

            except Exception as e:
                print(f"Warning: Error during attempt {attempts + 1}: {e}")
            
            attempts += 1

        try:
            remove_highlight_and_labels(wd)
            wd.switch_to.default_content()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
            
        return "Could not solve captcha."

    def verify_checkbox(self, wd):
        wd.switch_to.default_content()
        try:
            WebDriverWait(wd, 10).until(
                frame_to_be_available_and_switch_to_it(
                    (By.XPATH, "//iframe[@title='reCAPTCHA']")
                )
            )
            return WebDriverWait(wd, 5).until(
                lambda d: d.find_element(
                    By.CLASS_NAME, "recaptcha-checkbox"
                ).get_attribute("aria-checked") == "true"
            )
        except Exception:
            return False