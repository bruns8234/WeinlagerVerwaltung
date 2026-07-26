<template>
  <div class="einstellungen">
    <h2>Einstellungen</h2>

    <div class="tabs">
      <button :class="{ active: activeTab === 'stammdaten' }" @click="activeTab = 'stammdaten'">Stammdaten</button>
      <button :class="{ active: activeTab === 'backup' }" @click="activeTab = 'backup'">Backup</button>
    </div>

    <!-- Stammdaten -->
    <div v-if="activeTab === 'stammdaten'" class="tab-content">
      <div class="stammdaten-grid">
        <div class="stammdaten-card">
          <h3>Weinarten</h3>
          <div class="stammdaten-list">
            <div v-for="art in weinarten" :key="art.id" class="list-item">
              {{ art.bezeichnung }}
            </div>
          </div>
        </div>

        <div class="stammdaten-card">
          <h3>Farben</h3>
          <div class="stammdaten-list">
            <div v-for="farbe in farben" :key="farbe.id" class="list-item">
              {{ farbe.bezeichnung }}
            </div>
          </div>
        </div>

        <div class="stammdaten-card">
          <h3>Reifungsstufen</h3>
          <div class="stammdaten-list">
            <div v-for="stufe in stufen" :key="stufe.id" class="list-item">
              {{ stufe.bezeichnung }}
            </div>
          </div>
        </div>

        <div class="stammdaten-card">
          <h3>Regionen</h3>
          <div class="stammdaten-list">
            <div v-for="region in regionen" :key="region.id" class="list-item">
              {{ region.bezeichnung }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Backup -->
    <div v-if="activeTab === 'backup'" class="tab-content">
      <div class="backup-card">
        <h3>Datenbank-Backup</h3>
        <p>Sichern Sie Ihre Weinkeller-Datenbank.</p>
        <button class="btn btn-primary" @click="createBackup" :disabled="backuping">
          {{ backuping ? 'Erstelle Backup...' : 'Backup erstellen' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { stammdatenMasterAPI, backupAPI } from '../services/api.js'

export default {
  name: 'Einstellungen',
  data() {
    return {
      activeTab: 'stammdaten',
      weinarten: [],
      farben: [],
      stufen: [],
      regionen: [],
      backuping: false
    }
  },
  async mounted() {
    await this.loadStammdaten()
  },
  methods: {
    async loadStammdaten() {
      try {
        const [arten, farben, stufen, regionen] = await Promise.all([
          stammdatenMasterAPI.getWeinarten(),
          stammdatenMasterAPI.getFarben(),
          stammdatenMasterAPI.getStufen(),
          stammdatenMasterAPI.getRegionen()
        ])
        this.weinarten = arten.data
        this.farben = farben.data
        this.stufen = stufen.data
        this.regionen = regionen.data
      } catch (err) {
        console.error('Failed to load master data:', err)
      }
    },

    async createBackup() {
      this.backuping = true
      try {
        const response = await backupAPI.exportAlles()
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'weinlager_backup.json')
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        alert('Backup erfolgreich erstellt!')
      } catch (err) {
        alert('Fehler beim Erstellen des Backups: ' + (err.response?.data?.message || err.message))
      } finally {
        this.backuping = false
      }
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
}

.tabs button.active {
  color: #722F37;
  border-bottom-color: #722F37;
}

.stammdaten-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stammdaten-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stammdaten-card h3 {
  margin-top: 0;
  color: #722F37;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.stammdaten-list {
  max-height: 300px;
  overflow-y: auto;
}

.list-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f8f9fa;
}

.backup-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-width: 500px;
}

.backup-card h3 {
  color: #722F37;
}
</style>