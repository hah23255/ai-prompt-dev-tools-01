document.addEventListener('DOMContentLoaded', () => {
    const promptTextarea = document.getElementById('prompt-text');
    const enhanceButton = document.getElementById('enhance-btn');
    const processingStatusDivs = {
        topicAnalysis: document.querySelector('div:contains("Topic Analysis")').previousElementSibling,
        categoryBreakdown: document.querySelector('div:contains("Category Breakdown")').previousElementSibling,
        iterativeRefinement: document.querySelector('div:contains("Iterative Refinement")').previousElementSibling,
        researchIntegration: document.querySelector('div:contains("Research Integration")').previousElementSibling,
    };
    const enhancedPromptDiv = document.querySelector('h2:contains("Enhanced Prompt")').nextElementSibling;

    let websocket;

    function connectWebSocket() {
        // Assuming the WebSocket endpoint is at the root /ws
        websocket = new WebSocket(`ws://${window.location.host}/ws/enhance-prompt`);

        websocket.onopen = function(event) {
            console.log("WebSocket connection opened:", event);
            // Maybe enable the button or show a ready status
        };

        websocket.onmessage = function(event) {
            console.log("WebSocket message received:", event.data);
            const data = JSON.parse(event.data);
            // Handle different message types from the backend
            if (data.type === 'status') {
                // Update processing status indicators
                if (processingStatusDivs[data.agent]) {
                    processingStatusDivs[data.agent].textContent = data.status === 'completed' ? '✅' : '⏳';
                }
            } else if (data.type === 'enhanced_prompt') {
                // Display the final enhanced prompt
                enhancedPromptDiv.textContent = data.content;
            } else if (data.type === 'error') {
                console.error("Error from backend:", data.message);
                // Display error to the user
                enhancedPromptDiv.textContent = `Error: ${data.message}`;
            }
        };

        websocket.onerror = function(event) {
            console.error("WebSocket error observed:", event);
            // Display error to the user
            enhancedPromptDiv.textContent = "WebSocket error. Could not connect to the server.";
        };

        websocket.onclose = function(event) {
            console.log("WebSocket connection closed:", event);
            if (event.wasClean) {
                console.log(`Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                console.error('Connection died');
            }
            // Attempt to reconnect after a delay
            setTimeout(connectWebSocket, 5000);
        };
    }

    // Initial WebSocket connection
    connectWebSocket();

    enhanceButton.addEventListener('click', () => {
        const prompt = promptTextarea.value;
        if (prompt && websocket && websocket.readyState === WebSocket.OPEN) {
            // Reset status indicators
            Object.values(processingStatusDivs).forEach(div => div.textContent = '⏳');
            enhancedPromptDiv.textContent = 'Processing...';

            // Send the prompt to the backend
            websocket.send(JSON.stringify({ type: 'enhance_request', prompt: prompt }));
        } else {
            console.warn("Prompt is empty or WebSocket is not open.");
            if (!websocket || websocket.readyState !== WebSocket.OPEN) {
                 enhancedPromptDiv.textContent = "Server not connected. Please wait or refresh.";
            }
        }
    });
});

// Helper function to find elements by text content (basic implementation)
// Note: This is a simple helper and might need refinement for complex HTML structures
function findElementByText(selector, text) {
    const elements = document.querySelectorAll(selector);
    for (const element of elements) {
        if (element.textContent.includes(text)) {
            return element;
        }
    }
    return null;
}

// Extend Element prototype to use the helper
if (!Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
}

if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
        let el = this;
        do {
            if (el.matches(s)) return el;
            el = el.parentElement || el.parentNode;
        } while (el !== null && el.nodeType === 1);
        return null;
    };
}

// Add a simple contains method for convenience (not standard)
Element.prototype.containsText = function(text) {
    return this.textContent.includes(text);
};

// Add a simple querySelector that searches for text content
document.querySelector = (function(origQSA) {
    return function(selector) {
        // Check if the selector contains ':contains()'
        const containsMatch = selector.match(/^(.*?):contains\(['"](.*?)['"]\)(.*)$/);
        if (containsMatch) {
            const baseSelector = containsMatch[1] + containsMatch[3];
            const textToFind = containsMatch[2];
            const elements = origQSA.call(document, baseSelector); // This should be querySelectorAll
            // Correcting to use querySelectorAll for iteration
            const allElements = document.querySelectorAll(baseSelector);
            for (const element of allElements) {
                if (element.textContent.includes(textToFind)) {
                    return element;
                }
            }
            return null; // No element found with the text
        } else {
            // If no ':contains()', use the original querySelector
            return origQSA.call(document, selector);
        }
    };
})(document.querySelector);