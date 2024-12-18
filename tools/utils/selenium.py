import os

# Global variables for WebDriver and Selenium configurations
wd = None
selenium_config = {
    "chrome_profile_path": None,
    "headless": True,
    "full_page_screenshot": True,
}


def get_web_driver():
    """
    Initializes and returns a Selenium WebDriver instance.

    Returns:
        Selenium WebDriver instance.
    """
    print("Initializing WebDriver...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium_stealth import stealth

        print("Required packages imported successfully.")
    except ImportError as e:
        print(f"Missing package: {e}. Please install the required dependencies.")
        raise ImportError

    global wd, selenium_config

    if wd:
        print("Returning existing WebDriver instance.")
        return wd

    chrome_profile_path = selenium_config.get("chrome_profile_path", None)
    profile_directory = None
    user_data_dir = None

    if isinstance(chrome_profile_path, str) and os.path.exists(chrome_profile_path):
        profile_directory = os.path.split(chrome_profile_path)[-1].strip("\\").rstrip("/")
        user_data_dir = os.path.split(chrome_profile_path)[0].strip("\\").rstrip("/")
        print(f"Using Chrome profile: {profile_directory}")
        print(f"Using Chrome user data dir: {user_data_dir}")
        print(f"Using Chrome profile path: {chrome_profile_path}")

    chrome_options = webdriver.ChromeOptions()
    print("ChromeOptions initialized.")

    chrome_driver_path = "/usr/bin/chromedriver"
    if not os.path.exists(chrome_driver_path):
        print("ChromeDriver not found. Installing via webdriver_manager.")
        chrome_driver_path = ChromeDriverManager().install()
    else:
        print(f"ChromeDriver found at {chrome_driver_path}.")

    if selenium_config.get("headless", False):
        chrome_options.add_argument("--headless")
        print("Headless mode enabled.")
    if selenium_config.get("full_page_screenshot", False):
        chrome_options.add_argument("--start-maximized")
        print("Full page screenshot mode enabled.")
    else:
        chrome_options.add_argument("--window-size=1920,1080")
        print("Window size set to 1920x1080.")

    # General Chrome options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    if user_data_dir and profile_directory:
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"profile-directory={profile_directory}")
        print(f"Using user data dir: {user_data_dir} and profile directory: {profile_directory}")

    try:
        wd = webdriver.Chrome(
            service=ChromeService(chrome_driver_path), options=chrome_options
        )
        print("WebDriver initialized successfully.")

        if wd.capabilities.get("chrome", {}).get("userDataDir"):
            print(f"Profile path in use: {wd.capabilities['chrome']['userDataDir']}")
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        raise e

    if not selenium_config.get("chrome_profile_path", None):
        stealth(
            wd,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        print("Stealth mode configured.")

    wd.implicitly_wait(3)
    print("Implicit wait set to 3 seconds.")

    return wd


def set_web_driver(new_wd):
    """
    Updates the global WebDriver instance and removes pop-ups on the current page.

    Parameters:
        new_wd: New WebDriver instance.
    """
    js_script = """
    var popUpSelectors = ['modal', 'popup', 'overlay', 'dialog'];
    popUpSelectors.forEach(function(selector) {
        var elements = document.querySelectorAll(selector);
        elements.forEach(function(element) {
            element.parentNode.removeChild(element);
        });
    });
    """

    new_wd.execute_script(js_script)

    if "linkedin.com" in new_wd.current_url:
        linkedin_js_script = """
        var linkedinSelectors = ['div.msg-overlay-list-bubble', 'div.ml4.msg-overlay-list-bubble__tablet-height'];
        linkedinSelectors.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            elements.forEach(function(element) {
                element.parentNode.removeChild(element);
            });
        });
        """
        new_wd.execute_script(linkedin_js_script)

    new_wd.execute_script("document.body.style.zoom='1.2'")

    global wd
    wd = new_wd


def set_selenium_config(config):
    """
    Updates the Selenium configuration.

    Parameters:
        config: Dictionary with new Selenium settings.
    """
    global selenium_config
    selenium_config = config