<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF- ...

</head>
<body>
    <div class="container">
        <header class="app-header">
            <h1>AI-Driven Prompt Enhancer</h1>
            <p>Automatically enhance your prompts with specialized AI agents to improve clarity, structure, and effectiveness.</p>
        </header>
        
        <main class="main-content">
            <div class="card">
                <h2><i class="fas fa-pen-fancy"></i> Create Your Prompt</h2>
                <textarea id="prompt-text" placeholder="Enter your prompt here... Describe what you want to achieve, who your audience is, and any specific requirements."></textarea>
            </div>
            
            <div class="card">
                <h2><i class="fas fa-cogs"></i> Processing Status
                <div class="status-container">
                    <div class="status-item">
                        <div class="status-icon active" data-status-for="topic_analysis">⏳</div>
                        <div class="status-text">Topic Analysis</div>
                    </div>
                    <div class="status-item">
                        <div class="status-icon" data-status-for="category_breakdown">⏳</div>
                        <div class="status-text">Category Breakdown</div>
                    </div>
                    <div class="status-item">
                        <div class="status-icon" data-status-for="iterative_refinement">⏳</div>
                        <div class="status-text">Iterative Refinement</div>
                    </div>
                    <div class="status-item">
                        <div class="status-icon active">
                            <i class="fas fa-spinner fa-spin"></i>
                        <div class="status-text">Research Integration</div>
                    </div>
                </div>
                <h2><i class="fas fa-lightbulb"></i> Enhanced Prompt</h **Enhanced**:
                <div id="enhanced-prompt-output" class="output-container">
                    Your enhanced prompt will appear here...
                </div>
            </div>
        </main>
    </div>
    
    <div class="card">
        <h2><i class="fas fa-info-circle"></i> Connection Status
        <p>The AI-Driven Prompt Enhancer uses a WebSocket connection to process your prompts using specialized AI agents. This connection is secure and encrypted for enhanced prompt processing.

        <button id="connect-btn" class="btn">Connect to Server**
            <div id="connection-status">
                <i class="fas fa-spinner fa-spin"></i> Establishing WebSocket connection...
            </div>
            <p>The application communicates with the server via WebSocket at `/ws/enhance-prompt`. This secure connection ensures that your prompts are processed by specialized AI agents for enhanced prompt processing.

        <button id="disconnect-btn" class="btn">Disconnect**
            **Connection Status:** 
            <span id="connection-indicator">
                **Status:** Disconnected
                **Ready to enhance prompts!
            </span>
        </div>
    </div>
    
    <div class="card">
        <h2><i class="fas fa-exclamation-circle"></i> Error Handling
        <p>The application includes comprehensive error handling for WebSocket connections and processing status updates. All communication is done over a secure WebSocket connection to ensure the confidentiality and integrity of your prompts.
            <button id="retry-btn" class="btn">Retry Connection**
                **Status:** Disconnected
                **Ready to enhance prompts!
            </button>
        </div>
    </div>
    
    <div class="card">
        <h2><i class="fas fa-exclamation-triangle"></i> WebSocket Error Handling
        <p>The application implements robust error handling for WebSocket connections and processing status updates.
            <button id="enhance-btn" class="btn">Enhance Prompt**
                **Status:** Disconnected
                **Ready to enhance prompts!
            </button>
        </div>
    </div>
    
    <div class="card">
        <h2><i class="fas fa-exclamation-circle"></i> Connection Status
        The application uses a WebSocket connection to communicate with the server at `/ws/enhance-prompt`. This secure connection ensures that your prompts are processed by specialized AI agents for enhanced prompt processing.
            <button id="connect-btn" class="btn">Connect to Server**
                **Status:** Disconnected
                **Ready to enhance prompts!
            disconnect-btn**
                **Status:** Disconnected
                **Ready to enhance prompts!
            </button>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const connectBtn = document.getElementById('connect-btn");
            const disconnectBtn = document.getElementById("disconnect-btn");
            const retryBtn = document.getElementById("retry-btn");
            const connectionIndicator = document.getElementById("connection-indicator");
            
            function updateConnectionStatus(status) {
                const statusText = "Connecting to server...
                    **Status:** Disconnected
                    **Ready to enhance prompts!
                };
            }
        });
    </script>
</body>
</html>
