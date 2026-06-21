/**
 * VERICO API client for interacting with the FastAPI backend.
 */

export const api = {
  /**
   * Fetches the list of all documents and their risk summaries.
   */
  async getDocuments() {
    const res = await fetch('/api/documents');
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  /**
   * Fetches detailed information, including individual risk matches, for a single document.
   */
  async getDocumentDetails(docId) {
    const res = await fetch(`/api/documents/${docId}`);
    if (!res.ok) throw new Error('Failed to fetch document details');
    return res.json();
  },

  /**
   * Fetches all detected risk clauses across all documents.
   */
  async getAllRisks() {
    const res = await fetch('/api/documents/risks');
    if (!res.ok) throw new Error('Failed to fetch all risks');
    return res.json();
  },

  /**
   * Uploads multiple PDF documents for parsing and compliance scanning.
   */
  async uploadDocuments(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    const res = await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload documents');
    return res.json();
  },

  /**
   * Deletes a document, its chunks, and associated risk flags.
   */
  async deleteDocument(docId) {
    const res = await fetch(`/api/documents/${docId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete document');
    return res.json();
  },

  /**
   * Queries the extractive QA engine across all or specific documents.
   */
  async askQuestion(question, documentIds = null) {
    const res = await fetch('/api/qa/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        document_ids: documentIds && documentIds.length > 0 ? documentIds : null
      }),
    });
    if (!res.ok) throw new Error('QA search query failed');
    return res.json();
  }
};
