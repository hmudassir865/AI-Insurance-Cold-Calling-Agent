export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Lead {
  id: string;
  name: string;
  phone: string;
  language: string;
  status: string;
  extra_data: Record<string, unknown> | null;
  assigned_campaign_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Campaign {
  id: string;
  name: string;
  script_template: string;
  greeting_message: string | null;
  closing_message: string | null;
  status: string;
  total_leads: number;
  processed_leads: number;
  total_calls?: number;
  conversion_rate?: number;
  avg_sentiment?: number;
  created_at: string;
  updated_at: string;
}

export interface CallLog {
  id: string;
  lead_id: string;
  campaign_id: string | null;
  duration_seconds: number | null;
  status: string;
  transcript: TranscriptEntry[] | null;
  summary: string | null;
  sentiment_score: number | null;
  lead_status: string | null;
  recording_path: string | null;
  error_message: string | null;
  created_at: string;
}

export interface TranscriptEntry {
  role: 'user' | 'assistant';
  content: string;
}

export interface DashboardData {
  total_calls: number;
  total_leads: number;
  conversion_rate: number;
  avg_call_duration_seconds: number;
  avg_sentiment_score: number;
  lead_breakdown: Record<string, number>;
  daily_stats: DailyStat[];
}

export interface DailyStat {
  date: string;
  calls: number;
  avg_duration: number;
  avg_sentiment: number;
}
