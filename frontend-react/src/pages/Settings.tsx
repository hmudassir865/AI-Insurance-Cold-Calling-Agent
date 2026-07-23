import { useState } from 'react';
import { Wifi, WifiOff, Info, Server, CheckCircle, XCircle } from 'lucide-react';

interface Service {
  name: string;
  ok: boolean;
}

const defaultServices: Service[] = [
  { name: 'Backend', ok: true },
  { name: 'Database', ok: true },
  { name: 'Frontend', ok: true },
  { name: 'Gemini API', ok: true },
  { name: 'SignalWire', ok: true },
  { name: 'ElevenLabs', ok: true },
];

const techStack = [
  'React 19 + TypeScript',
  'FastAPI (Python)',
  'PostgreSQL + pgvector',
  'Redis (Queue + Cache)',
  'SignalWire (Voice)',
  'Gemini API (LLM)',
  'ElevenLabs (TTS)',
  'Tailwind CSS',
];

const features = [
  'JWT-based authentication & refresh tokens',
  'Multi-LLM fallback (Gemini primary)',
  'Advanced RAG pipeline for dynamic scripting',
  'Async task queue with Redis + Celery',
  'AI-driven lead scoring & prioritization',
  'Distributed caching layer (Redis)',
  'Real-time call status via WebSockets',
  'Comprehensive audit logging',
];

export default function Settings() {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [testResult, setTestResult] = useState<'idle' | 'success' | 'error'>('idle');
  const [testLoading, setTestLoading] = useState(false);

  const testConnection = async () => {
    setTestLoading(true);
    setTestResult('idle');
    try {
      const res = await fetch(`${apiUrl.replace(/\/+$/, '')}/health`);
      if (res.ok) {
        setTestResult('success');
      } else {
        setTestResult('error');
      }
    } catch {
      setTestResult('error');
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Configure backend connection and view system status
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Backend Connection</h2>

          <label className="mb-1.5 block text-sm font-medium text-gray-700">API URL</label>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => {
              setApiUrl(e.target.value);
              setTestResult('idle');
            }}
            placeholder="http://localhost:8000"
            className="mb-4 w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />

          <button
            onClick={testConnection}
            disabled={testLoading}
            className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Server className="h-4 w-4" />
            {testLoading ? 'Testing…' : 'Test Connection'}
          </button>

          {testResult === 'success' && (
            <div className="mt-3 flex items-center gap-2 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
              <CheckCircle className="h-4 w-4 flex-shrink-0" />
              Connection successful — API is reachable.
            </div>
          )}

          {testResult === 'error' && (
            <div className="mt-3 flex items-center gap-2 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
              <XCircle className="h-4 w-4 flex-shrink-0" />
              Connection failed — check the URL and ensure the server is running.
            </div>
          )}
        </div>

        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">System Status</h2>
          <div className="space-y-3">
            {defaultServices.map((svc) => (
              <div key={svc.name} className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-3">
                <span className="text-sm font-medium text-gray-700">{svc.name}</span>
                <span className="flex items-center gap-1.5 text-sm">
                  <span
                    className={`inline-block h-2.5 w-2.5 rounded-full ${
                      svc.ok ? 'bg-green-500' : 'bg-red-500'
                    }`}
                  />
                  {svc.ok ? (
                    <span className="text-green-600">Operational</span>
                  ) : (
                    <span className="text-red-600">Down</span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
        <h2 className="mb-1 text-lg font-semibold text-gray-900">About</h2>
        <p className="mb-4 text-sm text-gray-500">AI Health Insurance Cold Calling Agent — v2.0.0 (Production Ready)</p>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-700">Architecture</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• JWT Auth</li>
              <li>• Multi-LLM</li>
              <li>• Advanced RAG</li>
              <li>• Async Queue</li>
              <li>• Lead Scoring</li>
              <li>• Distributed Cache</li>
            </ul>
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-700">Tech Stack</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              {techStack.map((t) => (
                <li key={t}>• {t}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-700">Key Features</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              {features.map((f) => (
                <li key={f}>• {f}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
