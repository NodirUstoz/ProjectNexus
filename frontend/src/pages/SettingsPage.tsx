/**
 * SettingsPage: user profile settings, notification preferences,
 * workspace management, and account configuration.
 */

import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authSlice';
import { notificationsApi } from '../api/notifications';
import type { NotificationPreferences } from '../api/notifications';

type SettingsTab = 'profile' | 'notifications' | 'workspace' | 'account';

const SettingsPage: React.FC = () => {
  const { user, updateProfile } = useAuthStore();
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    job_title: '',
    bio: '',
    timezone: 'UTC',
  });
  const [notifPrefs, setNotifPrefs] = useState<NotificationPreferences | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    if (user) {
      setProfileForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        username: user.username || '',
        job_title: user.job_title || '',
        bio: user.bio || '',
        timezone: user.timezone || 'UTC',
      });
    }
  }, [user]);

  useEffect(() => {
    if (activeTab === 'notifications') {
      loadNotificationPreferences();
    }
  }, [activeTab]);

  const loadNotificationPreferences = async () => {
    try {
      const { data } = await notificationsApi.getPreferences();
      setNotifPrefs(data);
    } catch (err) {
      console.error('Failed to load notification preferences:', err);
    }
  };

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await updateProfile(profileForm);
      setSaveMessage('Profile updated successfully.');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch {
      setSaveMessage('Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleNotifPrefChange = async (
    key: keyof NotificationPreferences,
    value: string | boolean
  ) => {
    if (!notifPrefs) return;
    const updated = { ...notifPrefs, [key]: value };
    setNotifPrefs(updated);
    try {
      await notificationsApi.updatePreferences({ [key]: value });
    } catch {
      // Revert on failure
      loadNotificationPreferences();
    }
  };

  const TIMEZONES = [
    'UTC', 'US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific',
    'Europe/London', 'Europe/Paris', 'Europe/Berlin',
    'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Kolkata',
    'Australia/Sydney',
  ];

  const CHANNEL_OPTIONS = [
    { value: 'both', label: 'In-App & Email' },
    { value: 'in_app', label: 'In-App Only' },
    { value: 'email', label: 'Email Only' },
    { value: 'none', label: 'Disabled' },
  ];

  return (
    <div className="settings-page">
      <header className="page-header">
        <h1>Settings</h1>
      </header>

      <div className="settings-layout">
        {/* Sidebar */}
        <aside className="settings-sidebar">
          {(['profile', 'notifications', 'workspace', 'account'] as SettingsTab[]).map((tab) => (
            <button
              key={tab}
              className={`settings-nav-item ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </aside>

        {/* Content */}
        <main className="settings-content">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="settings-section">
              <h2>Profile Settings</h2>
              {saveMessage && <div className="alert">{saveMessage}</div>}
              <form onSubmit={handleProfileSave}>
                <div className="form-row">
                  <div className="form-group">
                    <label>First Name</label>
                    <input
                      type="text"
                      value={profileForm.first_name}
                      onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Last Name</label>
                    <input
                      type="text"
                      value={profileForm.last_name}
                      onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    value={profileForm.username}
                    onChange={(e) => setProfileForm({ ...profileForm, username: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Job Title</label>
                  <input
                    type="text"
                    value={profileForm.job_title}
                    onChange={(e) => setProfileForm({ ...profileForm, job_title: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Bio</label>
                  <textarea
                    value={profileForm.bio}
                    onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                    rows={4}
                    maxLength={500}
                  />
                  <span className="char-count">{profileForm.bio.length}/500</span>
                </div>
                <div className="form-group">
                  <label>Timezone</label>
                  <select
                    value={profileForm.timezone}
                    onChange={(e) => setProfileForm({ ...profileForm, timezone: e.target.value })}
                  >
                    {TIMEZONES.map((tz) => (
                      <option key={tz} value={tz}>{tz}</option>
                    ))}
                  </select>
                </div>
                <button type="submit" className="btn btn-primary" disabled={isSaving}>
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </form>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && notifPrefs && (
            <div className="settings-section">
              <h2>Notification Preferences</h2>
              <div className="notification-prefs">
                {[
                  { key: 'task_assigned' as const, label: 'Task Assigned to You' },
                  { key: 'task_updated' as const, label: 'Task Updates' },
                  { key: 'task_commented' as const, label: 'Task Comments' },
                  { key: 'mentioned' as const, label: 'Mentions' },
                  { key: 'milestone_due' as const, label: 'Milestone Due Dates' },
                  { key: 'sprint_updates' as const, label: 'Sprint Updates' },
                  { key: 'document_updated' as const, label: 'Document Updates' },
                  { key: 'team_updates' as const, label: 'Team Updates' },
                ].map(({ key, label }) => (
                  <div key={key} className="pref-row">
                    <span className="pref-label">{label}</span>
                    <select
                      value={notifPrefs[key] as string}
                      onChange={(e) => handleNotifPrefChange(key, e.target.value)}
                    >
                      {CHANNEL_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>
                ))}

                <h3>Digest Emails</h3>
                <div className="pref-row">
                  <span className="pref-label">Daily Digest</span>
                  <input
                    type="checkbox"
                    checked={notifPrefs.daily_digest}
                    onChange={(e) => handleNotifPrefChange('daily_digest', e.target.checked)}
                  />
                </div>
                <div className="pref-row">
                  <span className="pref-label">Weekly Summary</span>
                  <input
                    type="checkbox"
                    checked={notifPrefs.weekly_summary}
                    onChange={(e) => handleNotifPrefChange('weekly_summary', e.target.checked)}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Account Tab */}
          {activeTab === 'account' && (
            <div className="settings-section">
              <h2>Account</h2>
              <div className="account-info">
                <p><strong>Email:</strong> {user?.email}</p>
                <p><strong>Member since:</strong> {user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}</p>
              </div>
              <div className="danger-zone">
                <h3>Danger Zone</h3>
                <button className="btn btn-danger">Change Password</button>
                <button className="btn btn-danger btn-outline">Delete Account</button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default SettingsPage;
