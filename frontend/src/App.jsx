import { useCallback, useEffect, useMemo, useState } from 'react';

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080').replace(/\/$/, '');
const MAX_EVENTS = 12;

function formatDate(value) {
  if (!value) return '—';
  const parsed = typeof value === 'number' ? new Date(value * 1000) : new Date(value);
  if (Number.isNaN(parsed.getTime())) return '—';
  return parsed.toLocaleString('fr-FR');
}

export default function App() {
  const [jobs, setJobs] = useState({ pending: [], running: [], done: [], events: [], review: [] });
  const [recovery, setRecovery] = useState(null);
  const [connected, setConnected] = useState(false);
  const [lastEventId, setLastEventId] = useState(0);
  const [lastSyncAt, setLastSyncAt] = useState(null);
  const [error, setError] = useState('');

  const refreshFromApi = useCallback(async () => {
    const [jobsRes, recoveryRes] = await Promise.all([
      fetch(`${apiBaseUrl}/api/jobs`),
      fetch(`${apiBaseUrl}/api/recovery/status`),
    ]);

    if (!jobsRes.ok) throw new Error(`API jobs en échec (${jobsRes.status})`);

    const jobsData = await jobsRes.json();
    setJobs((prev) => ({ ...prev, ...jobsData }));

    if (recoveryRes.ok) {
      const recoveryData = await recoveryRes.json();
      setRecovery(recoveryData);
    }

    setLastSyncAt(new Date().toISOString());
  }, []);

  useEffect(() => {
    let mounted = true;

    refreshFromApi().catch((err) => {
      if (mounted) setError(err.message || 'Erreur de synchronisation initiale');
    });

    const polling = setInterval(() => {
      refreshFromApi().catch((err) => {
        if (mounted) setError(err.message || 'Erreur de rafraîchissement');
      });
    }, 10000);

    return () => {
      mounted = false;
      clearInterval(polling);
    };
  }, [refreshFromApi]);

  useEffect(() => {
    const url = new URL(`${apiBaseUrl}/api/events/stream`);
    if (lastEventId > 0) url.searchParams.set('since_id', String(lastEventId));

    const source = new EventSource(url.toString());

    source.onopen = () => {
      setConnected(true);
      setError('');
    };

    source.onmessage = (evt) => {
      const id = Number(evt.lastEventId || 0);
      if (id > 0) setLastEventId(id);

      try {
        const parsed = JSON.parse(evt.data || '{}');
        const payload = parsed.payload || parsed;
        const normalizedEvent = {
          id: id || parsed.id || Date.now(),
          stage: payload.stage || parsed.event_type || 'Mise à jour',
          message: payload.message || JSON.stringify(payload),
          folder: payload.folder || parsed.aggregate_id || '—',
          timestamp: payload.timestamp || parsed.created_at || new Date().toISOString(),
        };
        setJobs((prev) => ({ ...prev, events: [normalizedEvent, ...(prev.events || [])].slice(0, MAX_EVENTS) }));
      } catch {
        // ignore malformed events
      }

      refreshFromApi().catch((err) => setError(err.message || 'Erreur de synchronisation'));
    };

    source.onerror = () => setConnected(false);

    return () => {
      source.close();
      setConnected(false);
    };
  }, [lastEventId, refreshFromApi]);

  const kpis = useMemo(() => {
    const pending = jobs.pending?.length || 0;
    const running = jobs.running?.length || 0;
    const done = jobs.done?.length || 0;
    const failed = (jobs.done || []).filter((job) => job.status === 'failed').length;
    const review = jobs.review?.length || 0;

    return { pending, running, done, failed, review };
  }, [jobs]);

  return (
    <>
      <style>{`
        :root { --bg:#f5f7fb; --card:#fff; --text:#1f2937; --muted:#6b7280; --border:#d1d5db; --primary:#4f46e5; --danger:#b91c1c; }
        body { margin:0; background:var(--bg); color:var(--text); }
        .app-shell { display:flex; min-height:100vh; font-family:Arial,sans-serif; }
        .sidebar { width:250px; background:#0f172a; color:#fff; padding:18px 10px; }
        .brand { font-size:18px; font-weight:700; margin:4px 10px 16px; }
        .tab { width:100%; text-align:left; margin:0 0 6px; border:0; padding:9px 10px; border-radius:8px; background:#1e293b; color:#e2e8f0; }
        .tab.active { background:#2563eb; color:#fff; }
        .app-main { flex:1; min-width:0; }
        .topbar { background:#e5e7eb; border-bottom:1px solid #cbd5e1; padding:10px 20px; display:flex; justify-content:space-between; align-items:center; }
        .topbar h1 { margin:0; font-size:24px; }
        .meta { color:#475569; font-size:13px; }
        .live { font-size:12px; border-radius:999px; padding:4px 10px; border:1px solid; }
        .live.ok { color:#059669; border-color:#059669; background:#ecfdf5; }
        .live.off { color:#d97706; border-color:#d97706; background:#fffbeb; }
        .content { padding:18px 20px 40px; }
        .kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin-bottom:14px; }
        .kpi-card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px; }
        .kpi-title { margin:0 0 8px; color:var(--muted); text-transform:uppercase; font-size:12px; }
        .kpi-value { margin:0; font-size:30px; font-weight:700; }
        .card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px; margin-bottom:14px; }
        table { width:100%; border-collapse:collapse; }
        th,td { border-bottom:1px solid var(--border); text-align:left; padding:8px; font-size:14px; }
        .error { color:var(--danger); }
      `}</style>

      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">Audiobook Manager</div>
          <button className="tab active" type="button">📚 Dashboard bibliothèque</button>
          <button className="tab" type="button">⚙️ Traitements</button>
          <button className="tab" type="button">📦 Paquets</button>
          <button className="tab" type="button">🧩 Plugins</button>
          <button className="tab" type="button">🛠️ Configuration</button>
        </aside>

        <div className="app-main">
          <header className="topbar">
            <div>
              <h1>Audiobook Manager</h1>
              <div className="meta">Dernière vue: {formatDate(lastSyncAt)}</div>
            </div>
            <span className={`live ${connected ? 'ok' : 'off'}`}>
              Live sync: {connected ? 'connecté' : 'reconnexion…'}
            </span>
          </header>

          <main className="content">
            <section className="kpi-grid">
              <article className="kpi-card"><p className="kpi-title">Jobs en cours</p><p className="kpi-value">{kpis.running}</p></article>
              <article className="kpi-card"><p className="kpi-title">En attente</p><p className="kpi-value">{kpis.pending}</p></article>
              <article className="kpi-card"><p className="kpi-title">Terminés</p><p className="kpi-value">{kpis.done}</p></article>
              <article className="kpi-card"><p className="kpi-title">En échec</p><p className="kpi-value">{kpis.failed}</p></article>
              <article className="kpi-card"><p className="kpi-title">À revoir</p><p className="kpi-value">{kpis.review}</p></article>
            </section>

            <section className="card">
              <h3>Suivi backend</h3>
              <p>API: <code>{apiBaseUrl}</code></p>
              <p>
                Recovery — auto-retried: <strong>{recovery?.auto_retried ?? 0}</strong>, manual intervention:{' '}
                <strong>{recovery?.manual_intervention ?? 0}</strong>, retry pending: <strong>{recovery?.retry_pending ?? 0}</strong>
              </p>
              {error ? <p className="error">Erreur: {error}</p> : null}
            </section>

            <section className="card">
              <h3>Traitements (en cours)</h3>
              <table>
                <thead><tr><th>Dossier</th><th>Statut</th><th>Progression</th><th>Étape</th></tr></thead>
                <tbody>
                  {(jobs.running || []).map((job) => (
                    <tr key={job.id}><td>{job.folder}</td><td>{job.status}</td><td>{job.progress}%</td><td>{job.stage || '—'}</td></tr>
                  ))}
                  {(jobs.running || []).length === 0 ? <tr><td colSpan={4}>Aucun traitement en cours</td></tr> : null}
                </tbody>
              </table>
            </section>

            <section className="card">
              <h3>Évènements récents</h3>
              <table>
                <thead><tr><th>Quand</th><th>Étape</th><th>Dossier</th><th>Message</th></tr></thead>
                <tbody>
                  {(jobs.events || []).slice(0, MAX_EVENTS).map((evt) => (
                    <tr key={evt.id}><td>{formatDate(evt.timestamp)}</td><td>{evt.stage}</td><td>{evt.folder}</td><td>{evt.message}</td></tr>
                  ))}
                  {(jobs.events || []).length === 0 ? <tr><td colSpan={4}>Aucun évènement</td></tr> : null}
                </tbody>
              </table>
            </section>
          </main>
        </div>
      </div>
    </>
  );
}
