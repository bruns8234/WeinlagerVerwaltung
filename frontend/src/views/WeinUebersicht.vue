<template>
  <div class="wein-uebersicht">
    <div class="page-header">
      <h2>Weine</h2>
      <button class="btn btn-primary" @click="showEditModal(null)">
        + Wein anlegen
      </button>
    </div>

    <!-- Suchfeld -->
    <div class="search-bar">
      <input 
        v-model="suchbegriff"
        placeholder="Suche nach Name, Region, Jahrgang..."
        class="form-input"
        @input="loadWeine"
      />
    </div>

    <!-- Ladezustand -->
    <div v-if="loading" class="loading">Lade Weine...</div>

    <!-- Fehler -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadWeine">Neu laden</button>
    </div>

    <!-- Wein-Tabelle -->
    <div v-else class="wein-table-container">
      <table class="wein-table">
        <thead>
          <tr>
            <p class="text-center">
              <strong>Name</strong>
            </td>
            <th>Region</th>
            <th>Jahrgang</th>
            <th>Art</th>
            <th>Farbe</th>
            <th>Flaschen</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="wein in weine" :key="wein.id">
            <td>{{ wein.name }}</td>
            <td>{{ wein.region?.name || '-' }}</td>
            <td>{{ wein.jahrgang }}</td>
            <td>{{ wein.art?.name || '-' }}</td>
            <td>{{ wein.farbe?.name || '-' }}</td>
            <td>{{ wein.flaschenAnzahl }}</td>
            <td>
              <div class="action-buttons">
                <button class="btn btn-sm btn-info" @click="showEditModal(wein)">Bearbeiten</button>
                <button class="btn btn-sm btn-danger" @click="deleteWein(wein)">Löschen</button>
              </div>
            </td>
          </tr>
          <tr v-if="weine.length === 0">
            <td colspan="7" class="text-center">Keine Weine gefunden</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal zum Anlegen/Bearbeiten -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editMode ? 'Wein bearbeiten' : 'Neuen Wein anlegen' }}</h3>
          <button class="btn-close" @click="closeModal">&times;</button>
        </div>
        
        <form @submit.prevent="saveWein" class="modal-form">
          <div class="form-group">
            <label for="name">Name <span class="required">*</span></label>
            <input v-model="formData.name" id="name" type="text" class="form-input" required />
          </div>

          <div class="form-group">
            <label for="region">Region</label>
            <select v-model="formData.regionId" id="region" class="form-select">
              <option value="">-- Region wählen --</option>
              <option v-for="r in regionen" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="jahrgang">Jahrgang <span class="required">*</span></label>
            <input v-model.number="formData.jahrgang" id="jahrgang" type="number" class="form-input" required />
          </div>

          <div class="form-group">
            <label for="art">Weinart</label>
            <select v-model="formData.artId" id="art" class="form-select">
              <option value="">-- Art wählen --</option>
              <option v-for="a in arten" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="farbe">Farbe</label>
            <select v-model="formData.farbeId" id="farbe" class="form-select">
              <option value="">-- Farbe wählen --</option>
              <option v-for="f in farben" :key="f.id" :value="f.id">{{ f.name }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="flaschenAnzahl">Flaschen <span class="required">*</span></label>
            <input v-model.number="formData.flaschenAnzahl" id="flaschenAnzahl" type="number" min="0" class="form-input" required />
          </div>

          <div class="form-group">
            <label for="beschreibung">Beschreibung</label>
            <textarea v-model="formData.beschreibung" id="beschreibung" class="form-textarea" rows="3"></textarea>
          </div>

          <div class="form-group">
            <label for="ankaufspreis">Ankaufspreis</label>
            <input v-model.number="formData.ankaufspreis" id="ankaufspreis" type="number" step="0.01" min="0" class="form-input" />
          </div>

          <div class="form-group">
            <label for="ankaufsdatum">Ankaufsdatum</label>
            <input v-model="formData.ankaufsdatum" id="ankaufsdatum" type="date" class="form-input" />
          </div>

          <div class="form-group">
            <label for="trinkfertigkeit">Trinkfertigkeit</label>
            <select v-model="formData.trinkfertigkeitId" id="trinkfertigkeit" class="form-select">
              <option value="">-- Stufe wählen --</option>
              <option v-for="s in stufen" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Abbrechen</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Speichere...' : 'Speichern' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { weineAPI, stammdatenAPI } from '../services/api.js'

export default {
  name: 'WeinUebersicht',
  data() {
    return {
      loading: false,
      error: null,
      weine: [],
      suchbegriff: '',
      regionen: [],
      arten: [],
      farben: [],
      stufen: [],
      showModal: false,
      editMode: false,
      saving: false,
      formData: {
        id: null,
        name: '',
        regionId: null,
        jahrgang: new Date().getFullYear(),
        artId: null,
        farbeId: null,
        flaschenAnzahl: 1,
        beschreibung: '',
        ankaufspreis: null,
        ankaufsdatum: '',
        trinkfertigkeitId: null
      }
    }
  },
  async mounted() {
    await Promise.all([
      this.loadWeine(),
      this.loadStammdaten()
    ])
  },
  methods: {
    async loadWeine() {
      this.loading = true
      this.error = null
      try {
        const params = {}
        if (this.suchbegriff) params.suche = this.suchbegriff
        const response = await weineAPI.getAll(params)
        this.weine = response.data
      } catch (err) {
        this.error = 'Fehler beim Laden der Weine: ' + (err.response?.data?.message || err.message)
      } finally {
        this.loading = false
      }
    },

    async loadStammdaten() {
      try {
        const [regionenRes, artenRes, farbenRes, stufenRes] = await Promise.all([
          stammdatenAPI.getRegionen(),
          stammdatenAPI.getArten(),
          stammdatenAPI.getFarben(),
          stammdatenAPI.getStufen()
        ])
        this.regionen = regionenRes.data
        this.arten = artenRes.data
        this.farben = farbenRes.data
        this.stufen = stufenRes.data
      } catch (err) {
        console.error('Fehler beim Laden der Stammdaten:', err)
      }
    },

    showEditModal(wein) {
      if (wein) {
        this.editMode = true
        this.formData = {
          id: wein.id,
          name: wein.name,
          regionId: wein.regionId,
          jahrgang: wein.jahrgang,
          artId: wein.artId,
          farbeId: wein.farbeId,
          flaschenAnzahl: wein.flaschenAnzahl,
          beschreibung: wein.beschreibung || '',
          ankaufspreis: wein.ankaufspreis,
          ankaufsdatum: wein.ankaufsdatum ? wein.ankaufsdatum.split('T')[0] : '',
          trinkfertigkeitId: wein.trinkfertigkeitId
        }
      } else {
        this.editMode = false
        this.formData = {
          id: null,
          name: '',
          regionId: null,
          jahrgang: new Date().getFullYear(),
          artId: null,
          farbeId: null,
          flaschenAnzahl: 1,
          beschreibung: '',
          ankaufspreis: null,
          ankaufsdatum: '',
          trinkfertigkeitId: null
        }
      }
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
    },

    async saveWein() {
      this.saving = true
      try {
        if (this.editMode) {
          await weineAPI.update(this.formData.id, this.formData)
        } else {
          await weineAPI.create(this.formData)
        }
        this.closeModal()
        await this.loadWeine()
      } catch (err) {
        alert('Fehler beim Speichern: ' + (err.response?.data?.message || err.message))
      } finally {
        this.saving = false
      }
    },

    async deleteWein(wein) {
      if (confirm(`Möchtest du "${wein.name}" wirklich löschen?`)) {
        try {
          await weineAPI.delete(wein.id)
          await this.loadWeine()
        } catch (err) {
          alert('Fehler beim Löschen: ' + (err.response?.data?.message || err.message))
        }
      }
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h2 {
  color: #722F37;
  margin: 0;
}

.search-bar {
  margin-bottom: 1.5rem;
}

.wein-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.wein-table {
  width: 100%;
  border-collapse: collapse;
}

.wein-table th,
.wein-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.wein-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

.wein-table tr:hover {
  background: #f8f9fa;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.text-center {
  text-align: center;
}

/* Modal Styles */
.modal-overlay {
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
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  margin: 0;
  color: #722F37;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
}

.modal-form .form-group {
  margin-bottom: 1rem;
}

.modal-form label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  color: #495057;
}

.required {
  color: #dc3545;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #dc3545;
}
</style>