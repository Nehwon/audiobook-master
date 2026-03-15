import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, Badge, Button, Alert, Spinner } from './ui-components';

const fetchRecoveryStatus = async () => {
  const response = await fetch('/api/recovery/status');
  if (!response.ok) {
    throw new Error('Échec de la récupération de l\'état de récupération');
  }
  return response.json();
};

const RecoveryStatus = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingResult, setProcessingResult] = useState(null);
  
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['recoveryStatus'],
    queryFn: fetchRecoveryStatus,
    refetchInterval: 30000, // Rafraîchissement toutes les 30 secondes
  });
  
  const handleProcessOrphans = async () => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/recovery/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ retry_policy: 'safe_retry' }),
      });
      
      const result = await response.json();
      setProcessingResult(result);
      refetch(); // Rafraîchir les données après traitement
    } catch (err) {
      setProcessingResult({ success: false, message: 'Échec du traitement' });
    } finally {
      setIsProcessing(false);
    }
  };
  
  if (isLoading) return <Spinner />;
  
  if (error) return (
    <Alert variant="destructive">
      Erreur: {error.message}
    </Alert>
  );
  
  return (
    <Card className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">État de la récupération</h2>
        <Badge
          variant={data.orphaned_job_count === 0 ? 'success' : 'destructive'}
        >
          {data.orphaned_job_count} jobs orphelins
        </Badge>
      </div>
      
      {data.orphaned_job_count > 0 && (
        <div className="mb-4">
          <Button
            onClick={handleProcessOrphans}
            disabled={isProcessing}
            className="mb-2"
          >
            {isProcessing ? 'Traitement en cours...' : 'Traiter les jobs orphelins'}
          </Button>
          
          {processingResult && (
            <Alert variant={processingResult.success ? 'success' : 'destructive'} className="mt-2">
              {processingResult.message}
            </Alert>
          )}
        </div>
      )}
      
      <div className="space-y-2">
        {data.jobs.map(job => (
          <div key={job.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
            <div>
              <p className="font-medium">Job #{job.id}</p>
              <p className="text-sm text-gray-500">
                Dernier heartbeat: {new Date(job.last_heartbeat).toLocaleString()}
              </p>
            </div>
            <Badge variant="warning">
              {job.retry_count} retries
            </Badge>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default RecoveryStatus;
