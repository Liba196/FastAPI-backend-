/**
 * chatbot.js
 * The Chatbot class owns conversation state and event wiring. It composes
 * POESSAUi (DOM/animation), POESSAMessages (message model/rendering), and
 * POESSAApi (backend calls, mocked for now).
 */
(function (global) {
  'use strict';

  const Ui = global.POESSAUi;
  const Messages = global.POESSAMessages;
  const Api = global.POESSAApi;
  const { scrollToBottom, isBlank } = global.POESSAUtils;

  const SUGGESTED_QUESTIONS = [
    'እንዴት መመዝገብ እችላለሁ?',
    'አስፈላጊ ሰነዶች',
    'የጡረታ ብቃት',
    'የመገኛ አድራሻ',
  ];

  function Chatbot(rootEl) {
    this.rootEl = rootEl;
    this.history = [];
    this.hasOpenedBefore = false;
    this.isWaitingForReply = false;

    this.refs = Ui.buildWidget(rootEl);
    this._renderWelcome();
    this._bindEvents();
  }

  Chatbot.prototype._bindEvents = function () {
    const { launcher, minimizeBtn, closeBtn, textarea, sendBtn, chatWindow } = this.refs;

    launcher.addEventListener('click', () => this.toggleWindow());
    minimizeBtn.addEventListener('click', () => this.minimizeWindow());
    closeBtn.addEventListener('click', () => this.closeWindow());

    textarea.addEventListener('input', () => {
      Ui.autoResizeTextarea(textarea);
      sendBtn.disabled = isBlank(textarea.value);
    });

    textarea.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        this.sendCurrentInput();
      }
      // Shift+Enter falls through and inserts a newline naturally.
    });

    sendBtn.addEventListener('click', () => this.sendCurrentInput());

    // Escape closes the window when focus is inside it.
    chatWindow.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        this.closeWindow();
      }
    });
  };

  Chatbot.prototype._renderWelcome = function () {
    const card = Messages.renderWelcomeCard(SUGGESTED_QUESTIONS, (question) => {
      this.refs.textarea.value = question;
      this.refs.textarea.focus();
      Ui.autoResizeTextarea(this.refs.textarea);
      this.refs.sendBtn.disabled = isBlank(this.refs.textarea.value);
    });
    this.refs.messagesEl.appendChild(card);
  };

  Chatbot.prototype.toggleWindow = function () {
    const isOpen = this.refs.chatWindow.classList.contains('is-open');
    if (isOpen) {
      this.closeWindow();
    } else {
      this.openWindow();
    }
  };

  Chatbot.prototype.openWindow = function () {
    Ui.openWindow(this.refs);
    this.hasOpenedBefore = true;
  };

  Chatbot.prototype.closeWindow = function () {
    Ui.closeWindow(this.refs);
  };

  Chatbot.prototype.minimizeWindow = function () {
    Ui.minimizeWindow(this.refs);
  };

  /** Reads the textarea, and if non-empty, sends it as a user message. */
  Chatbot.prototype.sendCurrentInput = function () {
    const { textarea } = this.refs;
    const text = textarea.value.trim();
    if (isBlank(text) || this.isWaitingForReply) return;

    textarea.value = '';
    textarea.style.height = 'auto';
    this.refs.sendBtn.disabled = true;

    this._addMessage(Messages.createMessage({ role: 'user', text }));
    this._requestAssistantReply(text);
  };

  Chatbot.prototype._addMessage = function (message) {
    this.history.push(message);
    const row = Messages.renderMessageRow(message);
    this.refs.messagesEl.appendChild(row);
    scrollToBottom(this.refs.messagesEl, true);
    return row;
  };

  Chatbot.prototype._requestAssistantReply = function (userText) {
    this.isWaitingForReply = true;
    const typingRow = Messages.renderTypingIndicator();
    this.refs.messagesEl.appendChild(typingRow);
    scrollToBottom(this.refs.messagesEl, true);

    Api.sendMessage(userText, this.history)
      .then((reply) => {
        typingRow.remove();
        this._addMessage(Messages.createMessage(reply));
      })
      .catch(() => {
        typingRow.remove();
        this._addMessage(
          Messages.createMessage({
            role: 'assistant',
            text: 'ያንን መልእክት በመላክ ላይ ስህተት ተፈጥሯል። እባክዎ እንደገና ይሞክሩ።',
            isError: true,
          })
        );
      })
      .finally(() => {
        this.isWaitingForReply = false;
      });
  };

  global.POESSAChatbot = Chatbot;
})(window);

