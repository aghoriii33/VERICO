import React, { useState, useEffect, useRef } from 'react';
import { Send, FileText, CheckSquare, Square, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../api/client';

export default function ChatPanel({ documents }) {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'Hello! I am VERICO, your compliance intelligence assistant. Select documents on the left and ask me any questions about policies, contracts, or security procedures.',
    }
  ]);
  const [query, setQuery] = useState('');
  const [selectedDocIds, setSelectedDocIds] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedCitationIndex, setExpandedCitationIndex] = useState(null);
  const chatEndRef = useRef(null);

  // Initialize selected docs when list changes
  useEffect(() => {
    if (documents.length > 0 && selectedDocIds.length === 0) {
      setSelectedDocIds(documents.map(d => d.id));
    }
  }, [documents]);

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const toggleDocSelection = (id) => {
    setSelectedDocIds(prev => 
      prev.includes(id) ? prev.filter(docId => docId !== id) : [...prev, id]
    );
  };

  const handleSend = async (textToSend) => {
    const question = textToSend || query;
    if (!question.trim() || isLoading) return;

    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text: question }]);
    if (!textToSend) setQuery('');
    
    setIsLoading(true);
    try {
      const res = await api.askQuestion(question, selectedDocIds);
      
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: res.answer,
        score: res.score,
        document_name: res.document_name,
        page_number: res.page_number,
        context: res.context,
        start: res.start,
        end: res.end
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: 'Sorry, I encountered an error searching for that answer. Please try again.',
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const toggleCitationExpand = (idx) => {
    setExpandedCitationIndex(prev => prev === idx ? null : idx);
  };

  const getHighlightedContext = (context, start, end) => {
    if (!context) return null;
    const part1 = context.substring(0, start);
    const part2 = context.substring(start, end);
    const part3 = context.substring(end);
    return (
      <>
        <span>... {part1}</span>
        <span className="context-highlight">{part2}</span>
        <span>{part3} ...</span>
      </>
    );
  };

  const suggestedQuestions = [
    "What is the liability cap in Acme Software contract?",
    "Does the WFH policy breach employee privacy?",
    "What are the password complexity requirements?",
  ];

  return (
    <div className="chat-container">
      {/* Left Sub-panel: Multi-document filter */}
      <div className="chat-doc-selector glass-panel" style={{ padding: '1.25rem' }}>
        <h4 className="chat-doc-header">Search Context</h4>
        <div style={{ display: 'flex', gap: '0.5rem', margin: '0.75rem 0', justifyContent: 'flex-start' }}>
          <button 
            onClick={() => setSelectedDocIds(documents.map(d => d.id))}
            style={{ 
              background: 'rgba(255, 255, 255, 0.04)', 
              border: '1px solid var(--border-light)', 
              borderRadius: '6px', 
              color: 'var(--text-secondary)', 
              fontSize: '0.75rem', 
              padding: '0.25rem 0.5rem', 
              cursor: 'pointer',
              transition: 'var(--transition-smooth)'
            }}
            onMouseOver={(e) => e.target.style.borderColor = 'var(--primary)'}
            onMouseOut={(e) => e.target.style.borderColor = 'var(--border-light)'}
          >
            Select All
          </button>
          <button 
            onClick={() => setSelectedDocIds([])}
            style={{ 
              background: 'rgba(255, 255, 255, 0.04)', 
              border: '1px solid var(--border-light)', 
              borderRadius: '6px', 
              color: 'var(--text-secondary)', 
              fontSize: '0.75rem', 
              padding: '0.25rem 0.5rem', 
              cursor: 'pointer',
              transition: 'var(--transition-smooth)'
            }}
            onMouseOver={(e) => e.target.style.borderColor = 'var(--primary)'}
            onMouseOut={(e) => e.target.style.borderColor = 'var(--border-light)'}
          >
            Clear All
          </button>
        </div>
        <div className="chat-doc-list">
          {documents.length === 0 ? (
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No documents uploaded.</p>
          ) : (
            documents.map(doc => {
              const isSelected = selectedDocIds.includes(doc.id);
              return (
                <div
                  key={doc.id}
                  className={`chat-doc-item ${isSelected ? 'selected' : ''}`}
                  onClick={() => toggleDocSelection(doc.id)}
                >
                  {isSelected ? (
                    <CheckSquare size={16} color="var(--primary)" />
                  ) : (
                    <Square size={16} color="var(--text-muted)" />
                  )}
                  <span style={{
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    maxWidth: '180px'
                  }}>
                    {doc.filename}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Right Sub-panel: Chat interface */}
      <div className="chat-main">
        <div className="chat-history">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.sender === 'user' ? 'user' : 'assistant'}`}>
              <div className="chat-bubble">
                <p>{msg.text}</p>
                
                {/* Citation details */}
                {msg.document_name && (
                  <>
                    <div className="chat-bubble-citation">
                      <span>Found in:</span>
                      <span 
                        className="citation-tag"
                        onClick={() => toggleCitationExpand(idx)}
                      >
                        {msg.document_name} (Page {msg.page_number})
                        {expandedCitationIndex === idx ? (
                          <ChevronUp size={12} style={{ marginLeft: '4px', verticalAlign: 'middle' }} />
                        ) : (
                          <ChevronDown size={12} style={{ marginLeft: '4px', verticalAlign: 'middle' }} />
                        )}
                      </span>
                    </div>
                    {expandedCitationIndex === idx && msg.context && (
                      <div className="citation-context-box">
                        {getHighlightedContext(msg.context, msg.start, msg.end)}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="chat-message assistant">
              <div className="chat-bubble">
                <div className="typing-indicator">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Suggestion tags */}
        {messages.length === 1 && (
          <div className="suggested-qs">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                className="suggested-q-btn"
                onClick={() => handleSend(q)}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        <div className="chat-input-panel">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask a compliance or policy question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button 
            className="chat-send-btn" 
            onClick={() => handleSend()}
            disabled={isLoading || !query.trim()}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
