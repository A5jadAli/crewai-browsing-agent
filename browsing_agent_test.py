from main import BrowsingAgent

def test_news_extraction():
    print("Starting BrowsingAgent test: News Extraction from CNN Business section...")

    # Initialize the agent
    agent = BrowsingAgent()

    try:
        # Step 1: Navigate to cnn.com
        print("\nStep 1: Navigate to cnn.com")
        response = agent.process_command("Navigate to https://www.cnn.com")
        print("Response:", response)

        # Step 2: Go to the "Business" section
        print("\nStep 2: Navigate to the Business section")
        business_section_command = "[highlight clickable elements]"  # Simulate finding and clicking the "Business" section
        response = agent.process_command(business_section_command)
        print("Clickable Elements Highlight Response:", response)

        # Extract clickable elements and simulate clicking the "Business" link
        # Assume the Business section link is identified and represented as element number X
        business_link_element_number = 5  # Update this with the correct element number
        click_command = f"[ClickElement] {business_link_element_number}"
        response = agent.process_command(click_command)
        print("Business Section Click Response:", response)

        # Step 3: Extract text from the last 4 news articles
        print("\nStep 3: Extract text from the last 4 news articles")
        response = agent.process_command("[highlight clickable elements]")
        print("Clickable Elements Highlight Response:", response)

        # Simulate clicking and extracting content from the last 4 articles
        for article_number in range(-4, 0):
            print(f"\nExtracting text from article {article_number + 5}")
            article_click_command = f"[ClickElement] {article_number}"
            response = agent.process_command(article_click_command)
            print("Article Click Response:", response)

            # Simulate summarizing the article content
            summarize_command = "[summarize webpage]"
            summary = agent.process_command(summarize_command)
            print("Article Summary:", summary)

    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    test_news_extraction()