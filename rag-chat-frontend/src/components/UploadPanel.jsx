import { uploadDocument } from "../services/api";

function UploadPanel({ selectedFile, setSelectedFile, onNotification }) {
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      onNotification("Uploading and indexing document...", "loading");
      await uploadDocument(file);
      setSelectedFile(file.name);
      onNotification("Document uploaded and indexed successfully!", "success");
    } catch (err) {
      onNotification("Upload failed. Please try again.", "error",err);
    }
  };

  return (
    <div className="upload-panel">
      <input
        type="file"
        accept=".pdf,.docx,.txt,.md"
        onChange={handleUpload}
      />
      {selectedFile && <p>Selected: {selectedFile}</p>}
    </div>
  );
}

export default UploadPanel;
