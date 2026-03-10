import { useEffect, useMemo, useState } from 'react';

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080').replace(/\/$/, '');

function buildLegacyUiUrl(baseUrl) {
  const url = new URL(baseUrl);
  url.searchParams.set('ui', 'v2');
  return url.toString();
}

export default function App() {
  const [health, setHealth] = useState({ status: 'checking', service: null, error: null, updatedAt: null });

  const legacyUiUrl = useMemo(() => buildLegacyUiUrl(apiBaseUrl), []);

  useEffect(() => {
    let mounted = true;

    const checkHealth = async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/health`);
        if (!res.ok) throw new Error(`health ${res.status}`);
        const data = await res.json();
        if (!mounted) return;
        setHealth({
          status: data?.status || 'ok',
          service: data?.service || null,
          error: null,
          updatedAt: new Date().toISOString(),
        });
      } catch (err) {
        if (!mounted) return;
        setHealth({
          status: 'down',
          service: null,
          error: err?.message || 'backend indisponible',
          updatedAt: new Date().toISOString(),
        });
      }
    };

    checkHealth();
    const timer = setInterval(checkHealth, 10000);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  return (
    <main style={{ margin: 0, padding: 0, fontFamily: 'Arial, sans-serif' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 12px',
          borderBottom: '1px solid #d1d5db',
          background: '#f8fafc',
          color: '#334155',
          fontSize: 13,
        }}
      >
        <span>
          UI legacy backend (source de vérité): <code>{legacyUiUrl}</code>
        </span>
        <span>
          Backend: <strong>{health.status}</strong>
          {health.service ? ` · ${health.service}` : ''}
          {health.updatedAt ? ` · ${new Date(health.updatedAt).toLocaleTimeString('fr-FR')}` : ''}
          {health.error ? ` · erreur: ${health.error}` : ''}
        </span>
      </div>

      <iframe
        title="Audiobook Manager Legacy UI"
        src={legacyUiUrl}
        style={{ width: '100%', height: 'calc(100vh - 42px)', border: 0, display: 'block' }}
        allow="clipboard-read; clipboard-write"
      />
    </main>
  );
}
