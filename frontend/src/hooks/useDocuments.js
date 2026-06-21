import { useState, useEffect } from 'react';
import { api } from '../api/client';

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocs = async () => {
    setIsLoading(true);
    try {
      const data = await api.getDocuments();
      setDocuments(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const uploadDocs = async (files) => {
    setIsLoading(true);
    try {
      const result = await api.uploadDocuments(files);
      await fetchDocs();
      return result;
    } catch (e) {
      setError(e.message);
      throw e;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteDoc = async (id) => {
    try {
      await api.deleteDocument(id);
      await fetchDocs();
    } catch (e) {
      setError(e.message);
      throw e;
    }
  };

  useEffect(() => {
    let active = true;
    api.getDocuments()
      .then(data => {
        if (active) {
          setDocuments(data);
          setError(null);
          setIsLoading(false);
        }
      })
      .catch(e => {
        if (active) {
          setError(e.message);
          setIsLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  return {
    documents,
    isLoading,
    error,
    refreshDocuments: fetchDocs,
    uploadDocuments: uploadDocs,
    deleteDocument: deleteDoc
  };
}
export default useDocuments;
