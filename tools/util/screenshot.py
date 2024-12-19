def get_b64_screenshot(wd, element=None):
    """
    Captures a screenshot in base64 format.

    Parameters:
        wd: The web driver instance.
        element: The specific element to capture (optional). If not provided, captures the entire page.

    Returns:
        A base64-encoded string of the screenshot.
    """
    if element:
        screenshot_b64 = element.screenshot_as_base64
    else:
        screenshot_b64 = wd.get_screenshot_as_base64()

    return screenshot_b64