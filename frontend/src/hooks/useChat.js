import { useState } from 'react';
import { api } from '../api/client';

export function useChat() {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'Hello! I am VERICO, your compliance intelligence assistant. Select documents and ask me any questions about policies, contracts, or security procedures.',
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (question, documentIds = null) => {
    if (!question.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: question }]);
    setIsLoading(true);
    setError(null);

    try {
      const res = await api.askQuestion(question, documentIds);
      
      const newMsg = {
        sender: 'assistant',
        text: res.answer,
        score: res.score,
        document_name: res.document_name,
        page_number: res.page_number,
        context: res.context,
        start: res.start,
        end: res.end
      };

      setMessages(prev => [...prev, newMsg]);
      return newMsg;
    } catch (e) {
      setError(e.message);
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: 'Sorry, I encountered an error searching for that answer. Please try again.',
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        sender: 'assistant',
        text: 'Hello! I am VERICO, your compliance intelligence assistant. Select documents and ask me any questions about policies, contracts, or security procedures.',
      }
    ]);
  };

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat
  };
}
export default useChat;
