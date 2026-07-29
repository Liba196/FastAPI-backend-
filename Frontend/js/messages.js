/**
 * messages.js
 * Defines the message data model and renders it to DOM. Kept generic
 * enough to support features not wired up yet: streaming, citations,
 * source documents, attachments, error states, loading states.
 */
(function (global) {
  "use strict";

  const { generateId, escapeHTML, formatTime, h } = global.POESSAUtils;

  /**
   * Creates a normalized message object. This is the shape every
   * message in the conversation follows, whether it came from the
   * user, the assistant, or (eventually) the streaming/error paths.
   */
  function createMessage(partial) {
    return Object.assign(
      {
        id: generateId("msg"),
        role: "assistant",
        text: "",
        timestamp: new Date(),
        citations: [],
        sources: [],
        attachments: [],
        isError: false,
        isLoading: false,
        isUngrounded: false, // <-- new
      },
      partial,
    );
  }

  /** Renders a single message object into a `.poessa-row` DOM element. */
  function renderSources(sources) {
    if (!sources || !sources.length) return null;
    const items = sources.map((s) =>
      h("li", { class: "poessa-source-chip" }, [
        h("span", { class: "poessa-source-chip__title" }, [s.title]),
        s.excerpt
          ? h("span", { class: "poessa-source-chip__excerpt" }, [s.excerpt])
          : null,
      ]),
    );
    return h("ul", { class: "poessa-sources", "aria-label": "Sources" }, items);
  }

  function renderMessageRow(message) {
    const isUser = message.role === "user";

    const bubbleClass =
      `poessa-bubble${message.isError ? " poessa-bubble--error" : ""}` +
      `${message.isUngrounded ? " poessa-bubble--ungrounded" : ""}`;

    const bubble = h("div", {
      class: bubbleClass,
      html: escapeHTML(message.text).replace(/\n/g, "<br>"),
    });

    const groupChildren = [bubble];
    const sourcesEl = renderSources(message.sources);
    if (sourcesEl) groupChildren.push(sourcesEl);
    groupChildren.push(
      h("span", { class: "poessa-timestamp" }, [formatTime(message.timestamp)]),
    );

    const group = h("div", { class: "poessa-bubble-group" }, groupChildren);

    const children = isUser
      ? [group]
      : [
          h("div", { class: "poessa-avatar", "aria-hidden": "true" }, ["AI"]),
          group,
        ];

    return h(
      "div",
      {
        class: `poessa-row poessa-row--${isUser ? "user" : "assistant"}`,
        "data-message-id": message.id,
        role: "group",
        "aria-label": `${isUser ? "እርስዎ" : "የፖኤሳ AI ረዳት"} ብለዋል`,
      },
      children,
    );
  }

  /** Renders the animated three-dot typing indicator row. */
  function renderTypingIndicator() {
    const dots = h(
      "div",
      {
        class: "poessa-typing",
        role: "status",
        "aria-label": "የፖኤሳ AI ረዳት በመተየብ ላይ",
      },
      [
        h("span", { class: "poessa-typing__dot" }),
        h("span", { class: "poessa-typing__dot" }),
        h("span", { class: "poessa-typing__dot" }),
      ],
    );

    return h(
      "div",
      {
        class: "poessa-row poessa-row--assistant",
        "data-typing-indicator": "true",
      },
      [
        h("div", { class: "poessa-avatar", "aria-hidden": "true" }, ["AI"]),
        dots,
      ],
    );
  }

  /** Renders the clickable suggested-question chips. */
  function renderSuggestedQuestions(questions, onSelect) {
    const chips = questions.map((question) =>
      h(
        "button",
        {
          type: "button",
          class: "poessa-chip",
          onClick: () => onSelect(question),
        },
        [question],
      ),
    );
    return h(
      "div",
      {
        class: "poessa-suggestions",
        role: "group",
        "aria-label": "የተጠቆሙ ጥያቄዎች",
      },
      chips,
    );
  }

  /** Renders the initial welcome card (greeting + suggestions). */
  function renderWelcomeCard(questions, onSelectQuestion) {
    const greeting = h("p", { class: "poessa-welcome__greeting" }, []);
    greeting.innerHTML =
      "ሰላም! እኔ <strong>የርስዎ AI ረዳት</strong> ነኝ።<br><br>" +
      "ስለ ማህበራዊ ዋስትና አገልግሎቶች፣ አሰራሮች፣ ደንቦች እና ሰነዶች ጥያቄዎችን መጠየቅ ይችላሉ።";

    const notice = h("p", { class: "poessa-welcome__notice" }, [
      "ለመጀመር ጥያቄዎን እዚህ ጋር ይጻፉ።",
    ]);

    return h("div", { class: "poessa-welcome" }, [
      greeting,
      notice,
      renderSuggestedQuestions(questions, onSelectQuestion),
    ]);
  }

  global.POESSAMessages = {
    createMessage,
    renderMessageRow,
    renderTypingIndicator,
    renderSuggestedQuestions,
    renderWelcomeCard,
  };
})(window);
