/**
 * api.js
 * All backend communication is isolated here. Right now every function
 * returns mocked, locally-resolved data. When the RAG backend is ready,
 * only the bodies of these functions need to change — callers in
 * chatbot.js should not need to change at all.
 */
(function (global) {
  'use strict';

  const MOCK_RESPONSE_DELAY_MS = 1000;

  const MOCK_REPLY =
    "ለመልእክትዎ እናመሰግናለን።\n\n" +
    "የ AI ስርዓት በአሁኑ ጊዜ በመገንባት ላይ ነው። " +
    "እባክዎን በትእግስት ይጠብቁን።";

  /**
   * Sends a user message to the assistant and resolves with a response
   * message object once ready. Mirrors the shape a real backend call
   * will eventually return (see messages.js for the full message model),
   * including placeholders for fields not used yet.
   *
   * @param {string} userText - the message the user sent
   * @param {Array}  history  - prior message objects, for future context use
   * @returns {Promise<Object>} resolves with an assistant message payload
   */
  function sendMessage(userText, history) {
    // NOTE: swap this Promise body for a real fetch() to the RAG backend, e.g.:
    //
    // return fetch('/api/chat', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ message: userText, history })
    // }).then((res) => res.json());

    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          role: 'assistant',
          text: MOCK_REPLY,
          citations: [],       // future: [{ label, url }]
          sources: [],         // future: [{ title, documentId, excerpt }]
          attachments: [],     // future: [{ type, url, name }]
          isError: false,
        });
      }, MOCK_RESPONSE_DELAY_MS);
    });
  }

  /**
   * Placeholder for future streaming support. Not used yet — kept here
   * so chatbot.js can be wired to it later without restructuring.
   */
  function streamMessage(userText, history, onChunk) {
    return sendMessage(userText, history).then((full) => {
      if (typeof onChunk === 'function') onChunk(full.text);
      return full;
    });
  }

  global.POESSAApi = {
    sendMessage,
    streamMessage,
  };
})(window);
