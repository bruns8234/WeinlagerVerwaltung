<template>
  <div class="lagerung">
    <h2>Lagerung</h2>

    <!-- Tabs -->
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'einlagern' }" 
        @click="activeTab = 'einlagern'"
      >Einlagern</button>
      <button 
        :class="{ active: activeTab === 'entnehmen' }" 
        @click="activeTab = 'entnehmen'"
      >Entnehmen</button>
      <button 
        :class="{ active: activeTab === 'historie' }" 
        @click="activeTab = 'historie'"
      >Historie</button>
    </div>

    <!-- Einlagern -->
    <div v-if="activeTab === 'einlagern'" class="tab-content">
      <div class="form-card">
        <h3>Wein einlagern</h3>
        
        <div class="form-group">
          <label for="wein">Wein <span class="required">*</span></label>
          <select v-model="einlagerFormData.weinId" id="wein" class="form-select" required>
            <option value="">-- Wein wählen --</option>
            <option v-for="w in weine" :key="w.id" :value="w.id">
              {{ w.name }} ({{ w.jahrgang }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="lagerplatz">Lagerplatz <span class="required">*</span></label>
          <select v-model="einlagerFormData.lagerplatzId" id="lagerplatz" class="form-select" required>
            <option value="">-- Lagerplatz wählen --</option>
            <option v-for="p in freiePlaetze" :key="p.id" :value="p.id">
              {{ p.regal }}-{{ p.ebene }}-{{ p.position }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="anzahl">Anzahl Flaschen <span class="required">*</span></label>
          <input 
            v-model.number="einlagerFormData.anzahl" 
            id="anzahl" 
            type="number" 
            min="1" 
            class="form-input" 
            required 
          />
        </div>

        <div class="form-group">
          <label for="notiz">Notiz (optional)</label>
          <textarea v-model="einlagerFormData.notiz" id="notiz" class="form-textarea" rows="2"></textarea>
        </div>

        <div class="form-actions">
          <button class="btn btn-primary" @click="einlagern" :disabled="saving">
            {{ saving ? 'Einlagere...' : 'Einlagern' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Entnehmen -->
    <div v-if="activeTab === 'entnehmen'" class="tab-content">
      <div class="form-card">
        <h3>Flaschen entnehmen</h3>
        
        <div class="form-group">
          <label for="lagerung">Lagerung <span class="required">*</span></label>
          <select v-model="entnahmeFormData.lagerungId" id="lagerung" class="form-select" required @change="onLagerungSelect">
            <option value="">-- Lagerung wählen --</option>
            <option v-for="l in aktuelleLagerungen" :key="l.id" :value="l.id">
              {{ l.weinName }} → {{ l.lagerplatz }} ({{ l.flaschenAnzahl }} Flaschen)
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="entnahmeAnzahl">Anzahl Flaschen <span class="required">*</span></label>
          <input 
            v-model.number="entnahmeFormData.anzahl" 
            id="entnahmeAnzahl" 
            type="number" 
            min="1"
            :max="maxEntnahme"
            class="form-input" 
            required 
          />
          <small>Maximal: {{ maxEntnahme }} Flaschen</small>
        </div>

        <div class="form-group">
          <label for="entnahmeNotiz">Notiz (optional)</label>
          <textarea v-model="entnahmeFormData.notiz" id="entnahmeNotiz" class="form-textarea" rows="2"></textarea>
        </div>

        <div class="form-actions">
          <button class="btn btn-danger" @click="entnehmen" :disabled="saving">
            {{ saving ? 'Entnehme...' : 'Entnehmen' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Historie -->
    <div v-if="activeTab === 'historie'" class="tab-content">
      <div class="filter-bar">
        <input 
          v-model="historieSuche"
          placeholder="Suche..."
          class="form-input"
          @input="loadHistorie"
        />
        <select v-model="historieFilter" class="form-select" @change="loadHistorie">
          <option value="">Alle Aktionen</option>
          <option value="einlagern">Einlagerungen</option>
          <option value="entnehmen">Entnahmen</option>
          <option value="umlagern">Umlagerungen</option>
        </select>
      </div>

      <div class="historie-table">
        <table>
          <thead>
            <tr>
              <th>Datum</th>
              <th>Aktion</th>
              <th>Wein</th>
              <th>Lagerplatz</th>
              <th>Anzahl</th>
              <th>Notiz</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in historie" :key="entry.id">
              <td>{{ formatDate(entry.datum) }}</td>
              <td>
                <span :class="['badge', 'badge-' + entry.aktion]">
                  {{ formatAktion(entry.aktion) }}
                </span>
              </td>
              <td>{{ entry.weinName }}</td>
              <td>{{ entry.lagerplatz }}</td>
              <td>{{ entry.anzahl }}</td>
              <td>{{ entry.notiz || '-' }}</td>
            </tr>
            <tr v-if="historie.length === 0">
              <td colspan="6" class="text-center">Keine Einträge gefunden</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { lagerungAPI, weineAPI, lagerplaetzeAPI } from '../services/api.js'

export default {
  name: 'Lagerung',
  data() {
    return {
      activeTab: 'einlagern',
      saving: false,
      weine: [],
      freiePlaetze: [],
      aktuelleLagerungen: [],
      historie: [],
      historieSuche: '',
      historieFilter: '',
      einlagerFormData: {
        weinId: null,
        lagerplatzId: null,
        anzahl: 1,
        notiz: ''
      },
      entnahmeFormData: {
        lagerungId: null,
        anzahl: 1,
        notiz: ''
      },
      maxEntnahme: 0
    }
  },
  async mounted() {
    await this.loadDaten()
  },
  methods: {
    async loadDaten() {
      try {
        const [weineRes, plaetzeRes, lagerungRes, historieRes] = await Promise.all([
          weineAPI.getAll(),
          lagerplaetzeAPI.getFreie(),
          lagerungAPI.getActive(),
          lagerungAPI.getHistorie()
        ])
        this.weine = weineRes.data
        this.freiePlaetze = plaetzeRes.data
        this.aktuelleLagerungen = lagerungRes.data
        this.historie = historieRes.data
      } catch (err) {
        console.error('Fehler beim Laden:', err)
      }
    },

    async loadHistorie() {
      try {
        const params = {}
        if (this.historieSuche) params.suche = this.historieSuche
        if (this.historieFilter) params.aktion = this.historieFilter
        const res = await lagerungAPI.getHistorie(params)
        this.historie = res.data
      } catch (err) {
        console.error('Fehler beim Laden der Historie:', err)
      }
    },

    onLagerungSelect() {
      const lagerung = this.aktuelleLagerungen.find(l => l.id === this.entnahmeFormData.lagerungId)
      this.maxEntnahme = lagerung?.flaschenAnzahl || 0
      this.entnahmeFormData.anzahl = 1
    },

    async einlagern() {
      if (!this.einlagerFormData.weinId || !this.einlagerFormData.lagerplatzId || !this.einlagerFormData.anzahl) {
        alert('Bitte alle Pflichtfelder ausfüllen')
        return
      }

      this.saving = true
      try {
        await lagerungAPI.einlagern(this.einlagerFormData)
        this.einlagerFormData = {
          weinId: null,
          lagerplatzId: null,
          anzahl: 1,
          notiz: ''
        }
        await this.loadDaten()
      } catch (err) {
        alert('Fehler beim Einlagern: ' + (err.response?.data?.message || err.message))
      } finally {
        this.saving = false
      }
    },

    async entnehmen() {
      if (!this.entnahmeFormData.lagerungId || !this.entnahmeFormData.anzahl) {
        alert('Bitte alle Pflichtfelder ausfüllen')
        return
      }

      if (this.entnahmeFormData.anzahl > this.maxEntnahme) {
        alert('Anzahl überschreitet verfügbare Flaschen')
        return
      }

      this.saving = true
      try {
        await lagerungAPI.entnehmen(this.entnahmeFormData)
        this.entnahmeFormData = {
          lagerungId: null,
          anzahl: 1,
          notiz: ''
        }
        this.maxEntnahme = 0
        await this.loadDaten()
      } catch (err) {
        alert('Fehler beim Entnehmen: ' + (err.response?.data?.message || err.message))
      } finally {
        this.saving = false
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString('de-DE')
    },

    formatAktion(aktion) {
      const map = {
        einlagern: 'Einlagern',
        entnehmen: 'Entnehmen',
        umlagern: 'Umlagern'
      }
      return map[aktion] || aktion
    }
  }
}
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.tabs button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.2s ease;
}

.tabs button:hover {
  color: #722F37;
}

.tabs button.active {
  color: #722F37;
  border-bottom-color: #722F37;
}

.tab-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.form-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-width: 600px;
}

.form-card h3 {
  margin-top: 0;
  color: #722F37;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  color: #495057;
}

.required {
  color: #dc3545;
}

.form-group small {
  color: #6c757d;
  font-size: 0.8rem;
}

.form-actions {
  margin-top: 1.5rem;
}

.filter-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.historie-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow-x: auto;
}

.historie-table table {
  width: 100%;
  border-collapse: collapse;
}

.historie-table th,
.historie-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.historie-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.badge-einlagern {
  background: #d4edda;
  color: #155724;
}

.badge-entnehmen {
  background: #f8d7da;
  color: #721c24;
}

.badge-umlagern {
  background: #d1ecf1;
  color: #0c5460;
}

.text-center {
  text-align: center;
}
</style>