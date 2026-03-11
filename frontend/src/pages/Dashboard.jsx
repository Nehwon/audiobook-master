import React from 'react';
import { Layout, Card, StatCard, RecoveryStatus, JobHeartbeat } from '../components';
import { useQuery } from '@tanstack/react-query';

const fetchStats = async () => {
  const response = await fetch('/api/stats');
  if (!response.ok) {
    throw new Error('Échec de la récupération des statistiques');
  }
  return response.json();
};

const Dashboard = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: fetchStats,
  });
  
  return (
    <Layout>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Jobs en cours"
          value={stats?.active_jobs || 0}
          trend={stats?.active_jobs_trend || 0}
        />
        <StatCard
          title="Jobs orphelins"
          value={stats?.orphaned_jobs || 0}
          trend={stats?.orphaned_jobs_trend || 0}
          variant="warning"
        />
        <StatCard
          title="Erreurs récentes"
          value={stats?.recent_errors || 0}
          trend={stats?.recent_errors_trend || 0}
          variant="destructive"
        />
        <StatCard
          title="Taux de réussite"
          value={`${stats?.success_rate || 0}%`}
          trend={stats?.success_rate_trend || 0}
          variant="success"
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-lg font-semibold mb-4">État de la récupération</h2>
          <RecoveryStatus />
        </Card>
        
        <Card>
          <h2 className="text-lg font-semibold mb-4">Jobs actifs</h2>
          <div className="space-y-4">
            {stats?.active_jobs_list?.map(job => (
              <div key={job.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <div>
                  <p className="font-medium">Job #{job.id}</p>
                  <p className="text-sm text-gray-500">
                    {job.description}
                  </p>
                </div>
                <JobHeartbeat jobId={job.id} />
              </div>
            )) || (
              <p className="text-gray-500">Aucun job actif</p>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;
