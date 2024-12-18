def highlight_elements_with_labels(driver, selector):
    """
    Highlights elements on the page that match the given CSS selector by adding a red border and labels.

    Parameters:
        driver: Selenium WebDriver instance.
        selector: CSS selector for the elements to be highlighted.

    Returns:
        Updated WebDriver instance with highlighted elements.
    """
    script = f"""
        // Helper function to check if an element is visible
        function isElementVisible(element) {{
            var rect = element.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0 ||
                rect.top >= (window.innerHeight || document.documentElement.clientHeight) ||
                rect.bottom <= 0 ||
                rect.left >= (window.innerWidth || document.documentElement.clientWidth) ||
                rect.right <= 0) {{
                return false;
            }}
            // Check if any parent element is hidden
            var parent = element;
            while (parent) {{
                var style = window.getComputedStyle(parent);
                if (style.display === 'none' || style.visibility === 'hidden') {{
                    return false;
                }}
                parent = parent.parentElement;
            }}
            return true;
        }}

        // Remove previous labels and highlights
        document.querySelectorAll('.highlight-label').forEach(label => label.remove());
        document.querySelectorAll('.highlighted-element').forEach(element => {{
            element.classList.remove('highlighted-element');
            element.removeAttribute('data-highlighted');
        }});

        // Inject custom styles for highlighting
        var styleElement = document.getElementById('highlight-style');
        if (!styleElement) {{
            styleElement = document.createElement('style');
            styleElement.id = 'highlight-style';
            document.head.appendChild(styleElement);
        }}
        styleElement.textContent = `
            .highlighted-element {{
                border: 2px solid red !important;
                position: relative;
                box-sizing: border-box;
            }}
            .highlight-label {{
                position: absolute;
                z-index: 2147483647;
                background: yellow;
                color: black;
                font-size: 25px;
                padding: 3px 5px;
                border: 1px solid black;
                border-radius: 3px;
                white-space: nowrap;
                box-shadow: 0px 0px 2px #000;
                top: -25px;
                left: 0;
                display: none;
            }}
        `;

        // Function to create and append labels
        function createAndAdjustLabel(element, index) {{
            if (!isElementVisible(element)) return;

            element.classList.add('highlighted-element');
            var label = document.createElement('div');
            label.className = 'highlight-label';
            label.textContent = index.toString();
            label.style.display = 'block';

            // Position the label
            var rect = element.getBoundingClientRect();
            var top = rect.top + window.scrollY - 25;
            var left = rect.left + window.scrollX;

            label.style.top = top + 'px';
            label.style.left = left + 'px';

            document.body.appendChild(label);
        }}

        // Apply highlighting to matching elements
        var allElements = document.querySelectorAll('{selector}');
        var index = 1;
        allElements.forEach(element => {{
            if (!element.dataset.highlighted && isElementVisible(element)) {{
                element.dataset.highlighted = 'true';
                createAndAdjustLabel(element, index++);
            }}
        }});
    """

    driver.execute_script(script)
    return driver


def remove_highlight_and_labels(driver):
    """
    Removes all highlights and labels from the page, reverting the changes made by the highlighting function.

    Parameters:
        driver: Selenium WebDriver instance.

    Returns:
        Updated WebDriver instance with highlights removed.
    """
    selector = (
        'a, button, input, textarea, div[onclick], div[role="button"], div[tabindex], '
        'span[onclick], span[role="button"], span[tabindex]'
    )
    script = f"""
        // Remove all labels
        document.querySelectorAll('.highlight-label').forEach(label => label.remove());

        // Remove custom style for highlights
        var highlightStyle = document.getElementById('highlight-style');
        if (highlightStyle) {{
            highlightStyle.remove();
        }}

        // Remove inline styles for highlighted elements
        document.querySelectorAll('{selector}').forEach(element => {{
            element.style.border = '';
        }});
    """

    driver.execute_script(script)
    return driver
