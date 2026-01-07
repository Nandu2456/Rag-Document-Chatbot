import { useState } from "react";
import UploadPanel from "./components/UploadPanel";
import ChatWindow from "./components/ChatWindow";
import Controls from "./components/Controls";
import Notification from "./components/Notification";

function App() {
  const [messages, setMessages] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [notification, setNotification] = useState(null);

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleClearFiles = () => {
    setSelectedFiles([]);
  };

  const showNotification = (message, type = "success") => {
    setNotification({ message, type });
  };

  const hideNotification = () => {
    setNotification(null);
  };

  return (
    <div className="app">
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={hideNotification}
        />
      )}
      <h2>📄 Document Q&A Assistant</h2>
      <UploadPanel
        selectedFiles={selectedFiles}
        setSelectedFiles={setSelectedFiles}
        onNotification={showNotification}
      />
      <Controls
        onClearChat={handleClearChat}
        onClearFiles={handleClearFiles}
        onNotification={showNotification}
      />

      <ChatWindow messages={messages} setMessages={setMessages} />
    </div>
  );
}

export default App;
