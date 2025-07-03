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
            <p><strong>Query:</strong> ${data.query}</p>
            <p><strong>Agents Executed:</strong> ${data.agents_executed}</p>
            <p><strong>Status:</strong> ${data.status}</p>
            <p><strong>Summary:</strong> ${data.final_summary}</p>
        </div>
    `;

    // Display individual agent results
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
