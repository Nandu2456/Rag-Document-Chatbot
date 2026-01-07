import { clearChat, resetKnowledge } from "../services/api";

function Controls({ onClearChat, onClearFile }) {
  const handleClearChat = async () => {
    try {
      await clearChat();
      onClearChat();
    } catch (error) {
      console.error("Error clearing chat:", error);
      alert("Failed to clear chat. Please try again.");
    }
  };

  const handleResetKnowledge = async () => {
    
    
    try {
      const response = await resetKnowledge();
      // Clear chat and selected file when knowledge base is reset
      onClearChat();
      if (onClearFile) {
        onClearFile();
      }
      
      alert(response.data.message || "Knowledge base reset successfully. All documents have been removed.");
    } catch (error) {
      console.error("Error resetting knowledge base:", error);
      alert("Failed to reset knowledge base. Please try again.");
    }
  };

  return (
    <div className="controls">
      <button onClick={handleClearChat}>Clear Chat</button>
      <button onClick={handleResetKnowledge}>Reset Knowledge Base</button>
    </div>
  );
}

export default Controls;
