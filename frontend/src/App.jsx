const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export default function App() {
  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', maxWidth: 960, margin: '2rem auto', padding: '0 1rem' }}>
      <h1>Audiobook Master — Interface React</h1>
      <p>
        Cette interface React est prête pour se connecter au backend Flask.
      </p>
      <ul>
        <li>
          API backend: <code>{apiBaseUrl}</code>
        </li>
        <li>
          Endpoint de santé: <code>{apiBaseUrl}/health</code>
        </li>
        <li>
          Contrat API: <code>/docs/api/openapi-frontend-sprint3.yaml</code>
        </li>
      </ul>
    </main>
  );
}
