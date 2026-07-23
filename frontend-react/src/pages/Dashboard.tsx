import { useState, useEffect, useCallback, useRef } from 'react';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { Phone, Users, TrendingUp, Clock, Smile, Play, Send, Volume2 } from 'lucide-react';
import { getDashboard } from '../api/analytics';
import { listLeads } from '../api/leads';
import { testLocalCall, testProcessSpeech } from '../api/calls';
import { useWebSocket } from '../hooks/useWebSocket';
import type { DashboardData, Lead } from '../types';

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
}

function MetricCard({ title, value, icon }: MetricCardProps) {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
      <div className="rounded-lg bg-brand-50 p-3 text-brand-600">
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  );
}

const STATUS_COLORS: Record<string, string> = {
  new: '#3b82f6',
  contacted: '#8b5cf6',
  qualified: '#f59e0b',
  converted: '#10b981',
  lost: '#ef4444',
};

const STATUS_LABELS: Record<string, string> = {
  new: 'New',
  contacted: 'Contacted',
  qualified: 'Qualified',
  converted: 'Converted',
  lost: 'Lost',
};

export default function Dashboard() {
  const [days, setDays] = useState(7);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedLeadId, setSelectedLeadId] = useState('');
  const [callLogId, setCallLogId] = useState('');
  const [conversation, setConversation] = useState<{ role: string; text: string }[]>([]);
  const [userInput, setUserInput] = useState('');
  const [testLoading, setTestLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    getDashboard(days).then(setData).finally(() => setLoading(false));
  }, [days]);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    listLeads({ page_size: 50 }).then((res) => {
      setLeads(res.leads || []);
      if (res.leads?.length > 0) setSelectedLeadId(res.leads[0].id);
    }).catch(() => {});
  }, []);

  const handleStartTest = async () => {
    if (!selectedLeadId) return;
    setTestLoading(true);
    setConversation([]);
    setCallLogId('');
    try {
      const res = await testLocalCall(selectedLeadId);
      setCallLogId(res.call_log_id);
      setConversation([{ role: 'ai', text: res.greeting }]);
      if (audioRef.current) { audioRef.current.src = res.audio_url; audioRef.current.play().catch(() => {}); }
    } catch { /* ignore */ }
    setTestLoading(false);
  };

  const handleSendMessage = async () => {
    if (!callLogId || !userInput.trim()) return;
    const text = userInput.trim();
    setUserInput('');
    setConversation((c) => [...c, { role: 'user', text }]);
    try {
      const res = await testProcessSpeech(callLogId, text);
      setConversation((c) => [...c, { role: 'ai', text: res.ai_response }]);
      if (audioRef.current) { audioRef.current.src = res.audio_url; audioRef.current.play().catch(() => {}); }
    } catch { /* ignore */ }
  };

  useWebSocket(useCallback((msg) => {
    if (msg.event === 'call_status') fetchData();
  }, [fetchData]));

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
  };

  const formatPercent = (value: number) => `${value.toFixed(1)}%`;

  if (loading) return <LoadingSpinner />;

  const leadBreakdown = data?.lead_breakdown
    ? Object.entries(data.lead_breakdown).map(([status, count]) => ({
        status,
        label: STATUS_LABELS[status] || status,
        count,
        color: STATUS_COLORS[status] || '#6b7280',
      }))
    : [];

  const totalLeads = leadBreakdown.reduce((sum, item) => sum + item.count, 0);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time overview of your cold calling campaigns
          </p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {data ? (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <MetricCard
              title="Total Calls"
              value={data.total_calls.toLocaleString()}
              icon={<Phone className="h-5 w-5" />}
            />
            <MetricCard
              title="Total Leads"
              value={data.total_leads.toLocaleString()}
              icon={<Users className="h-5 w-5" />}
            />
            <MetricCard
              title="Conversion Rate"
              value={formatPercent(data.conversion_rate)}
              icon={<TrendingUp className="h-5 w-5" />}
            />
            <MetricCard
              title="Avg Duration"
              value={formatDuration(data.avg_call_duration_seconds)}
              icon={<Clock className="h-5 w-5" />}
            />
            <MetricCard
              title="Avg Sentiment"
              value={data.avg_sentiment_score.toFixed(2)}
              icon={<Smile className="h-5 w-5" />}
            />
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-gray-900">
                Lead Status Breakdown
              </h2>
              {leadBreakdown.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={leadBreakdown} layout="vertical" margin={{ left: 80 }}>
                    <XAxis type="number" tick={{ fontSize: 12 }} />
                    <YAxis
                      type="category"
                      dataKey="label"
                      tick={{ fontSize: 12 }}
                      width={80}
                    />
                    <Tooltip
                      formatter={(value: number) => [value.toLocaleString(), 'Leads']}
                    />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {leadBreakdown.map((entry) => (
                        <Cell key={entry.status} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="py-12 text-center text-sm text-gray-400">
                  No lead data available
                </p>
              )}
            </div>

            <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-gray-900">
                Daily Call Activity
              </h2>
              {data.daily_stats && data.daily_stats.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.daily_stats} margin={{ left: 0 }}>
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11 }}
                      tickFormatter={(d) => {
                        const date = new Date(d);
                        return `${date.getMonth() + 1}/${date.getDate()}`;
                      }}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      labelFormatter={(d) => new Date(d).toLocaleDateString()}
                      formatter={(value: number, name: string) => [
                        value,
                        name === 'calls' ? 'Calls' : name,
                      ]}
                    />
                    <Line
                      type="monotone"
                      dataKey="calls"
                      stroke="#2563eb"
                      strokeWidth={2}
                      dot={{ r: 3, fill: '#2563eb' }}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p className="py-12 text-center text-sm text-gray-400">
                  No daily activity data available
                </p>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">
              Lead Status Progress
            </h2>
            {leadBreakdown.length > 0 ? (
              <div className="space-y-4">
                {leadBreakdown.map((item) => {
                  const pct = totalLeads > 0 ? (item.count / totalLeads) * 100 : 0;
                  return (
                    <div key={item.status}>
                      <div className="mb-1 flex items-center justify-between text-sm">
                        <span className="font-medium text-gray-700">{item.label}</span>
                        <span className="text-gray-500">
                          {item.count} ({pct.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-gray-100">
                        <div
                          className="h-2 rounded-full transition-all duration-500"
                          style={{ width: `${pct}%`, backgroundColor: item.color }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="py-4 text-center text-sm text-gray-400">
                No lead data available
              </p>
            )}
          </div>
        </>
      ) : (
        <p className="py-20 text-center text-gray-400">
          No dashboard data available.
        </p>
      )}

      <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Test Call (Voice AI)</h2>
        <div className="flex items-center gap-3 mb-4">
          <select
            value={selectedLeadId}
            onChange={(e) => setSelectedLeadId(e.target.value)}
            className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none"
          >
            {leads.map((l) => (
              <option key={l.id} value={l.id}>{l.name} ({l.phone})</option>
            ))}
          </select>
          <button
            onClick={handleStartTest}
            disabled={testLoading || !selectedLeadId}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            <Play className="h-4 w-4" /> {testLoading ? 'Starting...' : 'Start Test Call'}
          </button>
        </div>

        {conversation.length > 0 && (
          <div className="space-y-3 mb-4 max-h-60 overflow-y-auto border rounded-lg p-3 bg-gray-50">
            {conversation.map((entry, i) => (
              <div key={i} className={`flex ${entry.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${entry.role === 'user' ? 'bg-brand-600 text-white' : 'bg-white border border-gray-200 text-gray-800'}`}>
                  {entry.text}
                </div>
              </div>
            ))}
          </div>
        )}

        {callLogId && (
          <div className="flex items-center gap-2">
            <input
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type your response..."
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none"
            />
            <button
              onClick={handleSendMessage}
              disabled={!userInput.trim()}
              className="inline-flex items-center gap-1 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              <Send className="h-4 w-4" /> Send
            </button>
            <Volume2 className="h-5 w-5 text-gray-400" title="Audio plays automatically" />
          </div>
        )}
        <audio ref={audioRef} className="hidden" />
      </div>
    </div>
  );
}
