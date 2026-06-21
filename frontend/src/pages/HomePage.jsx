import React, { useState, useEffect } from 'react';
import { ShieldAlert, Info, AlertTriangle, CheckCircle, FileText } from 'lucide-react';
import UploadZone from '../components/UploadZone';
import DocumentCard from '../components/DocumentCard';
import { api } from '../api/client';

export default function HomePage({ documents, setDocuments, fetchDocs }) {
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [selectedDocDetails, setSelectedDocDetails] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);

  // Auto-refresh details when selected doc changes or is updated
  useEffect(() => {
    if (selectedDoc) {
      loadDocDetails(selectedDoc.id);
    } else {
      setSelectedDocDetails(null);
    }
  }, [selectedDoc]);

  const loadDocDetails = async (id) => {
    setIsLoadingDetails(true);
    try {
      const details = await api.getDocumentDetails(id);
      setSelectedDocDetails(details);
    } catch (e) {
      console.error("Failed to load document details", e);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const handleUpload = async (files) => {
    setIsUploading(true);
    try {
      await api.uploadDocuments(files);
      await fetchDocs();
    } catch (e) {
      alert("Error uploading documents: " + e.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteDocument(id);
      if (selectedDoc?.id === id) {
        setSelectedDoc(null);
      }
      await fetchDocs();
    } catch (e) {
      alert("Error deleting document: " + e.message);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'High':
        return <ShieldAlert size={16} color="var(--risk-high)" />;
      case 'Medium':
        return <AlertTriangle size={16} color="var(--risk-medium)" />;
      default:
        return <Info size={16} color="var(--risk-low)" />;
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Compliance Registry</h2>
          <p className="page-subtitle">Scan and audit organization policies, vendor contracts, and security SOPs.</p>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Left Column: Upload and Document List */}
        <div className="upload-section">
          <UploadZone onUpload={handleUpload} isUploading={isUploading} />

          <div className="doc-list-header">
            <h3>Indexed Documents ({documents.length})</h3>
          </div>

          <div className="doc-grid">
            {documents.length === 0 ? (
              <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <FileText size={40} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                <p>No documents registered. Upload a PDF file to begin analysis.</p>
              </div>
            ) : (
              documents.map(doc => (
                <DocumentCard
                  key={doc.id}
                  doc={doc}
                  isSelected={selectedDoc?.id === doc.id}
                  onSelect={setSelectedDoc}
                  onDelete={handleDelete}
                />
              ))
            )}
          </div>
        </div>

        {/* Right Column: Active Document Risk Inspector */}
        <div className="inspector-panel glass-panel">
          <div className="inspector-header">
            <h3 className="inspector-title">Compliance Inspector</h3>
            <p className="inspector-desc">
              {selectedDoc 
                ? `Audit details for ${selectedDoc.filename}` 
                : 'Select an indexed document to audit its risk factors.'}
            </p>
          </div>

          <div className="inspector-content">
            {!selectedDoc ? (
              <div style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'var(--text-muted)' }}>
                <ShieldAlert size={44} style={{ marginBottom: '1rem', opacity: 0.3 }} />
                <p style={{ fontSize: '0.9rem' }}>No document selected.</p>
                <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
                  Click on any document in the registry list on the left to inspect detailed clause alerts.
                </p>
              </div>
            ) : isLoadingDetails ? (
              <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)' }}>
                <div className="typing-indicator" style={{ justifyContent: 'center' }}>
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
                <p style={{ fontSize: '0.85rem', marginTop: '0.75rem' }}>Loading compliance scans...</p>
              </div>
            ) : selectedDocDetails?.risks && selectedDocDetails.risks.length > 0 ? (
              selectedDocDetails.risks.map((risk) => (
                <div 
                  key={risk.id} 
                  className={`risk-clause-card ${risk.severity.toLowerCase()}`}
                >
                  <div className="risk-card-meta">
                    <span className="risk-name-badge">
                      {risk.category} Alert (Page {risk.page_number})
                    </span>
                    <span className={`risk-source-pill ${risk.source === 'ML' ? 'ml' : ''}`}>
                      {risk.source} Match {risk.confidence < 1.0 ? `(${Math.round(risk.confidence * 100)}%)` : ''}
                    </span>
                  </div>
                  
                  <p className="risk-clause-text">{risk.clause_text}</p>
                  
                  <div className="risk-footer">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      {getSeverityIcon(risk.severity)}
                      <span style={{ fontWeight: 600, color: `var(--risk-${risk.severity.toLowerCase()})` }}>
                        {risk.severity} Severity
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'var(--text-muted)' }}>
                <CheckCircle size={44} color="var(--risk-low)" style={{ marginBottom: '1rem', opacity: 0.6 }} />
                <p style={{ color: 'white', fontWeight: 500, fontSize: '0.95rem' }}>Document Compliant</p>
                <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
                  No high-risk clauses or compliance issues were detected in this document.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
