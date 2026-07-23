import { api } from './client';
import type { Lead } from '../types';

export function listLeads(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  campaign_id?: string;
  search?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.campaign_id) searchParams.set('campaign_id', params.campaign_id);
  if (params?.search) searchParams.set('search', params.search);
  if (params?.page) searchParams.set('page', String(params.page));
  if (params?.page_size) searchParams.set('page_size', String(params.page_size));
  const qs = searchParams.toString();
  return api.get<{ total: number; leads: Lead[] }>(`/leads${qs ? `?${qs}` : ''}`);
}

export function getLead(id: string) {
  return api.get<Lead>(`/leads/${id}`);
}

export function createLead(name: string, phone: string, language = 'urdu') {
  return api.post<Lead>('/leads', { name, phone, language });
}

export function updateLead(id: string, data: Partial<Lead>) {
  return api.patch<Lead>(`/leads/${id}`, data);
}

export function deleteLead(id: string) {
  return api.delete<void>(`/leads/${id}`);
}

export function bulkUploadLeads(file: File, campaignId?: string) {
  const formData = new FormData();
  formData.append('file', file);
  if (campaignId) formData.append('campaign_id', campaignId);
  return api.upload<{ total_uploaded: number; errors: string[] }>('/leads/bulk-upload', formData);
}
