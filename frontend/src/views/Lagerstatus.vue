<template>
  <div class="lagerstatus">
    <h2>Lagerstatus</h2>

    <!-- Zusammenfassung -->
    <div class="summary-cards">
      <div class="summary-card">
        <h3>Gesamtplätze</h3>
        <p class="summary-value">{{ summary.gesamtPlaetze || 0 }}</p>
      </div>
      <div class="summary-card">
        <h3>Belegt</h3>
        <p class="summary-value summary-belegt">{{ summary.belegt || 0 }}</p>
      </div>
      <div class="summary-card">
        <h3>Frei</h3>
        <p class="summary-value summary-frei">{{ summary.frei || 0 }}</p>
      </div>
      <div class="summary-card">
        <h3>Auslastung</h3>
        <p class="summary-value">{{ summary.auslastung || 0 }}%</p>
      </div>
    </div>

    <!-- Fortschrittsbalken -->
    <div class="progress-section">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: (summary.auslastung || 0) + '%' }"
          :class="getProgressClass(summary.auslastung)"
        ></div>
      </div>
    </div>

    <!-- Ladezustand -->
    <div v-if="loading" class="loading">Lade Lagerstatus...</div>

    <!-- Fehler -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadLagerstatus">Neu laden</button>
    </div>

    <!-- Filter -->
    <div v-else class="filter-section">
      <div class="filter-row">
        <select v-model="filterRegal" class="form-select">
          <option value="">Alle Regale</option>
          <option v-for="regal in regale" :key="regal" :value="regal">{{ regal }}</option>
        </select>
        <select v-model="filterStatus" class="form-select">
          <option value="">Alle Status</option>
          <option value="frei">Frei</option>
          <option value="belegt">Belegt</option>
        </select>
      </div>
    </div>

    <!-- Lagerplatz-Grid -->
    <div v-else class="lager-grid">
      <div 
        v-for="platz in gefiltertePlaetze" 
        :key="platz.id"
        class="lager-platz"
        :class="{ 'platz-belegt': !platz.frei, 'platz-frei': platz.frei }"
        @click="showPlatzDetails(platz)"
      >
        <div class="platz-header">
          <span class="platz-id">{{ platz.regal }}-{{ platz.ebene }}-{{ platz.position }}</span>
        </div>
        <div v-if="!platz.frei" class="platz-info">
          <p class="platz-wein">{{ platz.weinName }}</p>
          <p class="platz-jahrgang">{{ platz.jahrgang }}</p>
        </div>
        <div v-else class="platz-frei-label">
          Frei
        </div>
      </div>
    </div>

    <!-- Modal für Platz-Details -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content modal-sm" @click.stop>
        <div class="modal-header">
          <h3>Lagerplatz: {{ selectedPlatz?.regal }}-{{ selectedPlatz?.ebene }}-{{ selectedPlatz?.position }}</h3>
          <button class="btn-close" @click="closeModal">&times;</button>
        </div>
        <div class="platz-details">
          <p><strong>Status:</strong> {{ selectedPlatz?.frei ? 'Frei' : 'Belegt' }}</p>
          <p v-if="!selectedPlatz?.frei"><strong>Wein:</strong> {{ selectedPlatz?.weinName }}</p>
          <p v-if="!selectedPlatz?.frei"><strong>Jahrgang:</strong> {{ selectedPlatz?.jahrgang }}</p>
          <p v-if="!selectedPlatz?.frei"><strong>Seit:</strong> {{ formatDate(selectedPlatz?.lagerDatum) }}</p>
          <p v-if="selectedPlatz?.maxFlaschen"><strong>Max. Flaschen:</strong> {{ selectedPlatz?.maxFlaschen }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">Schließen</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { lagerplaetzeAPI } from '../services/api.js'

export default {
  name: 'Lagerstatus',
  data() {
    return {
      loading: false,
      error: null,
      plaetze: [],
      summary: {},
      filterRegal: '',
      filterStatus: '',
      regale: [],
      showModal: false,
      selectedPlatz: null
    }
  },
  computed: {
    gefiltertePlaetze() {
      let result = this.plaetze
      
      if (this.filterRegal) {
        result = result.filter(p => p.regal === this.filterRegal)
      }
      
      if (this.filterStatus === 'frei') {
        result = result.filter(p => p.frei)
      } else if (this.filterStatus === 'belegt') {
        result = result.filter(p => !p.frei)
      }
      
      return result
    }
  },
  async mounted() {
    await this.loadLagerstatus()
  },
  methods: {
    async loadLagerstatus() {
      this.loading = true
      this.error = null
      try {
        const [plaetzeRes, summaryRes] = await Promise.all([
          lagerplaetzeAPI.getAll(),
          lagerplaetzeAPI.getSummary()
        ])
        this.plaetze = plaetzeRes.data
        this.summary = summaryRes.data
        
        // Regale extrahieren
        const regalSet = new Set()
        this.plaetze.forEach(p => { if (p.regal) regalSet.add(p.regal) })
        this.regale = Array.from(regalSet).sort()
      } catch (err) {
        this.error = 'Fehler beim Laden des Lagerstatus: ' + (err.response?.data?.message || err.message)
      } finally {
        this.loading = false
      }
    },

    showPlatzDetails(platz) {
      this.selectedPlatz = platz
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
      this.selectedPlatz = null
    },

    getProgressClass(auslastung) {
      if (auslastung >= 90) return 'progress-critical'
      if (auslastung >= 75) return 'progress-warning'
      return 'progress-normal'
    },

    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('de-DE')
    }
  }
}
</script>

<style scoped>
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.summary-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #6c757d;
  text-transform: uppercase;
}

.summary-value {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
  color: #212529;
}

.summary-belegt { color: #722F37; }
.summary-frei { color: #28a745; }

.progress-section {
  margin-bottom: 1.5rem;
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

.filter-section {
  margin-bottom: 1.5rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
}

.lager-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}

.lager-platz {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border-left: 4px solid #28a745;
}

.lager-platz:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.platz-belegt {
  border-left-color: #722F37;
}

.platz-frei {
  border-left-color: #28a745;
}

.platz-header {
  margin-bottom: 0.5rem;
}

.platz-id {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}

.platz-info .platz-wein {
  margin: 0;
  font-size: 0.85rem;
  color: #212529;
  font-weight: 500;
}

.platz-info .platz-jahrgang {
  margin: 0.25rem 0 0 0;
  font-size: 0.8rem;
  color: #6c757d;
}

.platz-frei-label {
  text-align: center;
  color: #28a745;
  font-weight: 500;
  padding: 0.5rem 0;
}

/* Modal */
.modal-sm {
  max-width: 400px;
}

.platz-details p {
  margin: 0.5rem 0;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #dc3545;
}
</style>