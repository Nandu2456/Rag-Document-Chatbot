import { uploadDocuments } from "../services/api";
import { useState } from "react";

function UploadPanel({ selectedFiles, setSelectedFiles, onNotification }) {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    try {
      setUploading(true);
      onNotification(`Uploading and indexing ${files.length} document(s)...`, "loading");
      await uploadDocuments(files);
      
      const fileNames = files.map(f => f.name);
      setSelectedFiles((prev) => [...prev, ...fileNames]);
      
      onNotification(`${files.length} document(s) uploaded and indexed successfully!`, "success");
    } catch (err) {
      onNotification("Upload failed. Please try again.", "error", err);
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (fileName) => {
    setSelectedFiles((prev) => prev.filter(f => f !== fileName));
  };

  return (
    <div className="upload-panel">
      <input
        type="file"
        multiple
        disabled={uploading}
        accept=".pdf,.docx,.txt,.md"
        onChange={handleUpload}
      />
      {selectedFiles && selectedFiles.length > 0 && (
        <div className="selected-files">
          <p><strong>Uploaded Files ({selectedFiles.length}):</strong></p>
          <ul>
            {selectedFiles.map((file, idx) => (
              <li key={idx}>
                {file}
                <button 
                  onClick={() => removeFile(file)}
                  className="remove-file-btn"
                  title="Remove file"
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default UploadPanel;
