<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  
  // Import components
  import MetricsCard from '$lib/components/ui/MetricsCard.svelte';
  import JobList from '$lib/components/jobs/JobList.svelte';
  import Loading from '$lib/components/ui/Loading.svelte';
  
  // Import stores
  import { jobStore, activeJobs, failedJobs } from '$lib/stores/jobStore.js';
  import { websocketClient } from '$lib/api/websocket.js';
  
  let loading = true;
  let jobs = [];
  let stats = {
    total: 0,
    active: 0,
    failed: 0,
    completed: 0
  };
  
  onMount(async () => {
    // Load initial data
    await loadDashboardData();
    
    // Set up WebSocket listeners
    websocketClient.on('job_update', handleJobUpdate);
    websocketClient.on('job_insert', handleJobInsert);
    websocketClient.on('job_delete', handleJobDelete);
    
    loading = false;
  });
  
  async function loadDashboardData() {
    try {
      await jobStore.fetchJobs();
      await loadStats();
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  }
  
  async function loadStats() {
    try {
      const response = await fetch('/api/v1/jobs/stats');
      if (response.ok) {
        stats = await response.json();
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }
  
  function handleJobUpdate(event) {
    if (event.entity === 'job') {
      // Stats will be updated automatically through store
      loadStats();
    }
  }
  
  function handleJobInsert(event) {
    if (event.entity === 'job') {
      loadStats();
    }
  }
  
  function handleJobDelete(event) {
    if (event.entity === 'job') {
      loadStats();
    }
  }
  
  $: {
    jobs = $jobStore;
    stats.active = $activeJobs.length;
    stats.failed = $failedJobs.length;
  }
</script>

<svelte:head>
  <title>Tableau de bord - Audiobook Master v3</title>
</svelte:head>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Tableau de bord
      </h1>
      <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
        Vue d'ensemble des traitements audio et du système
      </p>
    </div>
    
    <div class="flex space-x-3">
      <button 
        class="btn btn-primary"
        onclick={() => window.location.href = '/jobs/new'}
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nouveau Job
      </button>
    </div>
  </div>
  
  <!-- Metrics Cards -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <MetricsCard
      title="Jobs Actifs"
      value={stats.active}
      icon="play-circle"
      color="primary"
      trend={stats.active > 0 ? 'up' : 'neutral'}
    />
    
    <MetricsCard
      title="Jobs en Erreur"
      value={stats.failed}
      icon="exclamation-circle"
      color="error"
      trend={stats.failed > 0 ? 'up' : 'down'}
    />
    
    <MetricsCard
      title="Jobs Complétés"
      value={stats.completed}
      icon="check-circle"
      color="success"
      trend="up"
    />
    
    <MetricsCard
      title="Total Jobs"
      value={stats.total}
      icon="folder"
      color="gray"
      trend="up"
    />
  </div>
  
  <!-- Recent Jobs -->
  <div class="card p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        Jobs Récents
      </h2>
      <a 
        href="/jobs" 
        class="text-blue-600 hover:text-blue-800 text-sm font-medium"
      >
        Voir tout →
      </a>
    </div>
    
    {#if loading}
      <Loading text="Chargement des jobs..." />
    {:else if jobs.length === 0}
      <div class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
          Aucun job
        </h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Commencez par créer votre premier job de traitement audio.
        </p>
        <div class="mt-6">
          <button 
            class="btn btn-primary"
            onclick={() => window.location.href = '/jobs/new'}
          >
            Créer un Job
          </button>
        </div>
      </div>
    {:else}
      <JobList jobs={jobs.slice(0, 5)} compact={true} />
    {/if}
  </div>
  
  <!-- System Status -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Connection Status -->
    <div class="card p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
        État des Connexions
      </h3>
      
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            WebSocket
          </span>
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Connecté
            </span>
          </div>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            API
          </span>
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Opérationnelle
            </span>
          </div>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            Base de données
          </span>
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Connectée
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Recent Activity -->
    <div class="card p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Activité Récente
      </h3>
      
      <div class="space-y-3">
        <div class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              Job #12345 démarré
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Il y a 2 minutes
            </p>
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              Job #12344 complété
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Il y a 15 minutes
            </p>
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              Job #12343 en erreur
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Il y a 1 heure
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
