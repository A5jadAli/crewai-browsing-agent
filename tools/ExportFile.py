# import base64
# from crewai_tools import tool
# from pydantic import Field

# from .util.selenium import get_web_driver
# from crewai.utils import get_openai_client

# @tool("Export current web page as a file")
# class ExportFile:
#     """
#     This tool converts the current full web page into a PDF file and returns its file_id.
#     You can send this file id back to the user for further processing.
#     """

#     def run(self):
#         wd = get_web_driver()
#         client = get_openai_client()

#         # Define parameters for generating the PDF
#         params = {
#             "landscape": False,
#             "displayHeaderFooter": False,
#             "printBackground": True,
#             "preferCSSPageSize": True,
#         }

#         # Generate the PDF via Chrome DevTools Protocol (CDP)
#         result = wd.execute_cdp_cmd("Page.printToPDF", params)
#         pdf_data = result["data"]

#         # Decode the PDF data
#         pdf_bytes = base64.b64decode(pdf_data)

#         # Save the PDF locally
#         pdf_file_name = "exported_file.pdf"
#         with open(pdf_file_name, "wb") as f:
#             f.write(pdf_bytes)

#         # Upload the PDF to OpenAI and get the file ID
#         with open(pdf_file_name, "rb") as file:
#             file_id = client.files.create(file=file, purpose="assistants").id

#         # Save the file ID in shared state for reference
#         self._shared_state.set("file_id", file_id)

#         return (
#             f"Success. File exported with id: `{file_id}`. "
#             f"You can now send this file id back to the user."
#         )

import base64
from crewai_tools import tool
from pydantic import Field
import openai
import os
from typing import Optional

from .util.selenium import get_web_driver

@tool("Export current web page as a file")
class ExportFile:
    """
    This tool converts the current full web page into a PDF file and returns its file_id.
    You can send this file id back to the user for further processing.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ExportFile tool with an optional API key.
        If no API key is provided, it will try to use OPENAI_API_KEY from environment variables.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either through constructor or OPENAI_API_KEY environment variable")
        self.client = openai.OpenAI(api_key=self.api_key)

    def run(self):
        wd = get_web_driver()

        # Define parameters for generating the PDF
        params = {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True,
        }

        # Generate the PDF via Chrome DevTools Protocol (CDP)
        result = wd.execute_cdp_cmd("Page.printToPDF", params)
        pdf_data = result["data"]

        # Decode the PDF data
        pdf_bytes = base64.b64decode(pdf_data)

        # Save the PDF locally with a unique name
        import uuid
        pdf_file_name = f"exported_file_{uuid.uuid4()}.pdf"
        
        try:
            # Save the PDF locally
            with open(pdf_file_name, "wb") as f:
                f.write(pdf_bytes)

            # Upload the PDF to OpenAI and get the file ID
            with open(pdf_file_name, "rb") as file:
                response = self.client.files.create(file=file, purpose="assistants")
                file_id = response.id

            # Save the file ID in shared state for reference
            self._shared_state.set("file_id", file_id)

            return (
                f"Success. File exported with id: `{file_id}`. "
                f"You can now send this file id back to the user."
            )
        
        finally:
            # Clean up the temporary file
            if os.path.exists(pdf_file_name):
                try:
                    os.remove(pdf_file_name)
                except Exception as e:
                    print(f"Warning: Could not delete temporary file {pdf_file_name}: {e}")