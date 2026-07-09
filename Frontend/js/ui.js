/**
 * ui.js
 * Builds the widget's DOM (ChatButton, ChatWindow, ChatHeader, ChatInput)
 * and exposes small render/animation helpers. Does not own conversation
 * state or business logic — that lives in chatbot.js.
 */
(function (global) {
  'use strict';

  const { h } = global.POESSAUtils;

  const ICONS = {
    chat:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>',
    close:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    minimize:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    send:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
  };

  /**
   * Builds the full widget DOM tree and appends it into `rootEl`.
   * Returns references to the key nodes chatbot.js needs to wire up.
   */
  function buildWidget(rootEl) {
    // ---- ChatButton ----
    const launcherIconChat = h('span', { class: 'poessa-launcher__icon poessa-launcher__icon--chat', html: ICONS.chat });
    const launcherIconClose = h('span', { class: 'poessa-launcher__icon poessa-launcher__icon--close', html: ICONS.close });
    const launcher = h(
      'button',
      {
        type: 'button',
        class: 'poessa-launcher',
        'aria-label': 'የፖኤሳ AI ረዳት ውይይት ይክፈቱ',
        'aria-expanded': 'false',
        'aria-controls': 'poessa-chat-window',
      },
      [launcherIconChat, launcherIconClose, h('span', { class: 'poessa-launcher__badge', 'aria-hidden': 'true' })]
    );

    // ---- ChatHeader ----
    const minimizeBtn = h(
      'button',
      { type: 'button', class: 'poessa-header__btn', 'aria-label': 'ውይይት ያሳንሱ', html: ICONS.minimize }
    );
    const closeBtn = h(
      'button',
      { type: 'button', class: 'poessa-header__btn', 'aria-label': 'ውይይት ዝጋ', html: ICONS.close }
    );

    const header = h(
      'div',
      { class: 'poessa-header' },
      [
        h('img', { class: 'poessa-header__logo', src: 'logo.png', alt: 'POESSA Logo', 'aria-hidden': 'true' }),
        h('div', { class: 'poessa-header__text' }, [
          h('p', { class: 'poessa-header__title' }, ['የ AI ረዳት']),
          h('p', { class: 'poessa-header__subtitle' }, ['ስለ ማህበራዊ ዋስትና አገልግሎቶች ይጠይቁ።']),
        ]),
        h('div', { class: 'poessa-header__actions' }, [minimizeBtn, closeBtn]),
      ]
    );

    // ---- ChatMessages ----
    const messagesEl = h('div', {
      class: 'poessa-messages',
      id: 'poessa-messages',
      role: 'log',
      'aria-live': 'polite',
      'aria-label': 'ውይይት',
    });

    // ---- ChatInput ----
    const textarea = h('textarea', {
      class: 'poessa-input',
      id: 'poessa-chat-input',
      placeholder: 'ጥያቄ ይጠይቁ...',
      rows: '1',
      'aria-label': 'መልእክት',
    });
    const sendBtn = h(
      'button',
      {
        type: 'button',
        class: 'poessa-send',
        'aria-label': 'መልእክት ላክ',
        disabled: 'true',
        html: ICONS.send,
      }
    );
    const inputBar = h('div', { class: 'poessa-input-bar' }, [textarea, sendBtn]);
    const footnote = h('p', { class: 'poessa-footnote' }, [
      'Responses are for general guidance only and are not final legal determinations.',
    ]);

    // ---- ChatWindow ----
    const chatWindow = h(
      'div',
      {
        class: 'poessa-window',
        id: 'poessa-chat-window',
        role: 'dialog',
        'aria-modal': 'false',
        'aria-label': 'የፖኤሳ AI ረዳት ውይይት መስኮት',
      },
      [header, messagesEl, inputBar, footnote]
    );

    // ---- ChatWidget (root) ----
    const widget = h('div', { class: 'poessa-widget' }, [chatWindow, launcher]);
    rootEl.appendChild(widget);

    return {
      widget,
      launcher,
      chatWindow,
      minimizeBtn,
      closeBtn,
      messagesEl,
      textarea,
      sendBtn,
    };
  }

  /** Opens the chat window with its transition and focuses the input. */
  function openWindow(refs) {
    refs.chatWindow.classList.remove('is-minimized');
    // Force layout so the transition reliably runs even right after unhiding.
    void refs.chatWindow.offsetHeight;
    refs.chatWindow.classList.add('is-open');
    refs.launcher.classList.add('is-open');
    refs.launcher.setAttribute('aria-expanded', 'true');
    refs.launcher.setAttribute('aria-label', 'የፖኤሳ AI ረዳት ውይይት ይዝጉ');
    window.setTimeout(() => refs.textarea.focus(), 220);
  }

  /** Fully closes the chat window. */
  function closeWindow(refs) {
    refs.chatWindow.classList.remove('is-open');
    refs.chatWindow.classList.remove('is-minimized');
    refs.launcher.classList.remove('is-open');
    refs.launcher.setAttribute('aria-expanded', 'false');
    refs.launcher.setAttribute('aria-label', 'የፖኤሳ AI ረዳት ውይይት ይክፈቱ');
    refs.launcher.focus();
  }

  /** Minimizes (hides without resetting conversation) the chat window. */
  function minimizeWindow(refs) {
    refs.chatWindow.classList.remove('is-open');
    refs.launcher.classList.remove('is-open');
    refs.launcher.setAttribute('aria-expanded', 'false');
    refs.launcher.setAttribute('aria-label', 'የፖኤሳ AI ረዳት ውይይት ይክፈቱ');
    window.setTimeout(() => {
      if (!refs.chatWindow.classList.contains('is-open')) {
        refs.chatWindow.classList.add('is-minimized');
      }
    }, 240);
    refs.launcher.focus();
  }

  /** Auto-grows the textarea up to the CSS max-height as the user types. */
  function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  global.POESSAUi = {
    buildWidget,
    openWindow,
    closeWindow,
    minimizeWindow,
    autoResizeTextarea,
  };
})(window);
