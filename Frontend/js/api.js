(function (global) {
  'use strict';

  const API_BASE_URL = 'http://127.0.0.1:8000';
  const CHAT_ENDPOINT = `${API_BASE_URL}/api/v1/chat`;

  // Persisted for the life of the page so follow-up questions carry the
  // same session_id. The backend doesn't use this for real conversation
  // memory yet — that's a tracked, deferred piece (Phase 7's
  // chat_sessions/chat_messages) — but wiring the plumbing now means
  // nothing here needs to change once it does.
  let currentSessionId = null;

  function mapCitationsToSources(citations) {
    return (citations || []).map((c) => ({
      title: c.document_title,
      excerpt: c.page_number ? `ገጽ ${c.page_number}` : null, // "Page N"
    }));
  }

  function sendMessage(userText, history) {
    return fetch(CHAT_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: currentSessionId,
        message: userText,
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`API returned ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        currentSessionId = data.session_id;
        return {
          role: 'assistant',
          text: data.answer,
          citations: [],
          sources: mapCitationsToSources(data.citations),
          attachments: [],
          isError: false,
          isUngrounded: !data.grounded,
        };
      });
    // Network/parsing errors deliberately propagate — chatbot.js
    // already has a .catch() that shows a friendly Amharic error bubble.
  }

  function streamMessage(userText, history, onChunk) {
    return sendMessage(userText, history).then((full) => {
      if (typeof onChunk === 'function') onChunk(full.text);
      return full;
    });
  }

  global.POESSAApi = { sendMessage, streamMessage };
})(window);