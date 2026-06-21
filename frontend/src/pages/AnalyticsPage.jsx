import { useState, useEffect } from 'react';
import { ShieldAlert, AlertOctagon, Files, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';

export default function AnalyticsPage({ documents }) {
  const [allRisks, setAllRisks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.resolve().then(() => {
      if (active) setIsLoading(true);
    });
    api.getAllRisks()
      .then(risks => {
        if (active) {
          setAllRisks(risks);
          setIsLoading(false);
        }
      })
      .catch(e => {
        console.error("Failed to load risks", e);
        if (active) {
          setIsLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [documents]);

  // 1. Calculate metrics
  const totalDocs = documents.length;
  const highRisks = allRisks.filter(r => r.severity === 'High').length;
  const mediumRisks = allRisks.filter(r => r.severity === 'Medium').length;
  const compliantDocs = documents.filter(d => d.total_risks === 0).length;

  // 2. Risk breakdown by Document Type
  const docTypeRisks = { 'HR Policy': 0, 'Vendor Contract': 0, 'Security SOP': 0, 'General': 0 };
  allRisks.forEach(r => {
    const type = r.document_type || 'General';
    docTypeRisks[type] = (docTypeRisks[type] || 0) + 1;
  });

  const maxDocTypeRisks = Math.max(...Object.values(docTypeRisks), 1);

  // 3. Risk breakdown by Category (Liability, Term, Compliance, etc.)
  const categoryRisks = {};
  allRisks.forEach(r => {
    const cat = r.category || 'Other';
    categoryRisks[cat] = (categoryRisks[cat] || 0) + 1;
  });
  const maxCategoryRisks = Math.max(...Object.values(categoryRisks), 1);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Compliance Analytics</h2>
          <p className="page-subtitle">Visual overview of compliance risk exposure across all registered files.</p>
        </div>
      </div>

      {/* Analytics Summary Stats Grid */}
      <div className="analytics-grid">
        <div className="metric-card glass-panel">
          <div className="metric-icon-box" style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)' }}>
            <Files size={22} />
          </div>
          <div className="metric-details">
            <h3>{totalDocs}</h3>
            <p>Documents Indexed</p>
          </div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-icon-box" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--risk-high)' }}>
            <ShieldAlert size={22} />
          </div>
          <div className="metric-details">
            <h3>{highRisks}</h3>
            <p>High Severity Risks</p>
          </div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-icon-box" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--risk-medium)' }}>
            <AlertOctagon size={22} />
          </div>
          <div className="metric-details">
            <h3>{mediumRisks}</h3>
            <p>Medium Severity Risks</p>
          </div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-icon-box" style={{ background: 'rgba(34, 197, 94, 0.1)', color: 'var(--risk-low)' }}>
            <CheckCircle2 size={22} />
          </div>
          <div className="metric-details">
            <h3>{compliantDocs}</h3>
            <p>Compliant Files</p>
          </div>
        </div>
      </div>

      {/* Visual Charts Section */}
      <div className="charts-section">
        {/* Chart 1: Risks by Document Type */}
        <div className="chart-card glass-panel">
          <h3 className="chart-title">Risk Exposure by File Type</h3>
          <div className="bar-chart-container">
            {Object.entries(docTypeRisks).map(([type, count]) => {
              const pct = (count / maxDocTypeRisks) * 100;
              let barColor = 'var(--primary)';
              if (type === 'Vendor Contract') barColor = 'var(--accent)';
              if (type === 'Security SOP') barColor = 'var(--secondary)';
              
              return (
                <div key={type} className="bar-chart-row">
                  <span className="bar-label">{type}</span>
                  <div className="bar-track">
                    <div 
                      className="bar-fill" 
                      style={{ 
                        width: `${pct}%`,
                        background: `linear-gradient(90deg, ${barColor}, #a5b4fc)` 
                      }} 
                    />
                  </div>
                  <span className="bar-value">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Chart 2: Risks by Compliance Category */}
        <div className="chart-card glass-panel">
          <h3 className="chart-title">Risks by Compliance Category</h3>
          <div className="bar-chart-container">
            {Object.keys(categoryRisks).length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem 0' }}>
                No risks detected to categorize.
              </div>
            ) : (
              Object.entries(categoryRisks).map(([cat, count]) => {
                const pct = (count / maxCategoryRisks) * 100;
                let barColor = 'var(--risk-high)';
                if (cat === 'Term') barColor = 'var(--risk-medium)';
                if (cat === 'Compliance') barColor = 'var(--info)';

                return (
                  <div key={cat} className="bar-chart-row">
                    <span className="bar-label">{cat}</span>
                    <div className="bar-track">
                      <div 
                        className="bar-fill" 
                        style={{ 
                          width: `${pct}%`,
                          background: `linear-gradient(90deg, ${barColor}, #a5b4fc)` 
                        }} 
                      />
                    </div>
                    <span className="bar-value">{count}</span>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Global Risk feed Table */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <h3 style={{ marginBottom: '1.25rem', color: 'white' }}>Compliance Risk Registry Feed</h3>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-muted)' }}>
            <div className="typing-indicator" style={{ justifyContent: 'center' }}>
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </div>
        ) : allRisks.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center', padding: '2rem 0' }}>
            No risks detected across any indexed files.
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="analytics-risks-table">
              <thead>
                <tr>
                  <th>Document Name</th>
                  <th>Category</th>
                  <th>Severity</th>
                  <th>Source</th>
                  <th>Page</th>
                  <th>Flagged Clause</th>
                </tr>
              </thead>
              <tbody>
                {allRisks.map((risk) => (
                  <tr key={risk.id}>
                    <td style={{ fontWeight: 500, color: 'white' }}>{risk.document_name}</td>
                    <td>{risk.category}</td>
                    <td>
                      <span className={`risk-pill ${risk.severity.toLowerCase()}`}>
                        {risk.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`risk-source-pill ${risk.source === 'ML' ? 'ml' : ''}`}>
                        {risk.source}
                      </span>
                    </td>
                    <td>{risk.page_number}</td>
                    <td 
                      style={{ 
                        maxWidth: '300px', 
                        whiteSpace: 'nowrap', 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis',
                        fontStyle: 'italic',
                        color: 'var(--text-secondary)'
                      }}
                      title={risk.clause_text}
                    >
                      "{risk.clause_text}"
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
