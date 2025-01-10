# from selenium.webdriver.common.by import By
# from crewai_tools import tool
# from crewai.utils import get_openai_client

# from .util.selenium import get_web_driver, set_web_driver

# @tool("Summarize the content of the current webpage")
# class WebPageSummarizer:
#     """
#     This tool summarizes the content of the current web page, extracting the main points and providing a concise summary.
#     """

#     def run(self):
#         wd = get_web_driver()
#         client = get_openai_client()

#         # Extract text from the webpage
#         content = wd.find_element(By.TAG_NAME, "body").text

#         # Limit the content to the first 10,000 characters
#         content = " ".join(content.split()[:10000])

#         # Generate a summary using the OpenAI API
#         completion = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "Your task is to summarize the content of the provided webpage. "
#                         "The summary should be concise and informative, capturing the main points and takeaways of the page."
#                     ),
#                 },
#                 {
#                     "role": "user",
#                     "content": (
#                         "Summarize the content of the following webpage:\n\n" + content
#                     ),
#                 },
#             ],
#             temperature=0.0,
#         )

#         # Return the generated summary
#         return completion.choices[0].message.content


# if __name__ == "__main__":
#     wd = get_web_driver()
#     wd.get("https://en.wikipedia.org/wiki/Python_(programming_language)")
#     set_web_driver(wd)
#     tool = WebPageSummarizer()
#     print(tool.run())


import os
from typing import Optional
import openai
from selenium.webdriver.common.by import By
from crewai_tools import tool

from .util.selenium import get_web_driver, set_web_driver

@tool("Summarize the content of the current webpage")
class WebPageSummarizer:
    """
    This tool summarizes the content of the current web page, extracting the main points and providing a concise summary.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", max_chars: int = 10000):
        """
        Initialize the WebPageSummarizer tool.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to use OPENAI_API_KEY from environment.
            model: OpenAI model to use for summarization. Defaults to GPT-3.5-turbo.
            max_chars: Maximum number of characters to process from the webpage. Defaults to 10000.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either through constructor or OPENAI_API_KEY environment variable")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
        self.max_chars = max_chars

    def clean_text(self, text: str) -> str:
        """
        Clean and prepare text for summarization.
        
        Args:
            text: Raw text from webpage
            
        Returns:
            Cleaned and truncated text
        """
        # Remove extra whitespace and normalize spacing
        cleaned = " ".join(text.split())
        # Truncate to max characters while preserving whole words
        return " ".join(cleaned.split()[:self.max_chars])

    def run(self) -> str:
        """
        Run the webpage summarization.
        
        Returns:
            str: Summarized content of the webpage
        
        Raises:
            Exception: If there are errors accessing the webpage or generating the summary
        """
        try:
            wd = get_web_driver()
            
            # Extract text from the webpage
            try:
                content = wd.find_element(By.TAG_NAME, "body").text
            except Exception as e:
                return f"Error extracting webpage content: {str(e)}"

            # Clean and prepare the content
            content = self.clean_text(content)
            
            if not content.strip():
                return "Error: No content found on the webpage to summarize."

            # Generate a summary using the OpenAI API
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Your task is to summarize the content of the provided webpage. "
                                "The summary should be concise and informative, capturing the main points and takeaways of the page. "
                                "Focus on key information and maintain a clear structure."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Summarize the content of the following webpage:\n\n{content}",
                        },
                    ],
                    temperature=0.0,
                )

                return completion.choices[0].message.content

            except openai.APIError as e:
                return f"Error generating summary: {str(e)}"
            
            except Exception as e:
                return f"Unexpected error during summarization: {str(e)}"

        except Exception as e:
            return f"Error accessing webpage: {str(e)}"

# Example usage if run directly
if __name__ == "__main__":
    try:
        # Initialize WebDriver and navigate to a page
        wd = get_web_driver()
        wd.get("https://en.wikipedia.org/wiki/Python_(programming_language)")
        set_web_driver(wd)
        
        # Create summarizer instance and run
        summarizer = WebPageSummarizer()
        summary = summarizer.run()
        print(summary)
        
    except Exception as e:
        print(f"Error running summarizer: {e}")
    
    finally:
        # Cleanup
        try:
            wd.quit()
        except:
            pass