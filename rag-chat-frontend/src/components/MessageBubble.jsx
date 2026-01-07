function MessageBubble({ role, text, citations = [] }) {
  return (
    <div className={`bubble ${role}`}>
      <p style={{ whiteSpace: "pre-wrap" }}>{text}</p>
      {citations && citations.length > 0 && role === "bot" && (
        <div className="citations">
          <strong>Sources:</strong>
          <ul>
            {citations.map((citation, idx) => (
              <li key={idx}>{citation.source}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default MessageBubble;
