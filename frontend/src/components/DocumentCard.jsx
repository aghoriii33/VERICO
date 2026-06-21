import React from 'react';
import { FileText, Trash2, Calendar, File } from 'lucide-react';

export default function DocumentCard({ doc, isSelected, onSelect, onDelete }) {
  const getDocTypeBadge = (type) => {
    switch (type) {
      case 'HR Policy':
        return <span className="tag-badge tag-hr">HR Policy</span>;
      case 'Vendor Contract':
        return <span className="tag-badge tag-vendor">Contract</span>;
      case 'Security SOP':
        return <span className="tag-badge tag-security">Security SOP</span>;
      default:
        return <span className="tag-badge">General</span>;
    }
  };

  const getFormattedDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (e) {
      return dateStr;
    }
  };

  const handleDelete = (e) => {
    e.stopPropagation(); // Avoid card selection trigger
    if (window.confirm(`Are you sure you want to delete ${doc.filename}?`)) {
      onDelete(doc.id);
    }
  };

  return (
    <div
      className={`doc-card glass-panel glass-panel-glow ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(doc)}
    >
      <div className="doc-icon-wrapper">
        <FileText size={20} />
      </div>

      <div className="doc-details">
        <h4 className="doc-name">{doc.filename}</h4>
        <div className="doc-meta">
          {getDocTypeBadge(doc.doc_type)}
          <div className="doc-meta-item">
            <Calendar size={12} />
            <span>{getFormattedDate(doc.upload_date)}</span>
          </div>
          <div className="doc-meta-item">
            <File size={12} />
            <span>{doc.page_count} {doc.page_count === 1 ? 'page' : 'pages'}</span>
          </div>
        </div>
      </div>

      <div className="doc-status-badge">
        {doc.status === 'indexed' ? (
          <div className="risk-count-strip">
            {doc.risks_summary?.High > 0 && (
              <span className="risk-pill high">{doc.risks_summary.High} H</span>
            )}
            {doc.risks_summary?.Medium > 0 && (
              <span className="risk-pill medium">{doc.risks_summary.Medium} M</span>
            )}
            {doc.risks_summary?.Low > 0 && (
              <span className="risk-pill low">{doc.risks_summary.Low} L</span>
            )}
            {doc.total_risks === 0 && (
              <span className="risk-pill low">Compliant</span>
            )}
          </div>
        ) : (
          <div className="status-dot-wrapper">
            <div className={`status-dot ${doc.status}`} />
          </div>
        )}
      </div>

      <button className="delete-btn" onClick={handleDelete} title="Delete document">
        <Trash2 size={16} />
      </button>
    </div>
  );
}
