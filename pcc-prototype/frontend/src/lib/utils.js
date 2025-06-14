import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function getBedStatusColor(status, hasBarriers) {
  if (status === 'available') return 'bg-gray-100 border-gray-300';
  if (hasBarriers) return 'bg-yellow-50 border-yellow-400';
  if (status === 'discharge-ready') return 'bg-green-50 border-green-400';
  return 'bg-blue-50 border-blue-400';
}

export function getBedStatusIcon(status) {
  if (status === 'available') return '🛏️';
  if (status === 'occupied') return '🏥';
  if (status === 'discharge-ready') return '✅';
  return '⚠️';
}

export function formatDuration(hours) {
  if (hours < 24) {
    return `${Math.round(hours)}h`;
  }
  const days = Math.floor(hours / 24);
  const remainingHours = Math.round(hours % 24);
  return `${days}d ${remainingHours}h`;
}

export function formatTimestamp(timestamp) {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}