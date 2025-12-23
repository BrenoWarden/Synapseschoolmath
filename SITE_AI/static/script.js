function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

let isGenerating = false;
let lastUserMessage = "";

function createMessageElement(role) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(role === 'user' ? 'user-message' : 'ai-message');
    
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    
    const toolsDiv = document.createElement('div');
    toolsDiv.classList.add('message-tools');
    
    msgDiv.appendChild(contentDiv);
    msgDiv.appendChild(toolsDiv);
    
    return { msgDiv, contentDiv, toolsDiv };
}

function renderMarkdown(target, text) {
    target.innerHTML = marked.parse(text);
    target.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
}

function addTools(role, msgDiv, contentDiv, text) {
    const toolsDiv = msgDiv.querySelector('.message-tools');
    toolsDiv.innerHTML = '';
    
    if (role === 'user') {
        const editBtn = document.createElement('button');
        editBtn.textContent = '✎';
        editBtn.title = "Editar";
        editBtn.onclick = () => editMessage(msgDiv, text);
        toolsDiv.appendChild(editBtn);
    } else {
        const likeBtn = document.createElement('button');
        likeBtn.textContent = '👍';
        likeBtn.title = "Gostei";
        likeBtn.onclick = () => sendFeedback(text, 'up');
        toolsDiv.appendChild(likeBtn);

        const dislikeBtn = document.createElement('button');
        dislikeBtn.textContent = '👎';
        dislikeBtn.title = "Não gostei";
        dislikeBtn.onclick = () => sendFeedback(text, 'down');
        toolsDiv.appendChild(dislikeBtn);

        const regenBtn = document.createElement('button');
        regenBtn.textContent = '🔄';
        regenBtn.title = "Gerar Novamente";
        regenBtn.onclick = () => regenerateResponse(msgDiv);
        toolsDiv.appendChild(regenBtn);
    }
}

async function sendFeedback(messageText, type) {
    try {
        await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText, type })
        });
    } catch (e) {
        console.error('Falha ao enviar feedback', e);
    }
}

async function editMessage(msgDiv, originalText) {
    if (isGenerating) return;
    
    let nextSibling = msgDiv.nextElementSibling;
    if (nextSibling && nextSibling.classList.contains('ai-message')) {
        nextSibling.remove();
    }
    msgDiv.remove();
    
    await fetch('/api/undo', { method: 'POST' });
    
    userInput.value = originalText;
    userInput.focus();
    autoResize(userInput);
}

async function regenerateResponse(aiMsgDiv) {
    if (isGenerating) return;
    aiMsgDiv.remove();
    await fetch('/api/undo', { method: 'POST' });
    sendMessage(lastUserMessage, true);
}

async function sendMessage(text = null, skipUserAppend = false) {
    if (isGenerating) return;
    
    const messageText = text || userInput.value.trim();
    if (!messageText) return;

    if (!text) {
        userInput.value = '';
        userInput.style.height = 'auto';
    }
    
    lastUserMessage = messageText;
    isGenerating = true;
    sendBtn.disabled = true;

    if (!skipUserAppend) {
        const { msgDiv, contentDiv } = createMessageElement('user');
        contentDiv.textContent = messageText;
        addTools('user', msgDiv, contentDiv, messageText);
        chatContainer.appendChild(msgDiv);
    }

    const { msgDiv: aiMsgDiv, contentDiv: aiContentDiv } = createMessageElement('ai');
    chatContainer.appendChild(aiMsgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    let accumulatedText = "";

    try {
        const response = await fetch('/api/stream', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: messageText })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            accumulatedText += chunk;
            renderMarkdown(aiContentDiv, accumulatedText);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        addTools('ai', aiMsgDiv, aiContentDiv, accumulatedText);
    } catch (error) {
        aiContentDiv.innerHTML += "\n\n[Erro de conexão]";
        console.error(error);
    } finally {
        isGenerating = false;
        sendBtn.disabled = false;
        if (!text) userInput.focus();
    }
}

sendBtn.addEventListener('click', () => sendMessage());

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
