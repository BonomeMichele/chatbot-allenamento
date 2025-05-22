/**
 * Script per gestione chat frontend
 */

class ChatManager {
    constructor() {
        this.currentChatId = null;
        this.isLoading = false;
        this.apiBaseUrl = '/api/v1';
        
        this.initializeElements();
        this.bindEvents();
        this.loadChatList();
        
        // Auto-resize del textarea
        this.setupTextareaAutoResize();
    }
    
    initializeElements() {
        // Chat elements
        this.chatContainer = document.getElementById('chatContainer');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.currentChatTitle = document.getElementById('currentChatTitle');
        
        // Sidebar elements
        this.chatList = document.getElementById('chatList');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.deleteAllBtn = document.getElementById('deleteAllBtn');
        this.noChatsMsg = document.getElementById('noChatsMsg');
        
        // Mobile menu
        this.menuToggle = document.getElementById('menuToggle');
        this.sidebar = document.getElementById('sidebar');
    }
    
    bindEvents() {
        // Send message events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input validation
        this.chatInput.addEventListener('input', () => this.validateInput());
        
        // Sidebar events
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        this.deleteAllBtn.addEventListener('click', () => this.deleteAllChats());
        
        // Mobile menu toggle
        this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!this.sidebar.contains(e.target) && !this.menuToggle.contains(e.target)) {
                    this.sidebar.classList.remove('show');
                }
            }
        });
    }
    
    setupTextareaAutoResize() {
        this.chatInput.addEventListener('input', () => {
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 150) + 'px';
        });
    }
    
    validateInput() {
        const hasContent = this.chatInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasContent || this.isLoading;
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isLoading) return;
        
        this.isLoading = true;
        this.sendBtn.disabled = true;
        
        try {
            // Add user message to chat
            this.addMessage(message, 'user');
            
            // Clear input
            this.chatInput.value = '';
            this.chatInput.style.height = 'auto';
            
            // Show loading indicator
            this.showLoading();
            
            // Send message to API
            const response = await fetch(`${this.apiBaseUrl}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    chat_id: this.currentChatId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Hide loading indicator
            this.hideLoading();
            
            // Update current chat ID if new chat
            if (!this.currentChatId) {
                this.currentChatId = data.chat_id;
                this.currentChatTitle.textContent = data.title;
            }
            
            // Add assistant response to chat
            this.addMessage(data.assistant_message.content, 'assistant', {
                type: data.assistant_message.type,
                sources: data.assistant_message.sources
            });
            
            // Refresh chat list
            this.loadChatList();
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideLoading();
            this.addMessage('Si è verificato un errore. Riprova tra poco.', 'assistant', { type: 'error' });
        } finally {
            this.isLoading = false;
            this.validateInput();
        }
    }
    
    addMessage(content, role, options = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        // Format workout content if it's a workout type
        if (options.type === 'workout') {
            messageDiv.innerHTML = this.formatWorkoutContent(content);
            messageDiv.classList.add('workout-message');
        } else {
            messageDiv.innerHTML = this.formatMessageContent(content);
        }
        
        // Add sources if available
        if (options.sources && options.sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            sourcesDiv.innerHTML = `<strong>Fonti:</strong> ${options.sources.join(', ')}`;
            messageDiv.appendChild(sourcesDiv);
        }
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessageContent(content) {
        // Convert markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/#{1,6}\s*(.*?)$/gm, '<h3>$1</h3>')
            .replace(/- (.*?)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    }
    
    formatWorkoutContent(content) {
        // Enhanced formatting for workout content
        let formatted = content
            .replace(/^# (.*?)$/gm, '<h2 class="workout-title">🏋️ $1</h2>')
            .replace(/^## (.*?)$/gm, '<h3 class="workout-section">$1</h3>')
            .replace(/^### (.*?)$/gm, '<h4 class="workout-subsection">$1</h4>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Format tables
        const tableRegex = /\|(.+)\|\n\|[-\s\|:]+\|\n((?:\|.*\|\n?)*)/g;
        formatted = formatted.replace(tableRegex, (match, headers, rows) => {
            const headerCells = headers.split('|').map(cell => cell.trim()).filter(cell => cell);
            const rowData = rows.trim().split('\n').map(row => 
                row.split('|').map(cell => cell.trim()).filter(cell => cell)
            );
            
            let table = '<table class="exercise-table"><thead><tr>';
            headerCells.forEach(header => {
                table += `<th>${header}</th>`;
            });
            table += '</tr></thead><tbody>';
            
            rowData.forEach(row => {
                table += '<tr>';
                row.forEach(cell => {
                    table += `<td>${cell}</td>`;
                });
                table += '</tr>';
            });
            
            table += '</tbody></table>';
            return table;
        });
        
        // Format lists
        formatted = formatted
            .replace(/^- (.*?)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            .replace(/\n/g, '<br>');
        
        return `<div class="workout-content">${formatted}</div>`;
    }
    
    showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.id = 'loadingIndicator';
        loadingDiv.innerHTML = `
            <span class="loading-text">Sto pensando...</span>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.chatContainer.appendChild(loadingDiv);
        this.scrollToBottom();
    }
    
    hideLoading() {
        const loadingDiv = document.getElementById('loadingIndicator');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
    
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    async loadChatList() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat/list`);
            if (!response.ok) throw new Error('Failed to load chats');
            
            const data = await response.json();
            this.renderChatList(data.chats);
            
        } catch (error) {
            console.error('Error loading chat list:', error);
        }
    }
    
    renderChatList(chats) {
        if (chats.length === 0) {
            this.noChatsMsg.style.display = 'block';
            return;
        }
        
        this.noChatsMsg.style.display = 'none';
        
        // Clear existing chat items
        const existingItems = this.chatList.querySelectorAll('.chat-item');
        existingItems.forEach(item => item.remove());
        
        chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            if (chat.id === this.currentChatId) {
                chatItem.classList.add('active');
            }
            
            chatItem.innerHTML = `
                <div class="chat-title" title="${chat.title}">${chat.title}</div>
                <button class="delete-chat" onclick="chatManager.deleteChat('${chat.id}')" title="Elimina chat">
                    <i class="fa-solid fa-trash"></i>
                </button>
            `;
            
            // Add click event to load chat
            chatItem.addEventListener('click', (e) => {
                if (!e.target.closest('.delete-chat')) {
                    this.loadChat(chat.id, chat.title);
                }
            });
            
            this.chatList.insertBefore(chatItem, this.noChatsMsg);
        });
    }
    
    async loadChat(chatId, title) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat/${chatId}`);
            if (!response.ok) throw new Error('Failed to load chat');
            
            const chat = await response.json();
            
            // Clear current chat
            this.clearChat();
            
            // Set current chat
            this.currentChatId = chatId;
            this.currentChatTitle.textContent = title;
            
            // Render messages
            chat.messages.forEach(message => {
                this.addMessage(message.content, message.role, {
                    type: message.type,
                    sources: message.sources
                });
            });
            
            // Update active chat in sidebar
            this.updateActiveChatInSidebar(chatId);
            
            // Close sidebar on mobile
            if (window.innerWidth <= 768) {
                this.sidebar.classList.remove('show');
            }
            
        } catch (error) {
            console.error('Error loading chat:', error);
            alert('Errore nel caricamento della chat');
        }
    }
    
    updateActiveChatInSidebar(activeChatId) {
        const chatItems = this.chatList.querySelectorAll('.chat-item');
        chatItems.forEach(item => {
            item.classList.remove('active');
            const deleteBtn = item.querySelector('.delete-chat');
            if (deleteBtn && deleteBtn.onclick.toString().includes(activeChatId)) {
                item.classList.add('active');
            }
        });
    }
    
    startNewChat() {
        this.clearChat();
        this.currentChatId = null;
        this.currentChatTitle.textContent = 'Nuova Chat';
        
        // Remove active class from all chat items
        const chatItems = this.chatList.querySelectorAll('.chat-item');
        chatItems.forEach(item => item.classList.remove('active'));
        
        // Show welcome message
        this.showWelcomeMessage();
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            this.sidebar.classList.remove('show');
        }
        
        // Focus input
        this.chatInput.focus();
    }
    
    clearChat() {
        // Remove all messages except welcome message
        const messages = this.chatContainer.querySelectorAll('.message, .loading');
        messages.forEach(message => message.remove());
    }
    
    showWelcomeMessage() {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <h2>🏋️ Benvenuto nel Chatbot Allenamento!</h2>
            <p>Sono il tuo assistente personale per la creazione di schede di allenamento personalizzate.</p>
            <p>Dimmi i tuoi obiettivi, il tuo livello di esperienza e quanti giorni vuoi allenarti, e creerò una scheda perfetta per te!</p>
            <p><strong>Esempi di richieste:</strong></p>
            <ul style="text-align: left; margin-top: 10px; display: inline-block;">
                <li>"Sono un principiante, voglio iniziare ad allenarmi 3 volte a settimana"</li>
                <li>"Voglio aumentare la forza, ho esperienza intermedia"</li>
                <li>"Come si esegue correttamente lo squat?"</li>
                <li>"Scheda per dimagrimento, 4 giorni a settimana"</li>
            </ul>
        `;
        
        this.chatContainer.appendChild(welcomeDiv);
    }
    
    async deleteChat(chatId) {
        if (!confirm('Sei sicuro di voler eliminare questa chat?')) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat/${chatId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to delete chat');
            
            // If deleted chat is current, start new chat
            if (chatId === this.currentChatId) {
                this.startNewChat();
            }
            
            // Refresh chat list
            this.loadChatList();
            
        } catch (error) {
            console.error('Error deleting chat:', error);
            alert('Errore nell\'eliminazione della chat');
        }
    }
    
    async deleteAllChats() {
        if (!confirm('Sei sicuro di voler eliminare TUTTE le chat? Questa azione non può essere annullata.')) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to delete all chats');
            
            const result = await response.json();
            
            // Start new chat
            this.startNewChat();
            
            // Refresh chat list
            this.loadChatList();
            
            alert(`${result.deleted_count} chat eliminate con successo`);
            
        } catch (error) {
            console.error('Error deleting all chats:', error);
            alert('Errore nell\'eliminazione delle chat');
        }
    }
    
    toggleSidebar() {
        this.sidebar.classList.toggle('show');
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new ChatManager();
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        document.getElementById('sidebar').classList.remove('show');
    }
});
