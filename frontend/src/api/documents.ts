/**
 * Documents API module: CRUD, versioning, folder management.
 */

import apiClient from './client';
import type { User } from './projects';

export interface DocumentFolder {
  id: string;
  name: string;
  parent: string | null;
  color: string;
  created_by: User;
  document_count: number;
  subfolder_count: number;
  full_path: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  title: string;
  content: string;
  doc_type: 'page' | 'wiki' | 'spec' | 'meeting' | 'template';
  author: User;
  last_edited_by: User;
  folder: string | null;
  folder_name: string | null;
  is_pinned: boolean;
  is_archived: boolean;
  is_template: boolean;
  version: number;
  word_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  id: string;
  version_number: number;
  title: string;
  content: string;
  edited_by: User;
  change_summary: string;
  created_at: string;
}

export const documentsApi = {
  list(params?: {
    project?: string;
    folder?: string;
    type?: string;
    search?: string;
    pinned?: string;
    templates?: string;
    root?: string;
  }) {
    return apiClient.get<{ results: Document[] }>('/documents/', { params });
  },

  get(id: string) {
    return apiClient.get<Document & { versions: DocumentVersion[] }>(`/documents/${id}/`);
  },

  create(data: {
    title: string;
    project_id: string;
    content?: string;
    doc_type?: string;
    folder?: string;
    is_template?: boolean;
  }) {
    return apiClient.post<Document>('/documents/', data);
  },

  update(id: string, data: Partial<Document> & { change_summary?: string }) {
    return apiClient.patch<Document>(`/documents/${id}/`, data);
  },

  delete(id: string) {
    return apiClient.delete(`/documents/${id}/`);
  },

  togglePin(id: string) {
    return apiClient.post<Document>(`/documents/${id}/pin/`);
  },

  archive(id: string) {
    return apiClient.post(`/documents/${id}/archive/`);
  },

  getVersions(id: string) {
    return apiClient.get<DocumentVersion[]>(`/documents/${id}/versions/`);
  },

  restoreVersion(docId: string, versionNumber: number) {
    return apiClient.post(`/documents/${docId}/versions/${versionNumber}/restore/`);
  },

  duplicate(id: string) {
    return apiClient.post<Document>(`/documents/${id}/duplicate/`);
  },

  // Folder operations
  listFolders(params?: { project?: string; root?: string }) {
    return apiClient.get<{ results: DocumentFolder[] }>('/folders/', { params });
  },

  createFolder(data: {
    name: string;
    project_id: string;
    parent?: string;
    color?: string;
  }) {
    return apiClient.post<DocumentFolder>('/folders/', data);
  },

  getFolderTree(folderId: string) {
    return apiClient.get(`/folders/${folderId}/tree/`);
  },
};
