import { useState, useEffect, useCallback } from 'react';
import { Search, RefreshCw, Phone, Clock, AlertCircle, MessageSquare, ChevronDown, ChevronRight } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { getCallHistory } from '../api/calls';
import { useWebSocket } from '../hooks/useWebSocket';
import type { CallLog } from '../types';

interface Filters {
  status: string;
  lead_id: string;
}

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
    </div>
  );
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '—';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function CallHistory() {
  const [filters, setFilters] = useState<Filters>({ status: '', lead_id: '' });
  const [calls, setCalls] = useState<CallLog[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const fetchHistory = useCallback(() => {
    setLoading(true);
    setError('');
    getCallHistory({
      status: filters.status || undefined,
      lead_id: filters.lead_id || undefined,
    })
      .then((res) => {
        setCalls(res.call_logs);
        setTotal(res.total);
      })
      .catch(() => setError('Failed to load call history.'))
      .finally(() => setLoading(false));
  }, [filters.status, filters.lead_id]);

  useEffect(() => {
    fetchHistory();
  }, [filters.status, filters.lead_id]);

  useWebSocket(useCallback((msg) => {
    if (msg.event === 'call_status' || msg.event === 'transcript') {
      fetchHistory();
    }
  }, [fetchHistory]));

  const toggleExpanded = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const statuses = ['', 'completed', 'failed', 'no-answer', 'busy', 'initiated'];

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Call History</h1>
        <p className="mt-1 text-sm text-gray-500">
          Review past calls, transcripts, and AI summaries
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <select
          value={filters.status}
          onChange={(e) => setFilters((prev) => ({ ...prev, status: e.target.value }))}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value="">All</option>
          {statuses.filter(Boolean).map((s) => (
            <option key={s} value={s}>
              {s.charAt(0).toUpperCase() + s.slice(1).replace(/-/g, ' ')}
            </option>
          ))}
        </select>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by Lead ID"
            value={filters.lead_id}
            onChange={(e) => setFilters((prev) => ({ ...prev, lead_id: e.target.value }))}
            className="w-56 rounded-lg border border-gray-300 bg-white py-2 pl-10 pr-3 text-sm text-gray-900 placeholder-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>

        <button
          onClick={fetchHistory}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      <p className="text-sm text-gray-500">
        Showing {calls.length} of {total} calls
      </p>

      {loading && <LoadingSpinner />}

      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {!loading && !error && calls.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400">
          <Phone className="mb-3 h-12 w-12" />
          <p className="text-lg font-medium">No calls found</p>
          <p className="text-sm">Try adjusting your filters or make your first call.</p>
        </div>
      )}

      {!loading && !error && calls.length > 0 && (
        <div className="space-y-4">
          {calls.map((call) => {
            const isOpen = expanded.has(call.id);
            const truncated = call.lead_id.length > 8 ? call.lead_id.slice(0, 8) + '…' : call.lead_id;

            return (
              <div
                key={call.id}
                className="rounded-xl border border-gray-100 bg-white shadow-sm transition-shadow hover:shadow-md"
              >
                <button
                  onClick={() => toggleExpanded(call.id)}
                  className="flex w-full items-center gap-4 px-5 py-4 text-left"
                >
                  <div className="flex-shrink-0 text-gray-400">
                    {isOpen ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
                  </div>

                  <div className="flex min-w-0 flex-1 items-center gap-4">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Clock className="h-4 w-4" />
                      {formatDate(call.created_at)}
                    </div>

                    <span className="font-mono text-sm font-medium text-gray-900">
                      {truncated}
                    </span>

                    <div className="flex items-center gap-1 text-sm text-gray-500">
                      <Phone className="h-4 w-4" />
                      {formatDuration(call.duration_seconds)}
                    </div>

                    <StatusBadge status={call.status} />
                  </div>

                  <div className="flex-shrink-0 text-sm text-gray-500">
                    {call.sentiment_score !== null ? (
                      <span>{call.sentiment_score.toFixed(2)}</span>
                    ) : (
                      <span className="text-gray-300">—</span>
                    )}
                  </div>
                </button>

                {isOpen && (
                  <div className="border-t border-gray-100 px-5 py-4 space-y-4">
                    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                      <div>
                        <p className="text-xs text-gray-500">Duration</p>
                        <p className="text-sm font-medium text-gray-900">{formatDuration(call.duration_seconds)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Sentiment</p>
                        <p className="text-sm font-medium text-gray-900">
                          {call.sentiment_score !== null ? call.sentiment_score.toFixed(2) : '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Lead Status</p>
                        <p className="text-sm font-medium text-gray-900 capitalize">
                          {call.lead_status ?? '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Call Status</p>
                        <p className="text-sm font-medium text-gray-900 capitalize">
                          {call.status.replace(/_/g, ' ')}
                        </p>
                      </div>
                    </div>

                    {call.summary && (
                      <div className="flex gap-3 rounded-lg bg-blue-50 p-4 text-sm text-blue-800">
                        <MessageSquare className="mt-0.5 h-4 w-4 flex-shrink-0" />
                        <p>{call.summary}</p>
                      </div>
                    )}

                    {call.transcript && call.transcript.length > 0 && (
                      <div className="space-y-2">
                        {call.transcript.map((entry, idx) => {
                          const isAi = entry.role === 'assistant';
                          return (
                            <div
                              key={idx}
                              className={`flex gap-3 rounded-lg p-3 text-sm ${
                                isAi
                                  ? 'border-l-4 border-blue-400 bg-blue-50'
                                  : 'border-l-4 border-green-400 bg-green-50'
                              }`}
                            >
                              <span className="flex-shrink-0 font-medium">
                                {isAi ? '🤖 AI' : '👤 Customer'}
                              </span>
                              <p className="text-gray-700">{entry.content}</p>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {call.error_message && (
                      <div className="flex items-start gap-2 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                        <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
                        <p>{call.error_message}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
