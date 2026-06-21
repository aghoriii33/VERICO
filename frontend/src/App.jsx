import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import HomePage from './pages/HomePage';
import ChatPanel from './components/ChatPanel';
import AnalyticsPage from './pages/AnalyticsPage';
import { api } from './api/client';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDocs = async () => {
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (e) {
      console.error("Failed to load documents list", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    api.getDocuments()
      .then(data => {
        if (active) {
          setDocuments(data);
          setIsLoading(false);
        }
      })
      .catch(e => {
        console.error("Failed to load documents list", e);
        if (active) {
          setIsLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  const renderActiveView = () => {
    switch (currentTab) {
      case 'dashboard':
        return (
          <HomePage 
            documents={documents} 
            fetchDocs={fetchDocs} 
          />
        );
      case 'chat':
        return <ChatPanel documents={documents} />;
      case 'analytics':
        return <AnalyticsPage documents={documents} />;
      default:
        return (
          <HomePage 
            documents={documents} 
            fetchDocs={fetchDocs} 
          />
        );
    }
  };

  return (
    <div className="app-container">
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />
      <main className="main-content">
        {isLoading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%',
            color: 'var(--text-muted)'
          }}>
            <div className="typing-indicator">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </div>
        ) : (
          renderActiveView()
        )}
      </main>
    </div>
  );
}
