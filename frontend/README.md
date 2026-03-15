# Audiobook Master v3 - Frontend Svelte

**Frontend moderne** : Svelte + Tailwind CSS + WebSocket temps réel  
**Version** : 3.0.0-alpha.1  
**Statut** : En développement  

---

## 🎨 Architecture

```text
[Svelte Components]
          |
   (Stores + Tailwind CSS)
          |
[WebSocket Client]
          |
[FastAPI Backend]
```

## 📁 Structure du Projet

```
v3/frontend/
├── src/
│   ├── lib/
│   │   ├── stores/
│   │   │   ├── authStore.js      # Authentification
│   │   │   ├── jobStore.js       # Jobs
│   │   │   ├── packetStore.js    # Packets
│   │   │   └── notificationStore.js # Notifications
│   │   ├── api/
│   │   │   ├── client.js         # Client API
│   │   │   └── websocket.js      # WebSocket client
│   │   ├── utils/
│   │   │   ├── auth.js           # Utilitaires auth
│   │   │   ├── format.js         # Formatage
│   │   │   └── validation.js     # Validation
│   │   └── components/
│   │       ├── ui/
│   │       │   ├── Button.svelte
│   │       │   ├── Input.svelte
│   │       │   ├── Modal.svelte
│   │       │   └── Loading.svelte
│   │       └── layout/
│   │           ├── Header.svelte
│   │           ├── Sidebar.svelte
│   │           └── Footer.svelte
│   ├── routes/
│   │   ├── +layout.svelte        # Layout principal
│   │   ├── +page.svelte         # Tableau de bord
│   │   ├── jobs/
│   │   │   ├── +page.svelte     # Liste jobs
│   │   │   ├── [id]/
│   │   │   │   └── +page.svelte # Détail job
│   │   ├── packets/
│   │   │   ├── +page.svelte     # Liste packets
│   │   │   └── [id]/
│   │   │       └── +page.svelte # Détail packet
│   │   ├── errors/
│   │   │   └── +page.svelte     # Gestion erreurs
│   │   └── settings/
│   │       └── +page.svelte     # Configuration
│   ├── app.css                  # Styles globaux
│   ├── app.html                 # HTML template
│   └── app.js                   # Point d'entrée
├── static/
│   ├── favicon.ico
│   └── logo.png
├── package.json
├── svelte.config.js
├── tailwind.config.js
├── vite.config.js
├── Dockerfile
└── README.md
```

## 🚀 Démarrage Rapide

### Installation
```bash
# Installation dépendances
npm install

# Ou avec yarn
yarn install
```

### Développement
```bash
# Démarrer serveur de développement
npm run dev

# Ou avec yarn
yarn dev

# Accès: http://localhost:5173
```

### Build
```bash
# Build pour production
npm run build

# Preview build
npm run preview
```

## 🎨 Configuration Tailwind CSS

### tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
```

## 📦 Stores Svelte

### authStore.js
```javascript
import { writable } from 'svelte/store';
import { apiClient } from '$lib/api/client.js';

function createAuthStore() {
  const { subscribe, set, update } = writable({
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false
  });

  return {
    subscribe,
    
    async login(credentials) {
      update(state => ({ ...state, loading: true }));
      try {
        const response = await apiClient.post('/auth/login', credentials);
        const { user, token } = response.data;
        
        set({
          user,
          token,
          isAuthenticated: true,
          loading: false
        });
        
        localStorage.setItem('token', token);
      } catch (error) {
        update(state => ({ ...state, loading: false }));
        throw error;
      }
    },
    
    logout() {
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false
      });
      localStorage.removeItem('token');
    },
    
    async refreshToken() {
      // TODO: Implémenter refresh token
    }
  };
}

export const authStore = createAuthStore();
```

### jobStore.js
```javascript
import { writable, derived } from 'svelte/store';
import { websocketClient } from '$lib/api/websocket.js';

function createJobStore() {
  const { subscribe, set, update } = writable([]);
  
  // WebSocket events
  websocketClient.on('job_update', (event) => {
    update(jobs => {
      const index = jobs.findIndex(job => job.id === event.entity_id);
      if (index !== -1) {
        const newJobs = [...jobs];
        newJobs[index] = { ...newJobs[index], ...event.payload };
        return newJobs;
      }
      return jobs;
    });
  });

  return {
    subscribe,
    
    async fetchJobs() {
      const response = await apiClient.get('/api/v1/jobs');
      set(response.data);
    },
    
    async createJob(jobData) {
      const response = await apiClient.post('/api/v1/jobs', jobData);
      update(jobs => [...jobs, response.data]);
      return response.data;
    },
    
    async updateJob(id, updates) {
      const response = await apiClient.put(`/api/v1/jobs/${id}`, updates);
      update(jobs => jobs.map(job => 
        job.id === id ? { ...job, ...response.data } : job
      ));
      return response.data;
    },
    
    async deleteJob(id) {
      await apiClient.delete(`/api/v1/jobs/${id}`);
      update(jobs => jobs.filter(job => job.id !== id));
    }
  };
}

export const jobStore = createJobStore();

// Store dérivé pour les jobs actifs
export const activeJobs = derived(
  jobStore,
  $jobs => $jobs.filter(job => job.status === 'running')
);

// Store dérivé pour les jobs en erreur
export const failedJobs = derived(
  jobStore,
  $jobs => $jobs.filter(job => job.status === 'failed')
);
```

## 🌐 WebSocket Client

### websocket.js
```javascript
class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.eventHandlers = {};
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.emit(data.event_type, data);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.emit('disconnected');
        this.reconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.reconnect();
    }
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      setTimeout(() => {
        console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
        this.connect();
      }, delay);
    }
  }

  on(event, handler) {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = [];
    }
    this.eventHandlers[event].push(handler);
  }

  emit(event, data) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach(handler => handler(data));
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const websocketClient = new WebSocketClient('ws://localhost:8000/ws');
```

## 🎯 Composants UI

### Button.svelte
```svelte
<script>
  export let variant = 'primary';
  export let size = 'md';
  export let disabled = false;
  export let loading = false;
  export let onClick = () => {};

  const variants = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    success: 'bg-success-600 hover:bg-success-700 text-white',
    error: 'bg-error-600 hover:bg-error-700 text-white',
    warning: 'bg-warning-600 hover:bg-warning-700 text-white',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  $: classes = `${variants[variant]} ${sizes[size]} 
                   rounded-lg font-medium transition-colors duration-200
                   ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                   ${loading ? 'opacity-75' : ''}`;
</script>

<button 
  class={classes}
  {disabled}
  onclick={onClick}
>
  {#if loading}
    <div class="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
  {:else}
    <slot />
  {/if}
</button>
```

### Loading.svelte
```svelte
<script>
  export let size = 'md';
  export let text = 'Chargement...';

  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };
</script>

<div class="flex items-center justify-center space-x-2">
  <div class="animate-spin {sizes[size]} border-2 border-primary-200 border-t-primary-600 rounded-full"></div>
  {#if text}
    <span class="text-gray-600">{text}</span>
  {/if}
</div>
```

## 📱 Pages Principales

### Tableau de bord (+page.svelte)
```svelte
<script>
  import { onMount } from 'svelte';
  import { jobStore, activeJobs, failedJobs } from '$lib/stores/jobStore.js';
  import Loading from '$lib/components/ui/Loading.svelte';
  import JobCard from '$lib/components/JobCard.svelte';
  import MetricsCard from '$lib/components/MetricsCard.svelte';

  let jobs = [];
  let loading = true;

  onMount(async () => {
    await jobStore.fetchJobs();
    loading = false;
  });

  $: activeCount = $activeJobs.length;
  $: failedCount = $failedJobs.length;
</script>

<div class="p-6">
  <h1 class="text-3xl font-bold text-gray-900 mb-6">Tableau de bord</h1>
  
  <!-- Metrics -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <MetricsCard title="Jobs Actifs" value={activeCount} color="primary" />
    <MetricsCard title="Jobs en Erreur" value={failedCount} color="error" />
    <MetricsCard title="Total Jobs" value={$jobs.length} color="gray" />
  </div>

  <!-- Recent Jobs -->
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-semibold mb-4">Jobs Récents</h2>
    
    {#if loading}
      <Loading text="Chargement des jobs..." />
    {:else}
      <div class="space-y-4">
        {#each $jobs.slice(0, 5) as job}
          <JobCard {job} />
        {/each}
      </div>
    {/if}
  </div>
</div>
```

## 🐳 Docker

### Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

### Docker Compose
```yaml
version: '3.8'

services:
  frontend:
    build: ./v3/frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000/ws

  backend:
    build: ./v3/backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/audiobook_v3
      - JWT_SECRET_KEY=votre-secret-key
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=audiobook_v3
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🧪 Tests

### Tests Unitaires
```bash
# Tests composants
npm run test

# Tests avec watch
npm run test:watch

# Couverture
npm run test:coverage
```

### Tests E2E
```bash
# Tests Playwright
npm run test:e2e

# Tests E2E headed
npm run test:e2e:headed
```

## 📊 Performance

### Optimisations
- **Bundle size** : Svelte compilation
- **Runtime performance** : Pas de virtual DOM
- **Loading** : Code splitting par route
- **Caching** : Service worker pour assets statiques

### Monitoring
```javascript
// Performance monitoring
if (import.meta.env.PROD) {
  // Google Analytics
  gtag('config', 'GA_MEASUREMENT_ID');
  
  // Sentry pour erreurs
  Sentry.init({
    dsn: 'your-sentry-dsn',
  });
}
```

## 🔧 Développement

### Code Style
```bash
# Formatage
npm run format

# Linting
npm run lint

# Type checking
npm run check
```

### Pre-commit
```bash
# Installation
npm install --save-dev husky lint-staged

# Configuration
npx husky install
npx husky add .husky/pre-commit "npm run lint-staged"
```

---

**Statut**: 🚧 **En développement** - Phase 1 en cours
