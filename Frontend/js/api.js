(function (global) {
  "use strict";

  // Reads the backend URL from the widget root's data attribute, so any
  // site embedding this widget can point it at their own deployment
  // without touching JS at all — just one HTML attribute.
  //   <div id="poessa-chat-widget-root" data-api-base-url="https://..."></div>
  // Falls back to POESSA's own production backend if the attribute is
  // missing, so existing embeds (and this demo page) keep working
  // unchanged.
  const DEFAULT_API_BASE_URL = "https://fastapi-backend-97x8.onrender.com";

  function resolveApiBaseUrl() {
    const root = document.getElementById("poessa-chat-widget-root");
    const configured = root && root.getAttribute("data-api-base-url");
    return (configured && configured.trim()) || DEFAULT_API_BASE_URL;
  }

  const API_BASE_URL = resolveApiBaseUrl();
  const CHAT_ENDPOINT = `${API_BASE_URL}/api/v1/chat`;

  let currentSessionId = null;

  function mapCitationsToSources(citations) {
    return (citations || []).map((c) => ({
      title: c.document_title,
      excerpt: c.page_number ? `ገጽ ${c.page_number}` : null,
    }));
  }

  function sendMessage(userText, history) {
    return fetch(CHAT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
          role: "assistant",
          text: data.answer,
          citations: [],
          sources: mapCitationsToSources(data.citations),
          attachments: [],
          isError: false,
          isUngrounded: !data.grounded,
        };
      });
  }

  function streamMessage(userText, history, onChunk) {
    return sendMessage(userText, history).then((full) => {
      if (typeof onChunk === "function") onChunk(full.text);
      return full;
    });
  }

  global.POESSAApi = { sendMessage, streamMessage };
})(window);