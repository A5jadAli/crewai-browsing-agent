from typing import Union
from selenium.webdriver import WebDriver

class HighlightUtility:
    @staticmethod
    def highlight_elements_with_labels(driver: WebDriver, selector: str) -> WebDriver:
        """
        Highlight elements matching the given CSS selector with red borders and numbered labels.

        :param driver: Selenium WebDriver instance
        :param selector: CSS selector for elements to highlight
        :return: Modified WebDriver instance
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

        // Remove previous labels and styles
        document.querySelectorAll('.highlight-label').forEach(function(label) {{
            label.remove();
        }});
        document.querySelectorAll('.highlighted-element').forEach(function(element) {{
            element.classList.remove('highlighted-element');
            element.removeAttribute('data-highlighted');
        }});

        // Inject custom highlighting style
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

        // Function to create and append a label to the body
        function createAndAdjustLabel(element, index) {{
            if (!isElementVisible(element)) return;

            element.classList.add('highlighted-element');
            var label = document.createElement('div');
            label.className = 'highlight-label';
            label.textContent = index.toString();
            label.style.display = 'block';

            // Calculate label position
            var rect = element.getBoundingClientRect();
            var top = rect.top + window.scrollY - 25;
            var left = rect.left + window.scrollX;

            label.style.top = top + 'px';
            label.style.left = left + 'px';

            document.body.appendChild(label);
        }}

        // Select and highlight elements
        var allElements = document.querySelectorAll('{selector}');
        var index = 1;
        allElements.forEach(function(element) {{
            if (!element.dataset.highlighted && isElementVisible(element)) {{
                element.dataset.highlighted = 'true';
                createAndAdjustLabel(element, index++);
            }}
        }});
        """

        driver.execute_script(script)
        return driver

    @staticmethod
    def remove_highlight_and_labels(driver: WebDriver) -> WebDriver:
        """
        Remove all red borders and labels from webpage elements.

        :param driver: Selenium WebDriver instance
        :return: Modified WebDriver instance
        """
        selector = (
            'a, button, input, textarea, div[onclick], div[role="button"], div[tabindex], '
            'span[onclick], span[role="button"], span[tabindex]'
        )
        script = f"""
        // Remove all labels
        document.querySelectorAll('.highlight-label').forEach(function(label) {{
            label.remove();
        }});

        // Remove the added style for red borders
        var highlightStyle = document.getElementById('highlight-style');
        if (highlightStyle) {{
            highlightStyle.remove();
        }}

        // Remove inline styles added by highlighting function
        document.querySelectorAll('{selector}').forEach(function(element) {{
            element.style.border = '';
        }});
        """

        driver.execute_script(script)
        return driver