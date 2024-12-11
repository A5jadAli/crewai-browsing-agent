from selenium.webdriver.common.by import By
from crewai_tools import tool
from crewai.utils import get_openai_client

from .util.selenium import get_web_driver, set_web_driver

@tool("Summarize the content of the current webpage")
class WebPageSummarizer:
    """
    This tool summarizes the content of the current web page, extracting the main points and providing a concise summary.
    """

    def run(self):
        wd = get_web_driver()
        client = get_openai_client()

        # Extract text from the webpage
        content = wd.find_element(By.TAG_NAME, "body").text

        # Limit the content to the first 10,000 characters
        content = " ".join(content.split()[:10000])

        # Generate a summary using the OpenAI API
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Your task is to summarize the content of the provided webpage. "
                        "The summary should be concise and informative, capturing the main points and takeaways of the page."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Summarize the content of the following webpage:\n\n" + content
                    ),
                },
            ],
            temperature=0.0,
        )

        # Return the generated summary
        return completion.choices[0].message.content


if __name__ == "__main__":
    wd = get_web_driver()
    wd.get("https://en.wikipedia.org/wiki/Python_(programming_language)")
    set_web_driver(wd)
    tool = WebPageSummarizer()
    print(tool.run())
