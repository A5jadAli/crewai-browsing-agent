import base64
from crewai_tools import tool
from pydantic import Field

from .util import get_web_driver
from crewai.utils import get_openai_client

@tool("Export current web page as a file")
class ExportFile:
    """
    This tool converts the current full web page into a PDF file and returns its file_id.
    You can send this file id back to the user for further processing.
    """

    def run(self):
        wd = get_web_driver()
        client = get_openai_client()

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

        # Save the PDF locally
        pdf_file_name = "exported_file.pdf"
        with open(pdf_file_name, "wb") as f:
            f.write(pdf_bytes)

        # Upload the PDF to OpenAI and get the file ID
        with open(pdf_file_name, "rb") as file:
            file_id = client.files.create(file=file, purpose="assistants").id

        # Save the file ID in shared state for reference
        self._shared_state.set("file_id", file_id)

        return (
            f"Success. File exported with id: `{file_id}`. "
            f"You can now send this file id back to the user."
        )