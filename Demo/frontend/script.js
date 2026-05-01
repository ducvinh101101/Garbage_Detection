document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    
    const apiKeyModal = document.getElementById('api-key-modal');
    const apiKeyInput = document.getElementById('api-key-input');
    const saveApiKeyBtn = document.getElementById('save-api-key');
    const settingsBtn = document.getElementById('settings-btn');
    
    const uploadBtn = document.getElementById('upload-btn');
    const imageUpload = document.getElementById('image-upload');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeImageBtn = document.getElementById('remove-image-btn');

    let chatHistory = [];
    let currentImageBase64 = null;
    
    // Load API Key from localStorage
    let apiKey = localStorage.getItem('gemini_api_key');
    if (!apiKey) {
        showModal();
    }

    settingsBtn.addEventListener('click', showModal);

    function showModal() {
        if (apiKey) {
            apiKeyInput.value = apiKey;
        }
        apiKeyModal.classList.add('active');
    }

    function hideModal() {
        apiKeyModal.classList.remove('active');
    }

    saveApiKeyBtn.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            apiKey = key;
            localStorage.setItem('gemini_api_key', key);
            hideModal();
            
            // Add a welcome message if history is empty
            if (chatHistory.length === 0) {
                // Do nothing, keep the default welcome message
            }
        } else {
            alert('Vui lòng nhập API Key hợp lệ!');
        }
    });

    // Close modal on outside click if API key exists
    apiKeyModal.addEventListener('click', (e) => {
        if (e.target === apiKeyModal && apiKey) {
            hideModal();
        }
    });

    // Image Upload Functionality
    uploadBtn.addEventListener('click', () => {
        imageUpload.click();
    });

    imageUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                currentImageBase64 = event.target.result;
                imagePreview.src = currentImageBase64;
                imagePreviewContainer.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    removeImageBtn.addEventListener('click', () => {
        currentImageBase64 = null;
        imageUpload.value = '';
        imagePreviewContainer.classList.add('hidden');
        imagePreview.src = '';
    });

    // Chat functionality
    function addMessage(content, role, imageBase64 = null) {
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (role === 'assistant') {
            // Use marked to parse markdown
            messageContent.innerHTML = marked.parse(content);
        } else {
            if (imageBase64) {
                const imgHtml = `<img src="${imageBase64}" style="max-width: 200px; border-radius: 8px; margin-bottom: 10px; display: block;">`;
                messageContent.innerHTML = imgHtml + (content ? `<span>${content}</span>` : '');
            } else {
                messageContent.textContent = content;
            }
        }
        
        wrapper.appendChild(avatar);
        wrapper.appendChild(messageContent);
        chatBox.appendChild(wrapper);
        
        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text && !currentImageBase64) return;
        
        if (!apiKey) {
            showModal();
            return;
        }

        // Add user message to UI
        addMessage(text, 'user', currentImageBase64);
        userInput.value = '';
        
        const imageToSend = currentImageBase64;
        
        // Clear image preview
        currentImageBase64 = null;
        imageUpload.value = '';
        imagePreviewContainer.classList.add('hidden');
        imagePreview.src = '';
        
        // Show typing indicator
        typingIndicator.classList.remove('hidden');
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    history: chatHistory,
                    prompt: text,
                    api_key: apiKey,
                    image: imageToSend
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Lỗi server');
            }

            const data = await response.json();
            
            // Add assistant message to UI
            addMessage(data.answer, 'assistant');
            
            // Update history
            let userHistoryContent = text;
            if (imageToSend) {
                userHistoryContent = "[Đã gửi ảnh] " + text;
            }
            chatHistory.push({ role: 'user', content: userHistoryContent });
            chatHistory.push({ role: 'assistant', content: data.answer });
            
        } catch (error) {
            addMessage(`Xin lỗi, đã xảy ra lỗi: ${error.message}`, 'assistant');
        } finally {
            // Hide typing indicator
            typingIndicator.classList.add('hidden');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
