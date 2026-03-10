/**
 * TeamDashboard: team overview with member workload visualization,
 * capacity planning indicators, and team performance metrics.
 */

import React, { useEffect, useState } from 'react';
import { teamsApi } from '../../api/teams';
import type { Team, TeamMember, WorkloadEntry } from '../../api/teams';
import { calculateProgress } from '../../utils/taskUtils';

interface TeamDashboardProps {
  teamId: string;
}

const CAPACITY_THRESHOLD = {
  low: 5,
  medium: 10,
  high: 15,
};

const TeamDashboard: React.FC<TeamDashboardProps> = ({ teamId }) => {
  const [team, setTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [workload, setWorkload] = useState<WorkloadEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadTeamData();
  }, [teamId]);

  const loadTeamData = async () => {
    setIsLoading(true);
    try {
      const [teamRes, membersRes, workloadRes] = await Promise.all([
        teamsApi.get(teamId),
        teamsApi.getMembers(teamId),
        teamsApi.getWorkload(teamId),
      ]);
      setTeam(teamRes.data);
      setMembers(membersRes.data);
      setWorkload(workloadRes.data);
    } catch (err) {
      console.error('Failed to load team data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !team) {
    return <div className="loading-spinner">Loading team dashboard...</div>;
  }

  const totalTasks = workload.reduce((sum, w) => sum + w.active_tasks, 0);
  const totalPoints = workload.reduce((sum, w) => sum + w.total_story_points, 0);
  const avgTasksPerMember = members.length > 0 ? Math.round(totalTasks / members.length) : 0;
  const maxTasks = Math.max(...workload.map((w) => w.active_tasks), 1);

  const getCapacityColor = (tasks: number): string => {
    if (tasks >= CAPACITY_THRESHOLD.high) return '#EF4444';
    if (tasks >= CAPACITY_THRESHOLD.medium) return '#F59E0B';
    if (tasks >= CAPACITY_THRESHOLD.low) return '#3B82F6';
    return '#10B981';
  };

  const getCapacityLabel = (tasks: number): string => {
    if (tasks >= CAPACITY_THRESHOLD.high) return 'Overloaded';
    if (tasks >= CAPACITY_THRESHOLD.medium) return 'At Capacity';
    if (tasks >= CAPACITY_THRESHOLD.low) return 'Normal';
    return 'Available';
  };

  return (
    <div className="team-dashboard">
      {/* Team Summary */}
      <div className="team-summary">
        <div className="team-header" style={{ borderLeftColor: team.color }}>
          <h2>{team.name}</h2>
          <p>{team.description}</p>
        </div>

        <div className="team-stats-grid">
          <div className="stat-card">
            <h4>Members</h4>
            <p className="stat-value">{members.length}</p>
          </div>
          <div className="stat-card">
            <h4>Active Tasks</h4>
            <p className="stat-value">{totalTasks}</p>
          </div>
          <div className="stat-card">
            <h4>Story Points</h4>
            <p className="stat-value">{totalPoints}</p>
          </div>
          <div className="stat-card">
            <h4>Avg Tasks/Person</h4>
            <p className="stat-value">{avgTasksPerMember}</p>
          </div>
        </div>
      </div>

      {/* Workload Distribution */}
      <div className="workload-section">
        <h3>Workload Distribution</h3>
        <div className="workload-grid">
          {workload.map((entry) => {
            const capacityColor = getCapacityColor(entry.active_tasks);
            const capacityLabel = getCapacityLabel(entry.active_tasks);
            const barPercent = (entry.active_tasks / maxTasks) * 100;

            return (
              <div key={entry.user.id} className="workload-member-card">
                <div className="member-header">
                  <div className="member-avatar-sm">
                    {entry.user.full_name.split(' ').map((n) => n[0]).join('').slice(0, 2)}
                  </div>
                  <div className="member-name-group">
                    <h4>{entry.user.full_name}</h4>
                    <span className="member-role">{entry.role}</span>
                  </div>
                  <span className="capacity-badge" style={{ color: capacityColor }}>
                    {capacityLabel}
                  </span>
                </div>

                <div className="member-workload-bar">
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{ width: `${barPercent}%`, backgroundColor: capacityColor }}
                    />
                  </div>
                  <span className="bar-label">
                    {entry.active_tasks} tasks | {entry.total_story_points} pts
                  </span>
                </div>

                <div className="priority-breakdown">
                  {Object.entries(entry.tasks_by_priority)
                    .filter(([_, count]) => count > 0)
                    .map(([priority, count]) => (
                      <span key={priority} className={`priority-chip priority-${priority}`}>
                        {priority}: {count}
                      </span>
                    ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Team Members */}
      <div className="members-section">
        <h3>Team Members</h3>
        <div className="members-grid">
          {members.map((member) => (
            <div key={member.id} className="member-tile">
              <div className="member-avatar-lg">
                {member.user.avatar ? (
                  <img src={member.user.avatar} alt={member.user.full_name} />
                ) : (
                  <span>
                    {member.user.first_name.charAt(0)}{member.user.last_name.charAt(0)}
                  </span>
                )}
              </div>
              <h4>{member.user.full_name}</h4>
              <span className="member-email">{member.user.email}</span>
              {member.user.job_title && <span className="member-job">{member.user.job_title}</span>}
              <span className={`role-badge role-${member.role}`}>{member.role}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TeamDashboard;
