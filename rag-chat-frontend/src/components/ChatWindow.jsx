import { useState, useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

function ChatWindow({ messages, setMessages }) {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef(null);

  // ✅ Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const questionText = input;

    // 1️⃣ Add user message
    setMessages((prev) => [...prev, { role: "user", text: questionText }]);
    setInput("");
    setIsLoading(true);

    // 2️⃣ Add bot placeholder ONCE
    setMessages((prev) => [...prev, { role: "bot", text: "", citations: [] }]);

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: questionText }),
      });

      if (!response.ok || !response.body) {
        throw new Error("Streaming failed");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let botText = "";
      let citations = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        // ✅ Handle SSE OR plain text
        const lines = chunk.split("\n");

        for (let line of lines) {
          line = line.trim();
          if (!line) continue;

          // SSE format
          if (line.startsWith("data:")) {
            const data = line.replace("data:", "").trim();
            if (data === "[DONE]") break;

            try {
              const json = JSON.parse(data);
              if (json.text) {
                botText += json.text;
              } else if (json.citations) {
                citations = json.citations;
              }
            } catch {
              botText += data;
            }
          } else {
            // Plain text fallback
            botText += line;
          }

          // ✅ Update last bot message
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...updated[updated.length - 1],
              text: botText,
              citations: citations,
            };
            return updated;
          });
        }
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "bot",
          text: "❌ Unable to get response. Please try again.",
          citations: [],
        };
        return updated;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} text={m.text} citations={m.citations || []} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask a question..."
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading}>
          {isLoading ? "Streaming..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
