import { api } from './client';
import type { Campaign } from '../types';

export function listCampaigns(params?: { status?: string; page?: number; page_size?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.page) searchParams.set('page', String(params.page));
  if (params?.page_size) searchParams.set('page_size', String(params.page_size));
  const qs = searchParams.toString();
  return api.get<{ total: number; campaigns: Campaign[] }>(`/campaigns${qs ? `?${qs}` : ''}`);
}

export function getCampaign(id: string) {
  return api.get<Campaign>(`/campaigns/${id}`);
}

export function createCampaign(data: {
  name: string;
  script_template: string;
  greeting_message?: string;
  closing_message?: string;
}) {
  return api.post<Campaign>('/campaigns', data);
}

export function updateCampaign(id: string, data: Partial<Campaign>) {
  return api.patch<Campaign>(`/campaigns/${id}`, data);
}

export function startCampaign(id: string) {
  return api.post<{ message: string; lead_count: number }>(`/campaigns/${id}/start`);
}

export function pauseCampaign(id: string) {
  return api.post<{ message: string }>(`/campaigns/${id}/pause`);
}

export function deleteCampaign(id: string) {
  return api.delete<void>(`/campaigns/${id}`);
}
