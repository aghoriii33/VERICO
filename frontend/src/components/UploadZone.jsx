import React, { useState, useRef } from 'react';
import { UploadCloud } from 'lucide-react';

export default function UploadZone({ onUpload, isUploading }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (isUploading) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onUpload(files);
    }
  };

  const handleFileChange = (e) => {
    if (isUploading) return;
    
    const files = e.target.files;
    if (files.length > 0) {
      onUpload(files);
    }
  };

  const handleClick = () => {
    if (isUploading) return;
    fileInputRef.current.click();
  };

  return (
    <div
      className={`upload-zone glass-panel ${isDragging ? 'dragging' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        accept=".pdf"
        style={{ display: 'none' }}
      />
      <UploadCloud className="upload-icon" />
      <h3 className="upload-title">
        {isUploading ? 'Compliance scanning in progress...' : 'Upload Compliance Documents'}
      </h3>
      <p className="upload-desc">
        {isUploading 
          ? 'Extracting text and running Rule+ML risk checks...' 
          : 'Drag & drop multiple PDFs or click to browse'}
      </p>
    </div>
  );
}
