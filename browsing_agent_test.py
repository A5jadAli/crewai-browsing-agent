from main import BrowsingAgent

# Initialize the BrowsingAgent
agent = BrowsingAgent()

def test_browsing():
    print("Starting BrowsingAgent test...")

    # Example 1: Highlight clickable elements on a web page
    print("\nStep 1: Highlight clickable elements")
    try:
        response = agent.process_command("[highlight clickable elements]")
        print("Response:", response)
    except Exception as e:
        print("Error:", e)

    # Example 2: Highlight text fields on a web page
    print("\nStep 2: Highlight text fields")
    try:
        response = agent.process_command("[highlight text fields]")
        print("Response:", response)
    except Exception as e:
        print("Error:", e)

    # Example 3: Take a screenshot of the current page
    print("\nStep 3: Take a screenshot")
    try:
        agent.take_screenshot()
        print("Screenshot saved as 'screenshot.jpg'")
    except Exception as e:
        print("Error:", e)

    # Example 4: Summarize the web page content
    print("\nStep 4: Summarize the web page")
    try:
        response = agent.process_command("Summarize the webpage")
        print("Summary:", response)
    except Exception as e:
        print("Error:", e)

    print("\nTest completed.")

if __name__ == "__main__":
    test_browsing()