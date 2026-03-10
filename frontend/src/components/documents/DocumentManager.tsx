/**
 * DocumentManager: reusable component for browsing, creating, and managing
 * documents within a project. Supports folder navigation and search.
 */

import React, { useEffect, useState } from 'react';
import { documentsApi } from '../../api/documents';
import type { Document, DocumentFolder } from '../../api/documents';
import { timeAgo } from '../../utils/dateUtils';
import { useDebounce } from '../../hooks/useDebounce';

interface DocumentManagerProps {
  projectId: string;
  onDocumentOpen: (doc: Document) => void;
}

const DocumentManager: React.FC<DocumentManagerProps> = ({ projectId, onDocumentOpen }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [folders, setFolders] = useState<DocumentFolder[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<Array<{ id: string; name: string }>>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'updated_at' | 'title' | 'created_at'>('updated_at');

  const debouncedSearch = useDebounce(searchQuery, 300);

  useEffect(() => {
    loadContent();
  }, [projectId, currentFolder, debouncedSearch, filterType]);

  const loadContent = async () => {
    setIsLoading(true);
    try {
      const docParams: Record<string, string> = { project: projectId };
      if (currentFolder) {
        docParams.folder = currentFolder;
      } else {
        docParams.root = 'true';
      }
      if (debouncedSearch) docParams.search = debouncedSearch;
      if (filterType) docParams.type = filterType;

      const [docsRes, foldersRes] = await Promise.all([
        documentsApi.list(docParams),
        documentsApi.listFolders({
          project: projectId,
          ...(currentFolder ? {} : { root: 'true' }),
        }),
      ]);

      setDocuments(docsRes.data.results);
      setFolders(foldersRes.data.results);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const navigateToFolder = (folder: DocumentFolder) => {
    setCurrentFolder(folder.id);
    setBreadcrumbs((prev) => [...prev, { id: folder.id, name: folder.name }]);
  };

  const navigateToBreadcrumb = (index: number) => {
    if (index < 0) {
      setCurrentFolder(null);
      setBreadcrumbs([]);
    } else {
      setCurrentFolder(breadcrumbs[index].id);
      setBreadcrumbs((prev) => prev.slice(0, index + 1));
    }
  };

  const handleCreateDocument = async () => {
    try {
      const { data: newDoc } = await documentsApi.create({
        title: 'Untitled Document',
        project_id: projectId,
        folder: currentFolder || undefined,
        doc_type: 'page',
      });
      onDocumentOpen(newDoc);
      loadContent();
    } catch (err) {
      console.error('Failed to create document:', err);
    }
  };

  const handleCreateFolder = async () => {
    const name = prompt('Folder name:');
    if (!name) return;
    try {
      await documentsApi.createFolder({
        name,
        project_id: projectId,
        parent: currentFolder || undefined,
      });
      loadContent();
    } catch (err) {
      console.error('Failed to create folder:', err);
    }
  };

  const handlePin = async (docId: string) => {
    await documentsApi.togglePin(docId);
    loadContent();
  };

  const handleDuplicate = async (docId: string) => {
    await documentsApi.duplicate(docId);
    loadContent();
  };

  const sortedDocuments = [...documents].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1;
    if (!a.is_pinned && b.is_pinned) return 1;
    if (sortBy === 'title') return a.title.localeCompare(b.title);
    return new Date(b[sortBy]).getTime() - new Date(a[sortBy]).getTime();
  });

  return (
    <div className="document-manager">
      {/* Toolbar */}
      <div className="doc-toolbar">
        <div className="toolbar-left">
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="doc-search-input"
          />
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <option value="">All Types</option>
            <option value="page">Pages</option>
            <option value="wiki">Wiki</option>
            <option value="spec">Specifications</option>
            <option value="meeting">Meeting Notes</option>
          </select>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)}>
            <option value="updated_at">Last Updated</option>
            <option value="created_at">Created Date</option>
            <option value="title">Title</option>
          </select>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-sm btn-outline" onClick={handleCreateFolder}>
            New Folder
          </button>
          <button className="btn btn-sm btn-primary" onClick={handleCreateDocument}>
            New Document
          </button>
        </div>
      </div>

      {/* Breadcrumbs */}
      <nav className="doc-breadcrumbs">
        <span onClick={() => navigateToBreadcrumb(-1)} className="breadcrumb-link">
          Root
        </span>
        {breadcrumbs.map((crumb, idx) => (
          <React.Fragment key={crumb.id}>
            <span className="breadcrumb-sep">/</span>
            <span onClick={() => navigateToBreadcrumb(idx)} className="breadcrumb-link">
              {crumb.name}
            </span>
          </React.Fragment>
        ))}
      </nav>

      {/* Content */}
      {isLoading ? (
        <div className="loading-spinner">Loading...</div>
      ) : (
        <div className="doc-grid">
          {/* Folders */}
          {folders.map((folder) => (
            <div
              key={folder.id}
              className="doc-item folder"
              onClick={() => navigateToFolder(folder)}
            >
              <div className="doc-item-icon" style={{ color: folder.color }}>
                Folder
              </div>
              <div className="doc-item-info">
                <h4>{folder.name}</h4>
                <span>{folder.document_count} docs</span>
              </div>
            </div>
          ))}

          {/* Documents */}
          {sortedDocuments.map((doc) => (
            <div
              key={doc.id}
              className="doc-item document"
              onClick={() => onDocumentOpen(doc)}
            >
              <div className="doc-item-header">
                <span className={`doc-type-indicator doc-type-${doc.doc_type}`}>
                  {doc.doc_type}
                </span>
                {doc.is_pinned && <span className="pinned-indicator">Pinned</span>}
              </div>
              <h4>{doc.title}</h4>
              <div className="doc-item-meta">
                <span>v{doc.version}</span>
                <span>{doc.word_count} words</span>
                <span>{timeAgo(doc.updated_at)}</span>
              </div>
              <div className="doc-item-actions" onClick={(e) => e.stopPropagation()}>
                <button onClick={() => handlePin(doc.id)}>
                  {doc.is_pinned ? 'Unpin' : 'Pin'}
                </button>
                <button onClick={() => handleDuplicate(doc.id)}>Duplicate</button>
              </div>
            </div>
          ))}

          {sortedDocuments.length === 0 && folders.length === 0 && (
            <div className="empty-state">
              <p>No documents found. Create one to get started.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentManager;
