/**
 * Date formatting and calculation utilities for the project management UI.
 */

/**
 * Format a date string to a human-readable format.
 * Example: "2025-01-15T10:30:00Z" -> "Jan 15, 2025"
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format a date string to include time.
 * Example: "2025-01-15T10:30:00Z" -> "Jan 15, 2025 10:30 AM"
 */
export function formatDateTime(dateString: string | null | undefined): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Get a relative time string (e.g., "2 hours ago", "in 3 days").
 */
export function timeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(Math.abs(diffMs) / 1000);
  const isFuture = diffMs < 0;

  const intervals: [number, string][] = [
    [31536000, 'year'],
    [2592000, 'month'],
    [604800, 'week'],
    [86400, 'day'],
    [3600, 'hour'],
    [60, 'minute'],
  ];

  for (const [seconds, label] of intervals) {
    const count = Math.floor(diffSeconds / seconds);
    if (count >= 1) {
      const plural = count > 1 ? 's' : '';
      return isFuture
        ? `in ${count} ${label}${plural}`
        : `${count} ${label}${plural} ago`;
    }
  }

  return 'just now';
}

/**
 * Calculate the number of days between two dates.
 */
export function daysBetween(start: string, end: string): number {
  const startDate = new Date(start);
  const endDate = new Date(end);
  const diffMs = endDate.getTime() - startDate.getTime();
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}

/**
 * Check if a date is overdue (before today).
 */
export function isOverdue(dateString: string | null | undefined): boolean {
  if (!dateString) return false;
  const date = new Date(dateString);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date < today;
}

/**
 * Check if a date is within the next N days.
 */
export function isDueSoon(dateString: string | null | undefined, days: number = 3): boolean {
  if (!dateString) return false;
  const date = new Date(dateString);
  const now = new Date();
  const future = new Date();
  future.setDate(future.getDate() + days);
  return date >= now && date <= future;
}

/**
 * Format hours into a human-readable duration string.
 * Example: 10.5 -> "10h 30m"
 */
export function formatDuration(hours: number): string {
  if (hours === 0) return '0h';
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

/**
 * Get date ranges for common filters.
 */
export function getDateRange(range: 'today' | 'week' | 'month' | 'quarter'): {
  start: string;
  end: string;
} {
  const today = new Date();
  const start = new Date(today);
  const end = new Date(today);

  switch (range) {
    case 'today':
      break;
    case 'week':
      start.setDate(today.getDate() - today.getDay());
      end.setDate(start.getDate() + 6);
      break;
    case 'month':
      start.setDate(1);
      end.setMonth(end.getMonth() + 1, 0);
      break;
    case 'quarter':
      const qMonth = Math.floor(today.getMonth() / 3) * 3;
      start.setMonth(qMonth, 1);
      end.setMonth(qMonth + 3, 0);
      break;
  }

  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0],
  };
}
