document.addEventListener('DOMContentLoaded', () => {
    const promptTextarea = document.getElementById('prompt-text');
    const enhanceButton = document.getElementById('enhance-btn');
    // Select all status icon divs using a class and data attribute
    const statusIcons = document.querySelectorAll('.status-icon');
    const enhancedPromptDiv = document.getElementById('enhanced-prompt-output');

    // Map data-status-for values to the actual icon elements
    const processingStatusIcons = {};
    statusIcons.forEach(icon => {
        const statusKey = icon.getAttribute('data-status-for');
        if (statusKey) {
            processingStatusIcons[statusKey] = icon;
        }
    });

    let websocket;

    function connectWebSocket() {
        // Assuming the WebSocket endpoint is at the root /ws
        // Use window.location.protocol to determine ws or wss
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        websocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/enhance-prompt`);

        websocket.onopen = function(event) {
            console.log("WebSocket connection opened:", event);
            // Maybe enable the button or show a ready status
            enhancedPromptDiv.textContent = 'Ready. Enter your prompt above.';
        };

        websocket.onmessage = function(event) {
            console.log("WebSocket message received:", event.data);
            try {
                const data = JSON.parse(event.data);
                // Handle different message types from the backend
                if (data.status === 'processing') {
                    // Update processing status indicators
                    // The backend should send the agent name in the 'stage' field
                    if (processingStatusIcons[data.stage]) {
                        processingStatusIcons[data.stage].textContent = '⏳'; // Indicate processing
                        // Optionally, update message or styling for the active stage
                    }
                     enhancedPromptDiv.textContent = data.message || 'Processing...'; // Display general processing message
                } else if (data.status === 'complete') {
                    // Display the final enhanced prompt
                    enhancedPromptDiv.textContent = data.enhanced_prompt; // Use data.enhanced_prompt as per backend response
                    // Mark all stages as complete
                    Object.values(processingStatusIcons).forEach(icon => icon.textContent = '✅');
                    console.log("Processing Details:", data.processing_details); // Log details if available
                } else if (data.status === 'error') {
                    console.error("Error from backend:", data.message);
                    // Display error to the user
                    enhancedPromptDiv.textContent = `Error: ${data.message}`;
                     // Mark all stages with an error indicator
                    Object.values(processingStatusIcons).forEach(icon => icon.textContent = '❌');
                } else {
                     console.warn("Received unknown WebSocket message status:", data.status, data);
                }
            } catch (e) {
                console.error("Failed to parse WebSocket message:", e, event.data);
                enhancedPromptDiv.textContent = "Error processing server response.";
            }
        };

        websocket.onerror = function(event) {
            console.error("WebSocket error observed:", event);
            // Display error to the user
            enhancedPromptDiv.textContent = "WebSocket error. Could not connect to the server.";
             // Mark all stages with an error indicator
            Object.values(processingStatusIcons).forEach(icon => icon.textContent = '❌');
        };

        websocket.onclose = function(event) {
            console.log("WebSocket connection closed:", event);
            if (event.wasClean) {
                console.log(`Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                console.error('Connection died');
            }
            enhancedPromptDiv.textContent = "Connection lost. Attempting to reconnect...";
            // Attempt to reconnect after a delay
            setTimeout(connectWebSocket, 5000);
        };
    }

    // Initial WebSocket connection
    connectWebSocket();

    enhanceButton.addEventListener('click', () => {
        const prompt = promptTextarea.value.trim(); // Trim whitespace
        if (prompt && websocket && websocket.readyState === WebSocket.OPEN) {
            // Reset status indicators to initial state
            Object.values(processingStatusIcons).forEach(icon => icon.textContent = '⏳');
            enhancedPromptDiv.textContent = 'Processing...';

            // Send the prompt to the backend
            // Ensure the payload matches the backend's expected format (e.g., { "prompt": "..." })
            websocket.send(JSON.stringify({ prompt: prompt })); // Sending just the prompt content

        } else {
            console.warn("Prompt is empty or WebSocket is not open.");
            if (!prompt) {
                 enhancedPromptDiv.textContent = "Please enter a prompt to enhance.";
            } else if (!websocket || websocket.readyState !== WebSocket.OPEN) {
                 enhancedPromptDiv.textContent = "Server not connected. Please wait or refresh.";
            }
        }
    });
});

// Removed the custom querySelector helper as it's no longer needed
// using standard DOM methods with classes and data attributes.
