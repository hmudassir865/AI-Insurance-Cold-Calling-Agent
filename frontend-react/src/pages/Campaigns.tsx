import { useState, useEffect } from 'react';
import { Play, Pause, Phone, Trash2, Plus, RefreshCw, FileText, ChevronDown, ChevronRight } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import {
  listCampaigns,
  createCampaign,
  startCampaign,
  pauseCampaign,
  deleteCampaign,
  updateCampaign,
} from '../api/campaigns';
import { getCampaignAnalytics } from '../api/analytics';
import { initiateCall } from '../api/calls';
import { listLeads } from '../api/leads';
import type { Campaign } from '../types';

const DEFAULT_SCRIPT = `Assalam-o-Alaikum! Main [Company Name] se health insurance ke baare mein baat kar raha hoon.
Aapke liye ek special health insurance plan hai jo aapko har tarah ki medical emergency mein cover karta hai.
Kya aap is baare mein mazeed jaanna chahenge?`;

interface CampaignForm {
  name: string;
  greeting_message: string;
  closing_message: string;
  script_template: string;
}

interface Alert {
  type: 'success' | 'error';
  message: string;
}

const emptyForm: CampaignForm = {
  name: '',
  greeting_message: '',
  closing_message: '',
  script_template: DEFAULT_SCRIPT,
};

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState<Alert | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'new'>('all');
  const [statusFilter, setStatusFilter] = useState('All');
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());
  const [form, setForm] = useState<CampaignForm>(emptyForm);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  useEffect(() => {
    if (!alert) return;
    const t = setTimeout(() => setAlert(null), 5000);
    return () => clearTimeout(t);
  }, [alert]);

  const fetchCampaigns = async () => {
    setLoading(true);
    try {
      const data = await listCampaigns();
      setCampaigns(data.campaigns);
    } catch {
      setAlert({ type: 'error', message: 'Failed to load campaigns' });
    } finally {
      setLoading(false);
    }
  };

  const showAlert = (type: 'success' | 'error', message: string) => {
    setAlert({ type, message });
  };

  const toggleExpand = (id: string) => {
    setExpandedCards((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const filteredCampaigns =
    statusFilter === 'All'
      ? campaigns
      : campaigns.filter((c) => c.status === statusFilter);

  const handleCreate = async () => {
    if (!form.name.trim()) {
      showAlert('error', 'Campaign name is required');
      return;
    }
    setSubmitting(true);
    try {
      await createCampaign(form);
      showAlert('success', 'Campaign created successfully');
      setForm(emptyForm);
      setActiveTab('all');
      await fetchCampaigns();
    } catch {
      showAlert('error', 'Failed to create campaign');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStart = async (id: string) => {
    try {
      await startCampaign(id);
      showAlert('success', 'Campaign started');
      await fetchCampaigns();
    } catch {
      showAlert('error', 'Failed to start campaign');
    }
  };

  const handlePause = async (id: string) => {
    try {
      await pauseCampaign(id);
      showAlert('success', 'Campaign paused');
      await fetchCampaigns();
    } catch {
      showAlert('error', 'Failed to pause campaign');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this campaign?')) return;
    try {
      await deleteCampaign(id);
      showAlert('success', 'Campaign deleted');
      await fetchCampaigns();
    } catch {
      showAlert('error', 'Failed to delete campaign');
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await updateCampaign(id, { status } as Partial<Campaign>);
      showAlert('success', `Status changed to ${status}`);
      await fetchCampaigns();
    } catch {
      showAlert('error', 'Failed to update status');
    }
  };

  const handleTestCall = async (campaignId: string) => {
    try {
      const leads = await listLeads({ campaign_id: campaignId, status: 'pending', page_size: 1 });
      if (leads.leads.length === 0) {
        showAlert('error', 'No pending leads found for this campaign');
        return;
      }
      await initiateCall(leads.leads[0].id);
      showAlert('success', 'Test call initiated: OK');
    } catch {
      showAlert('error', 'Test call failed');
    }
  };

  const handleFormChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  // --- Loading ---
  if (loading && campaigns.length === 0) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Alert */}
      {alert && (
        <div
          className={`px-4 py-3 rounded-lg text-sm font-medium ${
            alert.type === 'success'
              ? 'bg-green-100 text-green-800 border border-green-200'
              : 'bg-red-100 text-red-800 border border-red-200'
          }`}
        >
          {alert.message}
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
        <p className="text-sm text-gray-500 mt-1">
          Manage your cold calling campaigns, track performance, and launch new ones.
        </p>
      </div>

      {/* Tab switcher */}
      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('all')}
          className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'all'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          All Campaigns
        </button>
        <button
          onClick={() => setActiveTab('new')}
          className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'new'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          New Campaign
        </button>
      </div>

      {/* ===== All Campaigns Tab ===== */}
      {activeTab === 'all' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <label className="text-sm font-medium text-gray-700">Status:</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="All">All</option>
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <button
              onClick={fetchCampaigns}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {/* Campaign Cards */}
          {filteredCampaigns.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-dashed border-gray-300">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 font-medium">No campaigns found</p>
              <p className="text-sm text-gray-400 mt-1">
                {statusFilter === 'All'
                  ? 'Create your first campaign to get started.'
                  : `No campaigns with status "${statusFilter}".`}
              </p>
              {statusFilter === 'All' && (
                <button
                  onClick={() => setActiveTab('new')}
                  className="mt-4 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4" />
                  New Campaign
                </button>
              )}
            </div>
          ) : (
            <div className="grid gap-4">
              {filteredCampaigns.map((campaign) => {
                const isExpanded = expandedCards.has(campaign.id);
                const stats = {
                  total_leads: campaign.total_leads,
                  processed_leads: campaign.processed_leads,
                  total_calls: campaign.total_calls ?? 0,
                  conversion_rate: campaign.conversion_rate ?? 0,
                  avg_sentiment: campaign.avg_sentiment ?? 0,
                };
                const pendingLeads = campaign.total_leads - campaign.processed_leads;

                return (
                  <div
                    key={campaign.id}
                    className="bg-white border border-gray-200 rounded-xl shadow-sm p-5 space-y-4"
                  >
                    {/* Campaign Name + Status */}
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-bold text-gray-900">{campaign.name}</h3>
                      <StatusBadge status={campaign.status} />
                    </div>

                    {/* Stats Row */}
                    <div className="grid grid-cols-4 gap-4">
                      <div className="bg-gray-50 rounded-lg p-3 text-center">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Leads</p>
                        <p className="text-lg font-semibold text-gray-800">
                          {stats.processed_leads}/{stats.total_leads}
                        </p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 text-center">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Calls</p>
                        <p className="text-lg font-semibold text-gray-800">{stats.total_calls}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 text-center">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Conv. %</p>
                        <p className="text-lg font-semibold text-gray-800">
                          {stats.conversion_rate.toFixed(1)}%
                        </p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 text-center">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Sentiment</p>
                        <p className="text-lg font-semibold text-gray-800">
                          {stats.avg_sentiment.toFixed(2)}
                        </p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center flex-wrap gap-2">
                      {campaign.status === 'draft' && (
                        <button
                          onClick={() => handleStart(campaign.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                        >
                          <Play className="w-4 h-4" />
                          Start
                        </button>
                      )}
                      {campaign.status === 'active' && (
                        <button
                          onClick={() => handlePause(campaign.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-amber-500 rounded-lg hover:bg-amber-600"
                        >
                          <Pause className="w-4 h-4" />
                          Pause
                        </button>
                      )}
                      {pendingLeads > 0 && (
                        <button
                          onClick={() => handleTestCall(campaign.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100"
                        >
                          <Phone className="w-4 h-4" />
                          Test Call
                        </button>
                      )}

                      {/* Status change select */}
                      <select
                        defaultValue=""
                        onChange={(e) => {
                          if (e.target.value) handleStatusChange(campaign.id, e.target.value);
                          e.target.value = "";
                        }}
                        className="ml-auto border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="" disabled>
                          Change status...
                        </option>
                        <option value="draft">Draft</option>
                        <option value="active">Active</option>
                        <option value="paused">Paused</option>
                        <option value="completed">Completed</option>
                      </select>

                      <button
                        onClick={() => handleDelete(campaign.id)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100"
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </button>
                    </div>

                    {/* Script Preview - Expandable */}
                    <div>
                      <button
                        onClick={() => toggleExpand(campaign.id)}
                        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
                      >
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        )}
                        Script Preview
                      </button>
                      {isExpanded && (
                        <pre className="mt-2 p-4 bg-gray-900 text-green-400 text-sm font-mono rounded-lg overflow-x-auto whitespace-pre-wrap max-h-48 overflow-y-auto">
                          {campaign.script_template || 'No script template set.'}
                        </pre>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ===== New Campaign Tab ===== */}
      {activeTab === 'new' && (
        <div className="max-w-2xl bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Campaign Name
            </label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleFormChange}
              placeholder="e.g. Q4 Health Insurance Outreach"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Greeting Message
            </label>
            <input
              type="text"
              name="greeting_message"
              value={form.greeting_message}
              onChange={handleFormChange}
              placeholder="Assalam-o-Alaikum! Main [Company Name] se bol raha hoon."
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Closing Message
            </label>
            <input
              type="text"
              name="closing_message"
              value={form.closing_message}
              onChange={handleFormChange}
              placeholder="Thank you for your time! Have a great day."
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Script Template
            </label>
            <textarea
              name="script_template"
              rows={12}
              value={form.script_template}
              onChange={handleFormChange}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            onClick={handleCreate}
            disabled={submitting}
            className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            {submitting ? 'Creating...' : 'Create Campaign'}
          </button>
        </div>
      )}
    </div>
  );
}
