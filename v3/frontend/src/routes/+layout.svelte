<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  // Import components
  import Header from '$lib/components/layout/Header.svelte';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import Footer from '$lib/components/layout/Footer.svelte';
  
  // Import stores
  import { authStore } from '$lib/stores/authStore.js';
  import { websocketClient } from '$lib/api/websocket.js';
  
  let sidebarOpen = false;
  
  onMount(async () => {
    // Initialize WebSocket connection
    try {
      await websocketClient.connect();
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
    
    // Check authentication
    if (!$authStore.isAuthenticated) {
      // Redirect to login if not authenticated
      await goto('/login');
    }
  });
  
  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }
</script>

<svelte:head>
  <title>Audiobook Master v3</title>
  <meta name="description" content="Audiobook Master v3 - Modern audio processing management" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <!-- Header -->
  <Header {toggleSidebar} />
  
  <!-- Main Content -->
  <div class="flex">
    <!-- Sidebar -->
    <Sidebar {sidebarOpen} />
    
    <!-- Page Content -->
    <main class="flex-1 p-6 lg:ml-64">
      <div class="max-w-7xl mx-auto">
        <slot />
      </div>
    </main>
  </div>
  
  <!-- Footer -->
  <Footer />
</div>

<style>
  main {
    transition: margin-left 0.3s ease;
  }
  
  @media (min-width: 1024px) {
    main {
      margin-left: 16rem; /* lg:ml-64 */
    }
  }
</style>
