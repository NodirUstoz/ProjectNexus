/**
 * TeamPage: team management with member listing, workload view, and project assignments.
 */

import React, { useEffect, useState } from 'react';
import { teamsApi } from '../api/teams';
import type { Team, TeamMember, WorkloadEntry } from '../api/teams';

const TeamPage: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [workload, setWorkload] = useState<WorkloadEntry[]>([]);
  const [activeTab, setActiveTab] = useState<'members' | 'workload' | 'projects'>('members');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadTeams();
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      loadTeamDetails(selectedTeam.id);
    }
  }, [selectedTeam, activeTab]);

  const loadTeams = async () => {
    setIsLoading(true);
    try {
      const { data } = await teamsApi.list({ active: 'true' });
      setTeams(data.results);
      if (data.results.length > 0) {
        setSelectedTeam(data.results[0]);
      }
    } catch (err) {
      console.error('Failed to load teams:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadTeamDetails = async (teamId: string) => {
    try {
      if (activeTab === 'members') {
        const { data } = await teamsApi.getMembers(teamId);
        setMembers(data);
      } else if (activeTab === 'workload') {
        const { data } = await teamsApi.getWorkload(teamId);
        setWorkload(data);
      }
    } catch (err) {
      console.error('Failed to load team details:', err);
    }
  };

  const getMaxTasks = () => Math.max(...workload.map((w) => w.active_tasks), 1);

  return (
    <div className="team-page">
      <header className="page-header">
        <h1>Teams</h1>
        <button className="btn btn-primary">Create Team</button>
      </header>

      <div className="team-layout">
        {/* Team Sidebar */}
        <aside className="team-sidebar">
          <h3>Your Teams</h3>
          {teams.map((team) => (
            <div
              key={team.id}
              className={`team-item ${selectedTeam?.id === team.id ? 'active' : ''}`}
              onClick={() => setSelectedTeam(team)}
            >
              <div
                className="team-avatar"
                style={{ backgroundColor: team.color }}
              >
                {team.name.charAt(0).toUpperCase()}
              </div>
              <div className="team-item-info">
                <h4>{team.name}</h4>
                <span>{team.member_count} members</span>
              </div>
            </div>
          ))}
        </aside>

        {/* Team Detail */}
        {selectedTeam ? (
          <main className="team-detail">
            <div className="team-detail-header">
              <div>
                <h2>{selectedTeam.name}</h2>
                <p>{selectedTeam.description || 'No description'}</p>
              </div>
              <div className="team-stats">
                <div className="stat">
                  <span className="stat-value">{selectedTeam.member_count}</span>
                  <span className="stat-label">Members</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{selectedTeam.active_tasks_count}</span>
                  <span className="stat-label">Active Tasks</span>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="tabs">
              {(['members', 'workload', 'projects'] as const).map((tab) => (
                <button
                  key={tab}
                  className={`tab ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Members Tab */}
            {activeTab === 'members' && (
              <div className="members-list">
                {members.map((member) => (
                  <div key={member.id} className="member-card">
                    <div className="member-avatar">
                      {member.user.avatar ? (
                        <img src={member.user.avatar} alt={member.user.full_name} />
                      ) : (
                        <div className="avatar-placeholder">
                          {member.user.first_name.charAt(0)}{member.user.last_name.charAt(0)}
                        </div>
                      )}
                    </div>
                    <div className="member-info">
                      <h4>{member.user.full_name}</h4>
                      <span className="member-email">{member.user.email}</span>
                      {member.user.job_title && (
                        <span className="member-title">{member.user.job_title}</span>
                      )}
                    </div>
                    <span className={`role-badge role-${member.role}`}>{member.role}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Workload Tab */}
            {activeTab === 'workload' && (
              <div className="workload-chart">
                {workload.map((entry) => {
                  const maxTasks = getMaxTasks();
                  const barWidth = (entry.active_tasks / maxTasks) * 100;

                  return (
                    <div key={entry.user.id} className="workload-row">
                      <div className="workload-user">
                        <span className="user-name">{entry.user.full_name}</span>
                        <span className="user-role">{entry.role}</span>
                      </div>
                      <div className="workload-bar-container">
                        <div
                          className="workload-bar"
                          style={{
                            width: `${barWidth}%`,
                            backgroundColor: entry.active_tasks > 10 ? '#EF4444' : '#3B82F6',
                          }}
                        />
                        <span className="workload-count">
                          {entry.active_tasks} tasks | {entry.total_story_points} pts
                        </span>
                      </div>
                      <div className="workload-priority-breakdown">
                        {entry.tasks_by_priority.highest > 0 && (
                          <span className="priority-dot priority-highest">{entry.tasks_by_priority.highest}</span>
                        )}
                        {entry.tasks_by_priority.high > 0 && (
                          <span className="priority-dot priority-high">{entry.tasks_by_priority.high}</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </main>
        ) : (
          <div className="empty-state">
            <h3>No team selected</h3>
            <p>Select a team from the sidebar or create a new one.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamPage;
