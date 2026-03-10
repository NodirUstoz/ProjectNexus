/**
 * ProjectsPage: lists all projects with filtering, search, and create functionality.
 */

import React, { useEffect, useState } from 'react';
import { useProjectStore } from '../store/projectSlice';
import { formatDate } from '../utils/dateUtils';

type ViewMode = 'grid' | 'list';
type FilterType = 'all' | 'kanban' | 'scrum';

const ProjectsPage: React.FC = () => {
  const { projects, isLoading, fetchProjects, createProject, archiveProject } = useProjectStore();
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    key: '',
    description: '',
    project_type: 'kanban' as const,
    color: '#4A90D9',
  });

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const filteredProjects = projects.filter((p) => {
    if (filterType !== 'all' && p.project_type !== filterType) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        p.name.toLowerCase().includes(query) ||
        p.key.toLowerCase().includes(query) ||
        p.description.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProject({
        ...newProject,
        workspace_id: '', // Set from context
      });
      setShowCreateModal(false);
      setNewProject({ name: '', key: '', description: '', project_type: 'kanban', color: '#4A90D9' });
    } catch {
      // Error handled by store
    }
  };

  return (
    <div className="projects-page">
      <header className="page-header">
        <h1>Projects</h1>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          New Project
        </button>
      </header>

      {/* Filters Bar */}
      <div className="filters-bar">
        <input
          type="text"
          placeholder="Search projects..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        <div className="filter-group">
          {(['all', 'kanban', 'scrum'] as FilterType[]).map((type) => (
            <button
              key={type}
              className={`filter-btn ${filterType === type ? 'active' : ''}`}
              onClick={() => setFilterType(type)}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
        <div className="view-toggle">
          <button
            className={viewMode === 'grid' ? 'active' : ''}
            onClick={() => setViewMode('grid')}
          >
            Grid
          </button>
          <button
            className={viewMode === 'list' ? 'active' : ''}
            onClick={() => setViewMode('list')}
          >
            List
          </button>
        </div>
      </div>

      {/* Project List/Grid */}
      {isLoading ? (
        <div className="loading-spinner">Loading projects...</div>
      ) : (
        <div className={viewMode === 'grid' ? 'project-grid' : 'project-list'}>
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className={viewMode === 'grid' ? 'project-card' : 'project-row'}
              style={{ borderLeftColor: project.color }}
            >
              <div className="project-header">
                <span className="project-icon">{project.icon}</span>
                <div className="project-title-group">
                  <h3>{project.name}</h3>
                  <span className="project-key">{project.key}</span>
                </div>
                <span className={`badge badge-${project.project_type}`}>
                  {project.project_type}
                </span>
              </div>
              {viewMode === 'grid' && (
                <p className="project-description">
                  {project.description || 'No description'}
                </p>
              )}
              <div className="project-stats">
                <span>{project.task_count} tasks</span>
                <span>{project.member_count} members</span>
                {project.lead && <span>Lead: {project.lead.full_name}</span>}
                <span>Updated {formatDate(project.updated_at)}</span>
              </div>
              <div className="project-actions">
                <button className="btn btn-sm">Open Board</button>
                <button className="btn btn-sm btn-outline" onClick={() => archiveProject(project.id)}>
                  Archive
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {filteredProjects.length === 0 && !isLoading && (
        <div className="empty-state">
          <h3>No projects found</h3>
          <p>Create your first project to get started.</p>
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Project</h2>
            <form onSubmit={handleCreateProject}>
              <div className="form-group">
                <label>Project Name</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Project Key</label>
                <input
                  type="text"
                  value={newProject.key}
                  onChange={(e) => setNewProject({ ...newProject, key: e.target.value.toUpperCase() })}
                  maxLength={10}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Type</label>
                <select
                  value={newProject.project_type}
                  onChange={(e) => setNewProject({ ...newProject, project_type: e.target.value as 'kanban' | 'scrum' })}
                >
                  <option value="kanban">Kanban</option>
                  <option value="scrum">Scrum</option>
                </select>
              </div>
              <div className="form-group">
                <label>Color</label>
                <input
                  type="color"
                  value={newProject.color}
                  onChange={(e) => setNewProject({ ...newProject, color: e.target.value })}
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectsPage;
