function setExample(exampleText) {
    document.getElementById('queryInput').value = exampleText;
}

async function executeOrchestration() {
    const query = document.getElementById('queryInput').value.trim();
    const files = document.getElementById('fileInput').files;
    const executeBtn = document.getElementById('executeBtn');
    const resultsContainer = document.getElementById('resultsContainer');
    const agentProgress = document.getElementById('agentProgress');
    const finalResults = document.getElementById('finalResults');

    if (!query) {
        alert('Please enter a query describing what you want the AI to do.');
        return;
    }

    // Show loading state
    executeBtn.textContent = '🔄 Orchestrating Agents...';
    executeBtn.disabled = true;
    resultsContainer.classList.remove('hidden');
    agentProgress.innerHTML = '<div class="agent-step executing">🚀 Initializing multi-agent orchestration...</div>';
    finalResults.innerHTML = '';

    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('query', query);
        
        for (let file of files) {
            formData.append('files', file);
        }

        // Show progress steps
        updateProgress('🧠 Analyzing your request and planning agent coordination...');
        await sleep(1000);
        
        updateProgress('🤖 Deploying specialized agents for your task...');
        await sleep(1000);

        // Make API call
        const response = await fetch('/execute', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            displayResults(result.data);
        } else {
            throw new Error(result.error || 'Unknown error occurred');
        }

    } catch (error) {
        console.error('Error:', error);
        finalResults.innerHTML = `
            <div class="result-section" style="border-left: 4px solid #f44336;">
                <h4>❌ Orchestration Failed</h4>
                <p><strong>Error:</strong> ${error.message}</p>
                <p><small>Please check the backend connection and try again.</small></p>
            </div>
        `;
    } finally {
        executeBtn.textContent = '🚀 Execute Orchestration';
        executeBtn.disabled = false;
    }
}

function updateProgress(message) {
    const agentProgress = document.getElementById('agentProgress');
    const existingSteps = agentProgress.querySelectorAll('.agent-step');
    
    // Mark previous steps as completed
    existingSteps.forEach(step => {
        step.classList.remove('executing');
        step.style.borderLeftColor = '#4CAF50';
    });
    
    // Add new step
    const newStep = document.createElement('div');
    newStep.className = 'agent-step executing';
    newStep.textContent = message;
    agentProgress.appendChild(newStep);
}

function displayResults(data) {
    const agentProgress = document.getElementById('agentProgress');
    const finalResults = document.getElementById('finalResults');

    // Mark final progress step as completed
    const executingSteps = agentProgress.querySelectorAll('.executing');
    executingSteps.forEach(step => {
        step.classList.remove('executing');
        step.style.borderLeftColor = '#4CAF50';
    });

    // Add completion step
    updateProgress('✅ Multi-agent orchestration completed successfully!');

    // Display results
    let resultsHTML = `
        <div class="result-section">
            <h4>🎯 Orchestration Summary</h4>
            <p><strong>Query:</strong> ${data.query || 'N/A'}</p>
            <p><strong>Agents Executed:</strong> ${Array.isArray(data.agents_executed) ? data.agents_executed.join(', ') : 'None'}</p>
            <p><strong>Status:</strong> ${data.status || 'Unknown'}</p>
            <p><strong>Summary:</strong> ${data.summary || 'No summary available'}</p>
        </div>
    `;

    // Display individual agent results if available
    if (data.agent_results && data.agent_results.length > 0) {
        data.agent_results.forEach(result => {
            resultsHTML += `
                <div class="result-section">
                    <h4>🤖 ${result.agent} Results</h4>
                    <p><strong>Status:</strong> ${result.status}</p>
                    <p><strong>Summary:</strong> ${result.summary}</p>
                    
                    ${result.results ? `
                        <details style="margin-top: 15px;">
                            <summary style="cursor: pointer; font-weight: bold;">View Detailed Results</summary>
                            <pre style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin-top: 10px; overflow-x: auto; white-space: pre-wrap;">${JSON.stringify(result.results, null, 2)}</pre>
                        </details>
                    ` : ''}
                </div>
            `;
        });
    }

    // Display orchestration metadata if available
    if (data.orchestration_metadata) {
        resultsHTML += `
            <details style="margin-top: 20px;">
                <summary style="cursor: pointer; font-weight: bold;">🔧 Orchestration Details</summary>
                <pre style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin-top: 10px; overflow-x: auto; white-space: pre-wrap;">${JSON.stringify(data.orchestration_metadata, null, 2)}</pre>
            </details>
        `;
    }

    finalResults.innerHTML = resultsHTML;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Allow Enter key to execute (Cmd+Enter)
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('queryInput').addEventListener('keydown', function(e) {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            executeOrchestration();
        }
    });
});

// Automator Mascot Introduction
const mascotMessages = [
    "Hello! I'm your AI Automator assistant. Let me introduce our agent team! 🤖",
    "Meet our File Agent 📄 - Expert at analyzing documents and extracting insights!",
    "Our Research Agent 🔍 - Searches the web for real-time market intelligence!",
    "The Analysis Agent 🧠 - Synthesizes data into strategic recommendations!",
    "Our Mail Agent 📧 - Drafts professional emails and extracts action items!",
    "And our Calendar Agent 📅 - Manages schedules and optimizes your time!",
    "Together, we orchestrate intelligent workflows that would make Apple proud! 🍎",
    "Ready to see multi-agent coordination in action? Try one of the examples below! 🚀"
];

let currentMessageIndex = 0;
let isIntroPlaying = false;

function startMascotIntroduction() {
    if (isIntroPlaying) return;
    
    isIntroPlaying = true;
    const speechBubble = document.getElementById('speechBubble');
    const mascotText = document.getElementById('mascotText');
    
    function showNextMessage() {
        if (currentMessageIndex < mascotMessages.length) {
            // Fade out
            speechBubble.style.opacity = '0';
            
            setTimeout(() => {
                // Change text
                mascotText.textContent = mascotMessages[currentMessageIndex];
                
                // Fade in
                speechBubble.style.opacity = '1';
                currentMessageIndex++;
                
                // Schedule next message
                setTimeout(showNextMessage, 3000);
            }, 300);
        } else {
            // Introduction complete - hide mascot after a delay
            setTimeout(() => {
                const mascot = document.getElementById('automatorMascot');
                mascot.style.animation = 'slideInRight 1s ease-out reverse';
                setTimeout(() => {
                    mascot.style.display = 'none';
                    isIntroPlaying = false;
                }, 1000);
            }, 2000);
        }
    }
    
    // Start the introduction
    setTimeout(showNextMessage, 2000);
}

// Start introduction when page loads
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(startMascotIntroduction, 1000);
});

// Add click handler to replay introduction
document.addEventListener('DOMContentLoaded', function() {
    const mascot = document.getElementById('automatorMascot');
    if (mascot) {
        mascot.addEventListener('click', function() {
            if (!isIntroPlaying) {
                currentMessageIndex = 0;
                mascot.style.display = 'block';
                mascot.style.animation = 'slideInRight 1s ease-out';
                startMascotIntroduction();
            }
        });
    }
});
