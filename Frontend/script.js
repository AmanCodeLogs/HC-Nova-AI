// Dynamically detect environment: use local Flask URL when running locally, otherwise use production API
const BACKEND_URL = (
    window.location.hostname === "localhost" || 
    window.location.hostname === "127.0.0.1" || 
    window.location.protocol === "file:"
) ? "http://localhost:5000" : "https://hc-nova-ai.onrender.com";

// Tab Switching
function switchTab(tabId) {
    // Update Active Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${tabId}-btn`).classList.add('active');

    // Update Active Panels
    document.querySelectorAll('.view-panel').forEach(panel => panel.classList.remove('active'));
    document.getElementById(`panel-${tabId}`).classList.add('active');

    // Focus input if chat is active
    if (tabId === 'chat') {
        document.getElementById('chat-message-input').focus();
    }
}

// Display error alerts via Snackbar
function showError(message) {
    const toast = document.getElementById('toast-notification');
    const toastMsg = document.getElementById('toast-message');
    toastMsg.innerText = message;
    toast.classList.add('show');
    
    // Auto hide after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Upload and process prescription image
async function uploadPrescription(event) {
    const fileInput = event.target;
    if (!fileInput.files || fileInput.files.length === 0) return;

    const file = fileInput.files[0];
    const spinner = document.getElementById('tracker-spinner');
    const listContent = document.getElementById('timetable-content');

    // Show loading, clear contents
    spinner.style.display = 'block';
    listContent.innerHTML = '';

    const formData = new FormData();
    formData.append('prescription', file);

    try {
        const response = await fetch(`${BACKEND_URL}/api/ocr/process`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned status: ${response.status}`);
        }

        const data = await response.json();
        const timetable = data.timetable || [];

        if (timetable.length === 0) {
            listContent.innerHTML = '<div class="empty-timetable">No medication schedules extracted. Try a clearer photo.</div>';
        } else {
            timetable.forEach(item => {
                const card = document.createElement('div');
                card.className = 'med-card';
                
                card.innerHTML = `
                    <div class="med-icon-box">
                        <span class="material-symbols-rounded">medication</span>
                    </div>
                    <div class="med-info">
                        <span class="med-name">${item.medicine || 'Unknown Medicine'}</span>
                        <div class="med-meta">
                            <div class="meta-item">
                                <span class="material-symbols-rounded">access_time</span>
                                <span>${item.time || 'N/A'}</span>
                            </div>
                            <div class="meta-item">
                                <span>•</span>
                            </div>
                            <div class="meta-item">
                                <span class="material-symbols-rounded">opacity</span>
                                <span>${item.dosage || 'N/A'}</span>
                            </div>
                        </div>
                        ${item.instructions ? `<span class="med-instructions">Instructions: ${item.instructions}</span>` : ''}
                    </div>
                `;
                listContent.appendChild(card);
            });
        }
    } catch (err) {
        showError(`Failed to process prescription: ${err.message}`);
        listContent.innerHTML = '<div class="empty-timetable">Error loading schedule. Please try again.</div>';
    } finally {
        spinner.style.display = 'none';
        fileInput.value = ''; // Reset file input
    }
}

// Chat Message handler
async function sendChatMessage() {
    const input = document.getElementById('chat-message-input');
    const btn = document.getElementById('chat-send-btn');
    const history = document.getElementById('chat-messages');
    const text = input.value.trim();

    if (!text) return;

    // Clear input and disable elements while communicating
    input.value = '';
    input.disabled = true;
    btn.disabled = true;

    // Render User Bubble
    const userRow = document.createElement('div');
    userRow.className = 'chat-row user-msg';
    userRow.innerHTML = `
        <div class="chat-bubble">
            <span class="bubble-sender">You</span>
            <span class="bubble-text">${escapeHTML(text)}</span>
        </div>
    `;
    history.appendChild(userRow);
    history.scrollTop = history.scrollHeight;

    // Render Typing Indicator
    const typingRow = document.createElement('div');
    typingRow.className = 'chat-row ai-msg';
    typingRow.id = 'typing-indicator-row';
    typingRow.innerHTML = `
        <div class="typing-bubble">
            <span class="typing-text">Nova is typing</span>
            <div class="typing-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
    history.appendChild(typingRow);
    history.scrollTop = history.scrollHeight;

    try {
        const response = await fetch(`${BACKEND_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
            throw new Error(`Server returned status: ${response.status}`);
        }

        const data = await response.json();
        const aiText = data.text || 'No response received.';

        // Remove typing indicator
        document.getElementById('typing-indicator-row').remove();

        // Render AI Bubble
        const aiRow = document.createElement('div');
        aiRow.className = 'chat-row ai-msg';
        aiRow.innerHTML = `
            <div class="chat-bubble">
                <span class="bubble-sender">Nova AI</span>
                <span class="bubble-text">${escapeHTML(aiText)}</span>
            </div>
        `;
        history.appendChild(aiRow);
    } catch (err) {
        document.getElementById('typing-indicator-row').remove();
        showError(`Chat failed: ${err.message}`);
    } finally {
        input.disabled = false;
        btn.disabled = false;
        input.focus();
        history.scrollTop = history.scrollHeight;
    }
}

// Handle enter key submit inside text box
function handleChatSubmit(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendChatMessage();
    }
}

// Simple HTML Escaping utility for chat bubbles
function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
