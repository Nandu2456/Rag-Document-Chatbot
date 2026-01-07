import { useState } from "react";
import UploadPanel from "./components/UploadPanel";
import ChatWindow from "./components/ChatWindow";
import Controls from "./components/Controls";
import Notification from "./components/Notification";

function App() {
  const [messages, setMessages] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [notification, setNotification] = useState(null);

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleClearFile = () => {
    setSelectedFile(null);
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
        selectedFile={selectedFile}
        setSelectedFile={setSelectedFile}
        onNotification={showNotification}
      />
      <Controls
  onClearChat={handleClearChat}
  onClearFile={handleClearFile}
  onNotification={() =>
    showNotification("Document uploaded and indexed successfully!", "success")
  }
/>

      <ChatWindow messages={messages} setMessages={setMessages} />
    </div>
  );
}

export default App;
