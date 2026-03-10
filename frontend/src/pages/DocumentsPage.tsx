/**
 * DocumentsPage: document manager with folder navigation, search, rich editor,
 * and version history.
 */

import React, { useEffect, useState } from 'react';
import { documentsApi } from '../api/documents';
import type { Document, DocumentFolder, DocumentVersion } from '../api/documents';
import { formatDate, timeAgo } from '../utils/dateUtils';

const DOC_TYPE_LABELS: Record<string, string> = {
  page: 'Page',
  wiki: 'Wiki',
  spec: 'Specification',
  meeting: 'Meeting Notes',
  template: 'Template',
};

const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [folders, setFolders] = useState<DocumentFolder[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<(Document & { versions?: DocumentVersion[] }) | null>(null);
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [folderPath, setFolderPath] = useState<DocumentFolder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showEditor, setShowEditor] = useState(false);
  const [editorContent, setEditorContent] = useState({ title: '', content: '' });

  useEffect(() => {
    loadDocuments();
    loadFolders();
  }, [currentFolderId]);

  const loadDocuments = async () => {
    setIsLoading(true);
    try {
      const params: Record<string, string> = {};
      if (currentFolderId) {
        params.folder = currentFolderId;
      } else {
        params.root = 'true';
      }
      if (searchQuery) params.search = searchQuery;

      const { data } = await documentsApi.list(params);
      setDocuments(data.results);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFolders = async () => {
    try {
      const params: Record<string, string> = {};
      if (!currentFolderId) params.root = 'true';
      const { data } = await documentsApi.listFolders(params);
      setFolders(data.results);
    } catch (err) {
      console.error('Failed to load folders:', err);
    }
  };

  const openDocument = async (doc: Document) => {
    try {
      const { data } = await documentsApi.get(doc.id);
      setSelectedDoc(data);
      setShowEditor(true);
      setEditorContent({ title: data.title, content: data.content });
    } catch (err) {
      console.error('Failed to open document:', err);
    }
  };

  const saveDocument = async () => {
    if (!selectedDoc) return;
    try {
      await documentsApi.update(selectedDoc.id, {
        title: editorContent.title,
        content: editorContent.content,
        change_summary: 'Content updated',
      });
      loadDocuments();
    } catch (err) {
      console.error('Failed to save document:', err);
    }
  };

  const handlePin = async (docId: string) => {
    await documentsApi.togglePin(docId);
    loadDocuments();
  };

  const navigateToFolder = (folder: DocumentFolder | null) => {
    if (folder) {
      setCurrentFolderId(folder.id);
      setFolderPath((prev) => [...prev, folder]);
    } else {
      setCurrentFolderId(null);
      setFolderPath([]);
    }
  };

  const navigateUp = (index: number) => {
    if (index < 0) {
      setCurrentFolderId(null);
      setFolderPath([]);
    } else {
      setCurrentFolderId(folderPath[index].id);
      setFolderPath((prev) => prev.slice(0, index + 1));
    }
  };

  return (
    <div className="documents-page">
      <header className="page-header">
        <h1>Documents</h1>
        <div className="header-actions">
          <button className="btn btn-outline">New Folder</button>
          <button className="btn btn-primary">New Document</button>
        </div>
      </header>

      {/* Breadcrumb */}
      <nav className="breadcrumb">
        <span className="breadcrumb-item" onClick={() => navigateUp(-1)}>
          Documents
        </span>
        {folderPath.map((folder, idx) => (
          <React.Fragment key={folder.id}>
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-item" onClick={() => navigateUp(idx)}>
              {folder.name}
            </span>
          </React.Fragment>
        ))}
      </nav>

      {/* Search */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search documents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && loadDocuments()}
        />
      </div>

      <div className="documents-layout">
        {/* Document List */}
        <div className="documents-list">
          {/* Folders */}
          {folders.map((folder) => (
            <div
              key={folder.id}
              className="document-item folder-item"
              onClick={() => navigateToFolder(folder)}
            >
              <span className="folder-icon" style={{ color: folder.color }}>Folder</span>
              <div className="document-info">
                <h4>{folder.name}</h4>
                <span>{folder.document_count} documents, {folder.subfolder_count} subfolders</span>
              </div>
            </div>
          ))}

          {/* Documents */}
          {isLoading ? (
            <div className="loading-spinner">Loading...</div>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.id}
                className={`document-item ${selectedDoc?.id === doc.id ? 'selected' : ''}`}
                onClick={() => openDocument(doc)}
              >
                <div className="document-icon">
                  <span className={`doc-type-badge doc-type-${doc.doc_type}`}>
                    {DOC_TYPE_LABELS[doc.doc_type]}
                  </span>
                </div>
                <div className="document-info">
                  <h4>
                    {doc.is_pinned && <span className="pin-icon">Pinned</span>}
                    {doc.title}
                  </h4>
                  <span className="document-meta">
                    {doc.author?.full_name} | v{doc.version} | {doc.word_count} words | Updated {timeAgo(doc.updated_at)}
                  </span>
                </div>
                <div className="document-actions" onClick={(e) => e.stopPropagation()}>
                  <button className="btn btn-icon" onClick={() => handlePin(doc.id)}>
                    {doc.is_pinned ? 'Unpin' : 'Pin'}
                  </button>
                </div>
              </div>
            ))
          )}

          {documents.length === 0 && folders.length === 0 && !isLoading && (
            <div className="empty-state">
              <h3>No documents here</h3>
              <p>Create a new document or folder to get started.</p>
            </div>
          )}
        </div>

        {/* Editor Panel */}
        {showEditor && selectedDoc && (
          <div className="document-editor">
            <div className="editor-header">
              <input
                type="text"
                className="editor-title"
                value={editorContent.title}
                onChange={(e) => setEditorContent({ ...editorContent, title: e.target.value })}
              />
              <div className="editor-actions">
                <button className="btn btn-sm" onClick={saveDocument}>Save</button>
                <button className="btn btn-sm btn-outline" onClick={() => setShowEditor(false)}>Close</button>
              </div>
            </div>
            <div className="editor-meta">
              <span>Last edited by {selectedDoc.last_edited_by?.full_name}</span>
              <span>Version {selectedDoc.version}</span>
              <span>{selectedDoc.word_count} words</span>
            </div>
            <textarea
              className="editor-content"
              value={editorContent.content}
              onChange={(e) => setEditorContent({ ...editorContent, content: e.target.value })}
              placeholder="Write your content here... Markdown is supported."
            />
            {selectedDoc.versions && selectedDoc.versions.length > 0 && (
              <div className="version-history">
                <h4>Version History</h4>
                {selectedDoc.versions.slice(0, 5).map((v) => (
                  <div key={v.id} className="version-entry">
                    <span>v{v.version_number}</span>
                    <span>{v.edited_by?.full_name}</span>
                    <span>{v.change_summary}</span>
                    <span>{formatDate(v.created_at)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentsPage;
