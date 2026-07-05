/**
 * Chat Widget — ПравоАгент
 * Reusable AI Agent chat component
 * Connects to POST /api/agent/chat
 *
 * Usage:
 *   <div class="chat-widget" data-agent-type="litigation"></div>
 *   new ChatWidget(el);
 *
 * Vanilla JS (no dependencies). Matches ПравоАгент design system.
 */
class ChatWidget {
    /**
     * @param {HTMLElement} containerEl  DOM element to mount the chat into
     * @param {Object}      options
     * @param {string}      options.agentType    — one of: litigation, contracts, general_dept, legal_opinion, head_legal, admin
     * @param {string}      options.placeholder  — input placeholder text
     * @param {string}      options.title        — agent display name
     * @param {string}      options.welcomeText  — first message from agent
     */
    constructor(containerEl, options = {}) {
        if (!containerEl) throw new Error('ChatWidget: container element is required');

        this.container = containerEl;
        this.options = {
            agentType: containerEl.dataset.agentType || 'general_dept',
            placeholder: containerEl.dataset.placeholder || 'Введите ваш вопрос...',
            title: containerEl.dataset.title || 'AI-агент',
            welcomeText: containerEl.dataset.welcomeText || '',
            ...options,
        };

        // Build welcome text from agent type if not provided
        if (!this.options.welcomeText) {
            this.options.welcomeText = this._defaultWelcome();
        }

        /** @type {Array<{role: string, text: string}>} */
        this.messages = [];
        this.conversationId = null;
        this._abortController = null;
        this._streamInterval = null;

        this.init();
    }

    // ————————————————————————————————————————
    // Agent-type → default welcome messages
    // ————————————————————————————————————————
    _defaultWelcome() {
        const map = {
            litigation:
                'Здравствуйте! Я AI-агент "Судебный юрист". Чем могу помочь? Я могу подготовить иск, претензию, жалобу или помочь с анализом дела.',
            contracts:
                'Добрый день! Я AI-агент "Договорник". Помогу подготовить, проверить и согласовать договоры. Выберите шаблон или опишите задачу.',
            general_dept:
                'Здравствуйте! Я AI-агент "Общий отдел". Помогу с доверенностями, нотариатом, НПА и реестрами.',
            legal_opinion:
                'Добрый день! Я AI-агент "LegalOpinion". Помогу подготовить юридические заключения по закупкам, налогам, трудовому и корпоративному праву. Загрузите материалы или опишите ситуацию.',
            head_legal:
                'Здравствуйте! Я AI-агент "Head of Legal". Помогу с аналитикой по KPI, загрузкой команды, отчётами и стратегическими решениями.',
            admin:
                'Здравствуйте! Я AI-агент "Администратор". Помогу с управлением пользователями, тенантами, лимитами LLM и системными настройками.',
        };
        return map[this.options.agentType] || map.general_dept;
    }

    // ————————————————————————————————————————
    // Init
    // ————————————————————————————————————————
    init() {
        this.render();
        this.bindEvents();
        this.addWelcomeMessage();
    }

    // ————————————————————————————————————————
    // Render
    // ————————————————————————————————————————
    render() {
        this.container.classList.add('chat-widget');
        this.container.style.cssText =
            'display:flex;flex-direction:column;height:100%;overflow:hidden;';

        this.container.innerHTML =
            '<div class="chat-messages" style="flex:1;overflow-y:auto;padding:var(--space-md);display:flex;flex-direction:column;gap:var(--space-sm);">' +
            '</div>' +
            '<div class="chat-input-bar" style="border-top:1px solid var(--color-border);padding:var(--space-sm) var(--space-md);display:flex;gap:var(--space-xs);align-items:center;background:var(--color-bg-alt);">' +
                '<input type="text" class="chat-input form-input" placeholder="' +
                    this._escapeHtml(this.options.placeholder) +
                    '" style="flex:1;min-width:0;" autocomplete="off">' +
                '<button class="chat-send-btn btn btn-sm" title="Отправить" style="flex-shrink:0;">' +
                    '&#10148;' +
                '</button>' +
            '</div>';

        this.messagesEl = this.container.querySelector('.chat-messages');
        this.inputEl = this.container.querySelector('.chat-input');
        this.sendBtn = this.container.querySelector('.chat-send-btn');
    }

    // ————————————————————————————————————————
    // Events
    // ————————————————————————————————————————
    bindEvents() {
        // Send on click
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Send on Enter
        this.inputEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize input on input
        this.inputEl.addEventListener('input', () => {
            // simple: no multi-line for now
        });
    }

    // ————————————————————————————————————————
    // Welcome
    // ————————————————————————————————————————
    addWelcomeMessage() {
        this.addMessage('agent', this.options.welcomeText);
    }

    // ————————————————————————————————————————
    // Send message
    // ————————————————————————————————————————
    async sendMessage() {
        const text = this.inputEl.value.trim();
        if (!text) return;

        // Show user message
        this.addMessage('user', text);
        this.inputEl.value = '';
        this.inputEl.disabled = true;
        this.sendBtn.disabled = true;

        // Show typing indicator
        this.showTyping();

        // Abort any previous in-flight request
        if (this._abortController) {
            this._abortController.abort();
        }
        this._abortController = new AbortController();

        try {
            const response = await this._apiCall(text, this._abortController.signal);

            this.hideTyping();
            this.streamMessage(response.response);

            // Store conversation (client-side)
            this.messages.push({ role: 'user', text: text });
            this.messages.push({ role: 'agent', text: response.response });

            // Optional: update conversation ID if the API returns one (currently not)
            if (response.conversation_id) {
                this.conversationId = response.conversation_id;
            }
        } catch (err) {
            this.hideTyping();
            if (err.name === 'AbortError') return;

            this.addMessage(
                'agent',
                '<span style="color:var(--color-danger);">&#9888; Ошибка соединения: ' +
                    this._escapeHtml(err.message || 'не удалось получить ответ от сервера') +
                    '</span>'
            );
        } finally {
            this.inputEl.disabled = false;
            this.sendBtn.disabled = false;
            this.inputEl.focus();
            this._abortController = null;
        }
    }

    // ————————————————————————————————————————
    // API call to /api/agent/chat
    // ————————————————————————————————————————
    async _apiCall(text, signal) {
        const token = this._getToken();

        const resp = await fetch('/api/agent/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
                ...(token ? { Authorization: 'Bearer ' + token } : {}),
            },
            body: JSON.stringify({
                message: text,
                agent_type: this.options.agentType,
                conversation_id: this.conversationId,
            }),
            signal,
        });

        if (!resp.ok) {
            let detail = 'HTTP ' + resp.status;
            try {
                const errBody = await resp.json();
                if (errBody.detail) detail = errBody.detail;
            } catch (_) {
                // ignore parse error
            }
            throw new Error(detail);
        }

        return await resp.json();
    }

    /**
     * Read Bearer token from access_token cookie
     */
    _getToken() {
        const m = document.cookie.match(/access_token=([^;]+)/);
        return m ? m[1] : '';
    }

    // ————————————————————————————————————————
    // Message rendering
    // ————————————————————————————————————————
    addMessage(role, text) {
        const isUser = role === 'user';
        const div = document.createElement('div');
        div.className = 'chat-message chat-message-' + (isUser ? 'user' : 'agent');
        div.style.cssText =
            'max-width:85%;padding:var(--space-sm) var(--space-md);' +
            'border-radius:var(--radius-md);font-size:var(--font-size-sm);' +
            'line-height:1.5;word-wrap:break-word;overflow-wrap:break-word;' +
            'animation:fadeIn 0.2s ease;';

        if (isUser) {
            div.style.cssText +=
                'align-self:flex-end;' +
                'background:var(--color-primary-light);' +
                'border-bottom-right-radius:var(--radius-sm);';
            div.innerHTML =
                '<div class="text-xs text-muted" style="margin-bottom:4px;font-weight:600;">Вы</div>' +
                '<div>' + this._escapeHtml(text) + '</div>';
        } else {
            div.style.cssText +=
                'align-self:flex-start;' +
                'background:var(--color-bg-hover);' +
                'border-bottom-left-radius:var(--radius-sm);';
            div.innerHTML =
                '<div class="text-xs text-muted" style="margin-bottom:4px;font-weight:600;">' +
                    this._escapeHtml(this.options.title) +
                '</div>' +
                '<div>' + text + '</div>';
        }

        this.messagesEl.appendChild(div);
        this._scrollToBottom();
    }

    // ————————————————————————————————————————
    // Typing indicator
    // ————————————————————————————————————————
    showTyping() {
        if (this._typingEl) return;

        const div = document.createElement('div');
        div.className = 'chat-message chat-message-typing chat-message-agent';
        div.style.cssText =
            'max-width:85%;padding:var(--space-sm) var(--space-md);' +
            'border-radius:var(--radius-md);font-size:var(--font-size-sm);' +
            'align-self:flex-start;' +
            'background:var(--color-bg-hover);' +
            'border-bottom-left-radius:var(--radius-sm);' +
            'animation:fadeIn 0.2s ease;';

        div.innerHTML =
            '<div class="text-xs text-muted" style="margin-bottom:4px;font-weight:600;">' +
                this._escapeHtml(this.options.title) +
            '</div>' +
            '<div class="chat-typing-indicator" style="display:flex;gap:4px;align-items:center;padding:4px 0;">' +
                '<span style="width:6px;height:6px;border-radius:50%;background:var(--color-text-muted);animation:typingBounce 1.4s infinite ease-in-out;"></span>' +
                '<span style="width:6px;height:6px;border-radius:50%;background:var(--color-text-muted);animation:typingBounce 1.4s infinite ease-in-out;animation-delay:0.2s;"></span>' +
                '<span style="width:6px;height:6px;border-radius:50%;background:var(--color-text-muted);animation:typingBounce 1.4s infinite ease-in-out;animation-delay:0.4s;"></span>' +
            '</div>';

        this.messagesEl.appendChild(div);
        this._typingEl = div;
        this._scrollToBottom();
    }

    hideTyping() {
        if (this._typingEl) {
            this._typingEl.remove();
            this._typingEl = null;
        }
    }

    // ————————————————————————————————————————
    // Streaming response (character by character)
    // ————————————————————————————————————————
    streamMessage(text) {
        // Cancel any previous stream
        if (this._streamInterval) {
            clearInterval(this._streamInterval);
            this._streamInterval = null;
            // Remove leftover cursor from previous stream
            const oldCursor = this.messagesEl.querySelector('.chat-streaming-cursor');
            if (oldCursor) oldCursor.remove();
        }

        const div = document.createElement('div');
        div.className = 'chat-message chat-message-agent';
        div.style.cssText =
            'max-width:85%;padding:var(--space-sm) var(--space-md);' +
            'border-radius:var(--radius-md);font-size:var(--font-size-sm);' +
            'line-height:1.5;word-wrap:break-word;overflow-wrap:break-word;' +
            'animation:fadeIn 0.2s ease;' +
            'align-self:flex-start;' +
            'background:var(--color-bg-hover);' +
            'border-bottom-left-radius:var(--radius-sm);';

        div.innerHTML =
            '<div class="text-xs text-muted" style="margin-bottom:4px;font-weight:600;">' +
                this._escapeHtml(this.options.title) +
            '</div>' +
            '<div class="chat-message-content" style="min-height:1.2em;"></div>';

        this.messagesEl.appendChild(div);
        const contentEl = div.querySelector('.chat-message-content');

        let i = 0;
        this._streamInterval = setInterval(() => {
            if (i < text.length) {
                // Remove cursor, append character, add cursor back
                const cursor = contentEl.querySelector('.chat-streaming-cursor');
                if (cursor) cursor.remove();
                contentEl.appendChild(document.createTextNode(text[i]));
                const newCursor = document.createElement('span');
                newCursor.className = 'chat-streaming-cursor';
                newCursor.textContent = '|';
                newCursor.style.cssText = 'animation:blink 0.8s infinite;';
                contentEl.appendChild(newCursor);
                i++;
                this._scrollToBottom();
            } else {
                clearInterval(this._streamInterval);
                this._streamInterval = null;
                // Remove final cursor
                const cursor = contentEl.querySelector('.chat-streaming-cursor');
                if (cursor) cursor.remove();
            }
        }, 20);
    }

    // ————————————————————————————————————————
    // Scroll
    // ————————————————————————————————————————
    _scrollToBottom() {
        requestAnimationFrame(() => {
            this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
        });
    }

    // ————————————————————————————————————————
    // Utils
    // ————————————————————————————————————————
    _escapeHtml(str) {
        if (!str) return '';
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }
}

// ————————————————————————————————————————
// Inject keyframe animations once
// ————————————————————————————————————————
(function injectChatStyles() {
    if (document.getElementById('chat-widget-styles')) return;

    var style = document.createElement('style');
    style.id = 'chat-widget-styles';
    style.textContent =
        '@keyframes fadeIn {' +
            'from { opacity: 0; transform: translateY(6px); }' +
            'to { opacity: 1; transform: translateY(0); }' +
        '}' +
        '@keyframes typingBounce {' +
            '0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }' +
            '40% { transform: scale(1); opacity: 1; }' +
        '}' +
        '@keyframes blink {' +
            '0%, 100% { opacity: 1; }' +
            '50% { opacity: 0; }' +
        '}';
    document.head.appendChild(style);

    // Auto-initialize all .chat-widget containers on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', function autoInitChatWidgets() {
        document.querySelectorAll('.chat-widget[data-auto-init]').forEach(function (el) {
            new ChatWidget(el);
        });
    });
})();
