document.getElementById('send-button').addEventListener('click', sendMessage);

async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    // Display user's message in chat box
    displayMessage(userInput, 'user');

    // Clear input field
    document.getElementById('user-input').value = '';

    // Get AI's response
    const aiResponse = await getAIResponse(userInput);

    // Display AI's message in chat box
    displayMessage(aiResponse, 'ai');
}

function displayMessage(message, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', `${sender}-message`);
    messageElement.innerText = message;
    chatBox.appendChild(messageElement);

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function getAIResponse(userMessage) {
    try {
        const response = await fetch('http://127.0.0.1:5000/get-ai-response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage }),
        });

        if (!response.ok) {
            throw new Error('Failed to get response from server');
        }

        const responseData = await response.json();
        return responseData.response;
    } catch (error) {
        console.error('Error:', error);
        return "Sorry, I couldn't get a response from the AI.";
    }
}
