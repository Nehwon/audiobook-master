import React, { useEffect, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button, Tooltip } from './ui-components';

const updateHeartbeat = async (jobId) => {
  const response = await fetch(`/api/jobs/${jobId}/heartbeat`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Échec de la mise à jour du heartbeat');
  }
  return response.json();
};

const JobHeartbeat = ({ jobId }) => {
  const [lastUpdate, setLastUpdate] = useState(null);
  
  const { mutate, isPending, isError, isSuccess } = useMutation({
    mutationFn: () => updateHeartbeat(jobId),
    onSuccess: () => {
      setLastUpdate(new Date().toISOString());
    },
  });
  
  // Mise à jour automatique toutes les 2 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      mutate();
    }, 120000); // 2 minutes
    
    return () => clearInterval(interval);
  }, [jobId]);
  
  return (
    <div className="flex items-center space-x-2">
      <Tooltip content={`Dernière mise à jour: ${lastUpdate ? new Date(lastUpdate).toLocaleTimeString() : 'Jamais'}`}>
        <Button
          size="sm"
          variant="outline"
          onClick={() => mutate()}
          disabled={isPending}
        >
          {isPending ? 'Mise à jour...' : 'Mettre à jour le heartbeat'}
        </Button>
      </Tooltip>
      
      {isSuccess && (
        <span className="text-green-500 text-sm">✓ Mis à jour</span>
      )}
      {isError && (
        <span className="text-red-500 text-sm">Échec</span>
      )}
    </div>
  );
};

export default JobHeartbeat;
