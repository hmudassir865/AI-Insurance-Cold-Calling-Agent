import { useState, useEffect } from 'react';
import { Search, RefreshCw, Plus, Upload, Phone, Trash2, Check, ChevronDown, ChevronRight, X } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { listLeads, createLead, updateLead, deleteLead, bulkUploadLeads } from '../api/leads';
import { listCampaigns } from '../api/campaigns';
import { initiateCall } from '../api/calls';
import type { Lead } from '../types';

const LEAD_STATUSES = ['pending', 'interested', 'not_interested', 'callback'];
const LANGUAGES = ['urdu', 'english', 'hindi', 'arabic'];

type Tab = 'all' | 'add' | 'bulk';

interface AlertState {
  type: 'success' | 'error';
  message: string;
}

function Leads() {
  const [activeTab, setActiveTab] = useState<Tab>('all');

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Leads Management</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage, add, and upload leads for your cold calling campaigns
        </p>
      </div>

      <div className="flex gap-1 rounded-lg bg-gray-100 p-1 w-fit">
        {(['all', 'add', 'bulk'] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex items-center gap-1.5 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'all' && <Search className="h-4 w-4" />}
            {tab === 'add' && <Plus className="h-4 w-4" />}
            {tab === 'bulk' && <Upload className="h-4 w-4" />}
            {tab === 'all' ? 'All Leads' : tab === 'add' ? 'Add Lead' : 'Bulk Upload'}
          </button>
        ))}
      </div>

      {activeTab === 'all' && <AllLeadsTab />}
      {activeTab === 'add' && <AddLeadTab />}
      {activeTab === 'bulk' && <BulkUploadTab />}
    </div>
  );
}

function AllLeadsTab() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [alert, setAlert] = useState<AlertState | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState('');
  const [campaignFilter, setCampaignFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [campaigns, setCampaigns] = useState<{ id: string; name: string }[]>([]);

  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [newStatus, setNewStatus] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [callingId, setCallingId] = useState<string | null>(null);

  const fetchLeads = () => {
    setLoading(true);
    setError(null);
    const params: {
      status?: string;
      campaign_id?: string;
      search?: string;
      page_size?: number;
    } = { page_size: 200 };
    if (statusFilter) params.status = statusFilter;
    if (campaignFilter) params.campaign_id = campaignFilter;
    if (searchQuery) params.search = searchQuery;
    listLeads(params)
      .then((res) => {
        setLeads(res.leads);
        setTotal(res.total);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLeads();
  }, [statusFilter, campaignFilter, searchQuery]);

  useEffect(() => {
    listCampaigns()
      .then((res) => setCampaigns(res.campaigns.map((c) => ({ id: c.id, name: c.name }))))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!alert) return;
    const timer = setTimeout(() => setAlert(null), 4000);
    return () => clearTimeout(timer);
  }, [alert]);

  const handleUpdateStatus = (leadId: string) => {
    if (!newStatus) return;
    setUpdatingId(leadId);
    updateLead(leadId, { status: newStatus } as Partial<Lead>)
      .then(() => {
        setLeads((prev) =>
          prev.map((l) => (l.id === leadId ? { ...l, status: newStatus } : l))
        );
        setAlert({ type: 'success', message: 'Lead status updated' });
        setUpdatingId(null);
        setNewStatus('');
        setExpandedId(null);
      })
      .catch((err) => {
        setAlert({ type: 'error', message: err.message });
        setUpdatingId(null);
      });
  };

  const handleDelete = (leadId: string) => {
    setDeletingId(leadId);
    deleteLead(leadId)
      .then(() => {
        setLeads((prev) => prev.filter((l) => l.id !== leadId));
        setTotal((prev) => prev - 1);
        setAlert({ type: 'success', message: 'Lead deleted' });
        setDeletingId(null);
        setExpandedId(null);
      })
      .catch((err) => {
        setAlert({ type: 'error', message: err.message });
        setDeletingId(null);
      });
  };

  const handleCall = (leadId: string) => {
    setCallingId(leadId);
    initiateCall(leadId, campaignFilter || undefined)
      .then(() => {
        setAlert({ type: 'success', message: 'Call initiated' });
        setCallingId(null);
      })
      .catch((err) => {
        setAlert({ type: 'error', message: err.message });
        setCallingId(null);
      });
  };

  return (
    <div className="space-y-4">
      {alert && (
        <div
          className={`flex items-center gap-2 rounded-lg border px-4 py-3 text-sm ${
            alert.type === 'success'
              ? 'border-green-200 bg-green-50 text-green-800'
              : 'border-red-200 bg-red-50 text-red-800'
          }`}
        >
          {alert.type === 'success' ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
          {alert.message}
          <button onClick={() => setAlert(null)} className="ml-auto">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          <X className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value="">All Statuses</option>
          {LEAD_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, ' ')}
            </option>
          ))}
        </select>

        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or phone..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-64 rounded-lg border border-gray-300 py-2 pl-10 pr-3 text-sm text-gray-700 shadow-sm placeholder:text-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>

        <select
          value={campaignFilter}
          onChange={(e) => setCampaignFilter(e.target.value)}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value="">All Campaigns</option>
          {campaigns.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>

        <button
          onClick={fetchLeads}
          className="flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <p className="text-sm text-gray-500">
        Showing {leads.length} of {total} leads
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-20 text-sm text-gray-400">
          Loading...
        </div>
      ) : leads.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-20">
          <Search className="mb-3 h-10 w-10 text-gray-300" />
          <p className="text-sm font-medium text-gray-500">No leads found</p>
          <p className="text-xs text-gray-400">
            Try adjusting your filters or add a new lead
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {leads.map((lead) => {
            const isExpanded = expandedId === lead.id;
            return (
              <div
                key={lead.id}
                className="rounded-xl border border-gray-100 bg-white shadow-sm transition-shadow hover:shadow"
              >
                <button
                  onClick={() => setExpandedId(isExpanded ? null : lead.id)}
                  className="flex w-full items-center gap-3 px-5 py-4 text-left"
                >
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4 shrink-0 text-gray-400" />
                  ) : (
                    <ChevronRight className="h-4 w-4 shrink-0 text-gray-400" />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-gray-900">{lead.name}</p>
                    <p className="truncate text-sm text-gray-500">{lead.phone}</p>
                  </div>
                  <span className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 text-xs font-medium uppercase text-gray-600">
                    {lead.language}
                  </span>
                  <StatusBadge status={lead.status} />
                  <span className="hidden text-xs text-gray-400 sm:block">
                    {new Date(lead.created_at).toLocaleDateString()}
                  </span>
                </button>

                {isExpanded && (
                  <div className="border-t border-gray-100 px-5 py-4 space-y-4">
                    <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
                      <div>
                        <p className="text-xs text-gray-500">Status</p>
                        <p className="text-sm font-medium text-gray-900 capitalize">
                          {lead.status.replace(/_/g, ' ')}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Language</p>
                        <p className="text-sm font-medium text-gray-900 uppercase">
                          {lead.language}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Campaign</p>
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {lead.assigned_campaign_id
                            ? campaigns.find((c) => c.id === lead.assigned_campaign_id)?.name ||
                              lead.assigned_campaign_id.slice(0, 8)
                            : '-'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Created</p>
                        <p className="text-sm font-medium text-gray-900">
                          {new Date(lead.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Lead ID</p>
                        <p className="text-sm font-medium text-gray-900 font-mono text-xs">
                          {lead.id.slice(0, 8)}...
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 border-t border-gray-100 pt-4">
                      <select
                        value={newStatus || lead.status}
                        onChange={(e) => setNewStatus(e.target.value)}
                        className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                      >
                        {LEAD_STATUSES.map((s) => (
                          <option key={s} value={s}>
                            {s.replace(/_/g, ' ')}
                          </option>
                        ))}
                      </select>
                      <button
                        onClick={() => handleUpdateStatus(lead.id)}
                        disabled={updatingId === lead.id || !newStatus || newStatus === lead.status}
                        className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {updatingId === lead.id ? 'Loading...' : <Check className="h-4 w-4" />}
                        Update
                      </button>
                      <button
                        onClick={() => handleCall(lead.id)}
                        disabled={callingId === lead.id}
                        className="flex items-center gap-1.5 rounded-lg border border-green-300 bg-green-50 px-3 py-1.5 text-sm font-medium text-green-700 hover:bg-green-100 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {callingId === lead.id ? 'Loading...' : <Phone className="h-4 w-4" />}
                        Call Now
                      </button>
                      <button
                        onClick={() => handleDelete(lead.id)}
                        disabled={deletingId === lead.id}
                        className="ml-auto flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {deletingId === lead.id ? 'Loading...' : <Trash2 className="h-4 w-4" />}
                        Delete
                      </button>
                    </div>
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

function AddLeadTab() {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [language, setLanguage] = useState('urdu');
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState<AlertState | null>(null);

  useEffect(() => {
    if (!alert) return;
    const timer = setTimeout(() => setAlert(null), 4000);
    return () => clearTimeout(timer);
  }, [alert]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !phone.trim()) return;
    setSubmitting(true);
    createLead(name.trim(), phone.trim(), language)
      .then(() => {
        setAlert({ type: 'success', message: 'Lead created successfully' });
        setName('');
        setPhone('');
        setLanguage('urdu');
      })
      .catch((err) => setAlert({ type: 'error', message: err.message }))
      .finally(() => setSubmitting(false));
  };

  return (
    <div className="max-w-lg rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
      {alert && (
        <div
          className={`mb-4 flex items-center gap-2 rounded-lg border px-4 py-3 text-sm ${
            alert.type === 'success'
              ? 'border-green-200 bg-green-50 text-green-800'
              : 'border-red-200 bg-red-50 text-red-800'
          }`}
        >
          {alert.type === 'success' ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
          {alert.message}
          <button onClick={() => setAlert(null)} className="ml-auto">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Ahmed Khan"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 placeholder:text-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Phone</label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="e.g. +923001234567"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 placeholder:text-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          >
            {LANGUAGES.map((l) => (
              <option key={l} value={l}>
                {l.charAt(0).toUpperCase() + l.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <button
          type="submit"
          disabled={submitting || !name.trim() || !phone.trim()}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting ? 'Loading...' : <Plus className="h-4 w-4" />}
          Create Lead
        </button>
      </form>
    </div>
  );
}

function BulkUploadTab() {
  const [file, setFile] = useState<File | null>(null);
  const [campaignId, setCampaignId] = useState('');
  const [campaigns, setCampaigns] = useState<{ id: string; name: string }[]>([]);
  const [preview, setPreview] = useState<string[][]>([]);
  const [uploading, setUploading] = useState(false);
  const [alert, setAlert] = useState<AlertState | null>(null);

  useEffect(() => {
    listCampaigns()
      .then((res) => setCampaigns(res.campaigns.map((c) => ({ id: c.id, name: c.name }))))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!alert) return;
    const timer = setTimeout(() => setAlert(null), 4000);
    return () => clearTimeout(timer);
  }, [alert]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    const reader = new FileReader();
    reader.onload = () => {
      const text = reader.result as string;
      const lines = text.split('\n').filter(Boolean);
      const rows = lines.slice(0, 6).map((line) => line.split(','));
      setPreview(rows);
    };
    reader.readAsText(f);
  };

  const handleUpload = () => {
    if (!file) return;
    setUploading(true);
    bulkUploadLeads(file, campaignId || undefined)
      .then((res) => {
        setAlert({
          type: 'success',
          message: `Uploaded ${res.total_uploaded} leads${res.errors.length > 0 ? `. Errors: ${res.errors.length}` : ''}`,
        });
        setFile(null);
        setPreview([]);
      })
      .catch((err) => setAlert({ type: 'error', message: err.message }))
      .finally(() => setUploading(false));
  };

  return (
    <div className="max-w-2xl space-y-4">
      {alert && (
        <div
          className={`flex items-center gap-2 rounded-lg border px-4 py-3 text-sm ${
            alert.type === 'success'
              ? 'border-green-200 bg-green-50 text-green-800'
              : 'border-red-200 bg-red-50 text-red-800'
          }`}
        >
          {alert.type === 'success' ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
          {alert.message}
          <button onClick={() => setAlert(null)} className="ml-auto">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">CSV File</label>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="w-full text-sm text-gray-500 file:mr-4 file:cursor-pointer file:rounded-lg file:border-0 file:bg-brand-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-brand-700 hover:file:bg-brand-100"
            />
            <p className="mt-1 text-xs text-gray-400">
              CSV must include headers: name, phone, language (optional)
            </p>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Campaign (optional)
            </label>
            <select
              value={campaignId}
              onChange={(e) => setCampaignId(e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="">No campaign</option>
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {preview.length > 0 && (
        <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-gray-900">Preview</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  {preview[0]?.map((header, i) => (
                    <th key={i} className="px-3 py-2 font-medium text-gray-600 capitalize">
                      {header.trim()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.slice(1).map((row, ri) => (
                  <tr key={ri} className="border-b border-gray-100 last:border-0">
                    {row.map((cell, ci) => (
                      <td key={ci} className="px-3 py-2 text-gray-700">
                        {cell.trim()}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-gray-400">
            Showing up to 5 rows
          </p>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50 sm:w-fit"
      >
        {uploading ? 'Loading...' : <Upload className="h-4 w-4" />}
        Upload Leads
      </button>
    </div>
  );
}

export default Leads;
