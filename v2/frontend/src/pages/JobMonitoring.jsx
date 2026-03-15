import React, { useState } from 'react';
import { Layout, Card, Table, Badge, Button, Spinner, Alert } from '../components';
import { useQuery } from '@tanstack/react-query';

const fetchJobs = async (statusFilter) => {
  const url = statusFilter ? `/api/jobs?status=${statusFilter}` : '/api/jobs';
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Échec de la récupération des jobs');
  }
  return response.json();
};

const JobMonitoring = () => {
  const [statusFilter, setStatusFilter] = useState('');
  
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['jobs', statusFilter],
    queryFn: () => fetchJobs(statusFilter),
  });
  
  if (isLoading) return <Spinner />;
  
  if (error) return (
    <Alert variant="destructive">
      Erreur: {error.message}
    </Alert>
  );
  
  return (
    <Layout>
      <Card className="mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-semibold">Suivi des jobs</h1>
          <div className="flex space-x-2">
            <Button
              variant={statusFilter === '' ? 'default' : 'outline'}
              onClick={() => setStatusFilter('')}
            >
              Tous
            </Button>
            <Button
              variant={statusFilter === 'running' ? 'default' : 'outline'}
              onClick={() => setStatusFilter('running')}
            >
              En cours
            </Button>
            <Button
              variant={statusFilter === 'failed' ? 'default' : 'outline'}
              onClick={() => setStatusFilter('failed')}
            >
              Échoués
            </Button>
            <Button
              onClick={refetch}
              variant="outline"
            >
              Rafraîchir
            </Button>
          </div>
        </div>
      </Card>
      
      <Card>
        <Table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Statut</th>
              <th>Dernière mise à jour</th>
              <th>Retries</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.jobs.map(job => (
              <tr key={job.id}>
                <td>{job.id}</td>
                <td>
                  <Badge
                    variant={{
                      'queued': 'info',
                      'running': 'warning',
                      'failed': 'destructive',
                      'done': 'success',
                    }[job.status] || 'default'}
                  >
                    {job.status}
                  </Badge>
                </td>
                <td>{new Date(job.updated_at).toLocaleString()}</td>
                <td>{job.retry_count}</td>
                <td>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      // Logique pour voir les détails du job
                    }}
                  >
                    Détails
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>
    </Layout>
  );
};

export default JobMonitoring;
