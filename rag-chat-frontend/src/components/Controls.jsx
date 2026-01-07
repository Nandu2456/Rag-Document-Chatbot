import { clearChat, resetKnowledge } from "../services/api";

function Controls({ onClearChat, onClearFiles, onNotification }) {
  const handleClearChat = async () => {
    try {
      await clearChat();
      onClearChat();
      if (onNotification) {
        onNotification("Chat cleared successfully!", "success");
      }
    } catch (error) {
      console.error("Error clearing chat:", error);
      if (onNotification) {
        onNotification("Failed to clear chat. Please try again.", "error");
      }
    }
  };

  const handleResetKnowledge = async () => {
    try {
      const response = await resetKnowledge();
      // Clear chat and selected files when knowledge base is reset
      onClearChat();
      if (onClearFiles) {
        onClearFiles();
      }
      
      if (onNotification) {
        onNotification(response.data.message || "Knowledge base reset successfully. All documents have been removed.", "success");
      }
    } catch (error) {
      console.error("Error resetting knowledge base:", error);
      if (onNotification) {
        onNotification("Failed to reset knowledge base. Please try again.", "error");
      }
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
