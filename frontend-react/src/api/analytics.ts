import { api } from './client';
import type { DashboardData, Campaign } from '../types';

export function getDashboard(days = 7) {
  return api.get<DashboardData>(`/analytics/dashboard?days=${days}`);
}

export function getCampaignAnalytics() {
  return api.get<{ campaigns: Campaign[] }>('/analytics/campaigns');
}
