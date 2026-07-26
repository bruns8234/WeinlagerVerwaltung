<template>
  <div class="dashboard">
    <h2>Dashboard</h2>
    
    <div v-if="loading" class="loading">
      <p>Lade Dashboard...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadDashboard">Neu laden</button>
    </div>
    
    <div v-else class="dashboard-content">
      <!-- Statistik-Karten -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🍷</div>
          <div class="stat-info">
            <h3>Gesamtbestand</h3>
            <p class="stat-value">{{ stats.gesamtFlaschen || 0 }}</p>
            <p class="stat-label">Flaschen</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-info">
            <h3>Weinsorten</h3>
            <p class="stat-value">{{ stats.weinsorten || 0 }}</p>
            <p class="stat-label">im Bestand</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <h3>Bestandswert</h3>
            <p class="stat-value">{{ formatCurrency(stats.bestandswert || 0) }}</p>
            <p class="stat-label">Gesamtwert</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🏠</div>
          <div class="stat-info">
            <h3>Lagerauslastung</h3>
            <p class="stat-value">{{ stats.auslastung || 0 }}%</p>
            <p class="stat-label">Belegte Plätze</p>
          </div>
        </div>
      </div>
      
      <!-- Lagerauslastung Balken -->
      <div class="chart-section">
        <h3>Lagerauslastung</h3>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: (stats.auslastung || 0) + '%' }"
            :class="getAuslastungClass(stats.auslastung)"
          ></div>
        </div>
        <p class="progress-label">
          {{ stats.belegtePlaetze || 0 }} von {{ stats.gesamtPlaetze || 0 }} Plätzen belegt
        </p>
      </div>
      
      <!-- Alterungsanalyse -->
      <div class="chart-section" v-if="stats.alterungsanalyse && stats.alterungsanalyse.length > 0">
        <h3>Alterungsanalyse</h3>
        <div class="alterung-list">
          <div 
            v-for="item in stats.alterungsanalyse" 
            :key="item.kategorie"
            class="alterung-item"
          >
            <span class="alterung-label">{{ item.kategorie }}</span>
            <span class="alterung-count">{{ item.anzahl }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reportingAPI } from '../services/api.js'

export default {
  name: 'Dashboard',
  data() {
    return {
      loading: false,
      error: null,
      stats: {}
    }
  },
  async mounted() {
    await this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      this.loading = true
      this.error = null
      
      try {
        const response = await reportingAPI.getUebersicht()
        this.stats = response.data
      } catch (err) {
        this.error = 'Fehler beim Laden des Dashboards: ' + (err.response?.data?.message || err.message)
      } finally {
        this.loading = false
      }
    },
    formatCurrency(amount) {
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
      }).format(amount)
    },
    getAuslastungClass(auslastung) {
      if (auslastung >= 90) return 'progress-critical'
      if (auslastung >= 75) return 'progress-warning'
      return 'progress-normal'
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.dashboard h2 {
  color: #722F37;
  margin-bottom: 1.5rem;
  font-size: 1.75rem;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.error {
  color: #dc3545;
}

.error button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #722F37;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info h3 {
  margin: 0;
  font-size: 0.875rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  margin: 0.25rem 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #212529;
}

.stat-label {
  margin: 0;
  font-size: 0.875rem;
  color: #6c757d;
}

.chart-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 1.5rem;
}

.chart-section h3 {
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 1.125rem;
}

.progress-bar {
  height: 24px;
  background: #e9ecef;
  border-radius: 12px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
  transition: width 0.3s ease;
  border-radius: 12px;
}

.progress-fill.progress-warning {
  background: linear-gradient(90deg, #ffc107 0%, #fd7e14 100%);
}

.progress-fill.progress-critical {
  background: linear-gradient(90deg, #dc3545 0%, #c82333 100%);
}

.progress-label {
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
  color: #6c757d;
}

.alterung-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.alterung-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.alterung-label {
  font-weight: 500;
  color: #495057;
}

.alterung-count {
  font-size: 1.25rem;
  font-weight: 600;
  color: #722F37;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>