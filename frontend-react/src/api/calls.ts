import { api } from './client';
import type { CallLog } from '../types';

export function initiateCall(leadId: string, campaignId?: string) {
  const params = new URLSearchParams({ lead_id: leadId });
  if (campaignId) params.set('campaign_id', campaignId);
  return api.post<{ call_sid: string; call_log_id: string }>(`/calls/initiate?${params}`);
}

export function getCallHistory(params?: {
  lead_id?: string;
  campaign_id?: string;
  status?: string;
  page?: number;
  page_size?: number;
}) {
  const searchParams = new URLSearchParams();
  if (params?.lead_id) searchParams.set('lead_id', params.lead_id);
  if (params?.campaign_id) searchParams.set('campaign_id', params.campaign_id);
  if (params?.status) searchParams.set('status', params.status);
  if (params?.page) searchParams.set('page', String(params.page));
  if (params?.page_size) searchParams.set('page_size', String(params.page_size));
  const qs = searchParams.toString();
  return api.get<{ total: number; call_logs: CallLog[] }>(`/calls/history${qs ? `?${qs}` : ''}`);
}

export function testLocalCall(leadId: string) {
  return api.post<{ greeting: string; audio_url: string; call_log_id: string }>(
    `/calls/test-local/${leadId}`
  );
}

export function testProcessSpeech(callLogId: string, text: string) {
  return api.post<{ ai_response: string; audio_url: string; completed: boolean }>(
    `/calls/test-process-speech?call_log_id=${callLogId}&text=${encodeURIComponent(text)}`
  );
}
