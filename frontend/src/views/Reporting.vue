<template>
  <div class="reporting">
    <h2>Reporting</h2>

    <div class="report-cards">
      <div class="report-card" @click="showReport = 'bestand'">
        <h3>Bestandsübersicht</h3>
        <p>Aktueller Bestand nach Wein, Region und Art</p>
      </div>
      <div class="report-card" @click="showReport = 'lager'">
        <h3>Lagerauslastung</h3>
        <p>Belegung und Kapazität der Lagerplätze</p>
      </div>
      <div class="report-card" @click="showReport = 'bewegungen'">
        <h3>Bewegungen</h3>
        <p>Ein- und Auslagerungen im Zeitraum</p>
      </div>
    </div>

    <div v-if="showReport" class="report-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ reportTitle }}</h3>
          <button class="btn-close" @click="showReport = null">×</button>
        </div>

        <!-- Bestand Report -->
        <div v-if="showReport === 'bestand'" class="report-data">
          <div class="filter-bar">
            <select v-model="bestandFilter.region" class="form-select">
              <option value="">Alle Regionen</option>
              <option v-for="r in regionen" :key="r.id" :value="r.bezeichnung">{{ r.bezeichnung }}</option>
            </select>
            <select v-model="bestandFilter.art" class="form-select">
              <option value="">Alle Arten</option>
              <option v-for="a in arten" :key="a.id" :value="a.bezeichnung">{{ a.bezeichnung }}</option>
            </select>
            <button class="btn btn-primary" @click="loadBestandReport">Anzeigen</button>
          </div>

          <table v-if="bestandData.length > 0">
            <thead>
              <tr>
                <th>Wein</th>
                <th>Region</th>
                <th>Art</th>
                <th>Flaschen</th>
                <th>Lagerplätze</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in bestandData" :key="row.weinName">
                <td>{{ row.weinName }}</td>
                <td>{{ row.region }}</td>
                <td>{{ row.art }}</td>
                <td>{{ row.flaschen }}</td>
                <td>{{ row.plaetze }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Lager Report -->
        <div v-if="showReport === 'lager'" class="report-data">
          <div class="lager-stats">
            <div class="stat-card">
              <h4>Gesamtkapazität</h4>
              <p class="stat-value">{{ lagerStats.gesamt || 0 }}</p>
            </div>
            <div class="stat-card">
              <h4>Belegt</h4>
              <p class="stat-value">{{ lagerStats.belegt || 0 }}</p>
            </div>
            <div class="stat-card">
              <h4>Frei</h4>
              <p class="stat-value">{{ lagerStats.frei || 0 }}</p>
            </div>
            <div class="stat-card">
              <h4>Auslastung</h4>
              <p class="stat-value">{{ auslastung }}%</p>
            </div>
          </div>
        </div>

        <!-- Bewegungen Report -->
        <div v-if="showReport === 'bewegungen'" class="report-data">
          <div class="filter-bar">
            <input type="date" v-model="bewegungFilter.von" class="form-input" />
            <input type="date" v-model="bewegungFilter.bis" class="form-input" />
            <button class="btn btn-primary" @click="loadBewegungenReport">Anzeigen</button>
          </div>

          <table v-if="bewegungData.length > 0">
            <thead>
              <tr>
                <th>Datum</th>
                <th>Typ</th>
                <th>Wein</th>
                <th>Anzahl</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in bewegungData" :key="row.id">
                <td>{{ formatDate(row.datum) }}</td>
                <td>
                  <span :class="['badge', 'badge-' + row.aktion]">
                    {{ formatAktion(row.aktion) }}
                  </span>
                </td>
                <td>{{ row.weinName }}</td>
                <td>{{ row.anzahl }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reportingAPI, stammdatenAPI } from '../services/api.js'

export default {
  name: 'Reporting',
  data() {
    return {
      showReport: null,
      regionen: [],
      arten: [],
      bestandFilter: { region: '', art: '' },
      bestandData: [],
      lagerStats: {},
      bewegungFilter: { von: '', bis: '' },
      bewegungData: []
    }
  },
  computed: {
    reportTitle() {
      const titles = {
        bestand: 'Bestandsübersicht',
        lager: 'Lagerauslastung',
        bewegungen: 'Bewegungen'
      }
      return titles[this.showReport] || ''
    },
    auslastung() {
      if (!this.lagerStats.gesamt) return 0
      return Math.round((this.lagerStats.belegt / this.lagerStats.gesamt) * 100)
    }
  },
  async mounted() {
    try {
      const [regionen, arten] = await Promise.all([
        stammdatenAPI.getRegionen(),
        stammdatenAPI.getWeinarten()
      ])
      this.regionen = regionen.data
      this.arten = arten.data
    } catch (err) {
      console.error('Fehler:', err)
    }
  },
  watch: {
    showReport(val) {
      if (val === 'lager') this.loadLagerReport()
    }
  },
  methods: {
    async loadBestandReport() {
      try {
        const res = await reportingAPI.getBestand(this.bestandFilter)
        this.bestandData = res.data
      } catch (err) {
        console.error('Fehler:', err)
      }
    },
    async loadLagerReport() {
      try {
        const res = await reportingAPI.getLager()
        this.lagerStats = res.data
      } catch (err) {
        console.error('Fehler:', err)
      }
    },
    async loadBewegungenReport() {
      try {
        const res = await reportingAPI.getBewegungen(this.bewegungFilter)
        this.bewegungData = res.data
      } catch (err) {
        console.error('Fehler:', err)
      }
    },
    formatDate(d) {
      return new Date(d).toLocaleString('de-DE')
    },
    formatAktion(a) {
      const map = { einlagern: 'Einlagern', entnehmen: 'Entnehmen', umlagern: 'Umlagern' }
      return map[a] || a
    }
  }
}
</script>

<style scoped>
.report-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.report-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.report-card h3 {
  color: #722F37;
  margin-top: 0;
}

.report-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 900px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  color: #722F37;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
}

.filter-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: end;
}

.lager-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.stat-card h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.85rem;
  color: #6c757d;
  text-transform: uppercase;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #722F37;
  margin: 0;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  font-size: 0.8rem;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.badge-einlagern { background: #d4edda; color: #155724; }
.badge-entnehmen { background: #f8d7da; color: #721c24; }
.badge-umlagern { background: #d1ecf1; color: #0c5460; }
</style>