import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Stammdaten (Weine)
export const stammdatenAPI = {
  getAll: () => api.get('/stammdaten'),
  getById: (id) => api.get(`/stammdaten/${id}`),
  create: (data) => api.post('/stammdaten', data),
  update: (id, data) => api.put(`/stammdaten/${id}`, data),
  delete: (id) => api.delete(`/stammdaten/${id}`),
  search: (params) => api.get('/stammdaten/search', { params })
}

// Lagerplaetze
export const lagerplaetzeAPI = {
  getAll: () => api.get('/lagerplaetze'),
  getById: (id) => api.get(`/lagerplaetze/${id}`),
  create: (data) => api.post('/lagerplaetze', data),
  update: (id, data) => api.put(`/lagerplaetze/${id}`, data),
  delete: (id) => api.delete(`/lagerplaetze/${id}`),
  getVerfuegbar: () => api.get('/lagerplaetze/verfuegbar'),
  getBelegt: () => api.get('/lagerplaetze/belegt')
}

// Stammdaten Master (Arten, Farben, Stufen, Regionen) - Alias für Einstellungen
export const stammdatenMasterAPI = {
  getWeinarten: () => api.get('/master/arten'),
  getFarben: () => api.get('/master/farben'),
  getStufen: () => api.get('/master/stufen'),
  getRegionen: () => api.get('/master/regionen'),
}

// Master Data (Arten, Farben, Stufen, Regionen)
export const masterDataAPI = {
  getArten: () => api.get('/master/arten'),
  getFarben: () => api.get('/master/farben'),
  getStufen: () => api.get('/master/stufen'),
  getRegionen: () => api.get('/master/regionen'),
  createArt: (data) => api.post('/master/arten', data),
  createFarbe: (data) => api.post('/master/farben', data),
  createStufe: (data) => api.post('/master/stufen', data),
  createRegion: (data) => api.post('/master/regionen', data),
  updateArt: (id, data) => api.put(`/master/arten/${id}`, data),
  updateFarbe: (id, data) => api.put(`/master/farben/${id}`, data),
  updateStufe: (id, data) => api.put(`/master/stufen/${id}`, data),
  updateRegion: (id, data) => api.put(`/master/regionen/${id}`, data),
  deleteArt: (id) => api.delete(`/master/arten/${id}`),
  deleteFarbe: (id) => api.delete(`/master/farben/${id}`),
  deleteStufe: (id) => api.delete(`/master/stufen/${id}`),
  deleteRegion: (id) => api.delete(`/master/regionen/${id}`)
}

// Lagerung (Bestand/Operationen)
export const lagerungAPI = {
  getAll: () => api.get('/lagerung'),
  getById: (id) => api.get(`/lagerung/${id}`),
  create: (data) => api.post('/lagerung', data),
  update: (id, data) => api.put(`/lagerung/${id}`, data),
  delete: (id) => api.delete(`/lagerung/${id}`),
  einlagern: (data) => api.post('/lagerung/einlagern', data),
  auslagern: (data) => api.post('/lagerung/auslagern', data),
  umlagern: (data) => api.post('/lagerung/umlagern', data),
  getHistorie: (weinId) => api.get(`/lagerung/historie/${weinId}`)
}

// Reporting
export const reportingAPI = {
  getUebersicht: () => api.get('/reporting/uebersicht'),
  getBestandswert: () => api.get('/reporting/bestandswert'),
  getAlterungsanalyse: () => api.get('/reporting/alterungsanalyse'),
  getLagerauslastung: () => api.get('/reporting/lagerauslastung'),
  exportCsv: (params) => api.get('/reporting/export/csv', { params, responseType: 'blob' }),
  getBestand: (params) => api.get('/reporting/bestand', { params }),
  getLager: () => api.get('/reporting/lager'),
  getBewegungen: (params) => api.get('/reporting/bewegungen', { params })
}

// Backup
export const backupAPI = {
  exportAlles: () => api.get('/backup/export/alles', { responseType: 'blob' }),
  importAlles: (data, replace = false) => api.post(`/backup/import/alles?replace=${replace}`, data),
  exportStammdaten: () => api.get('/backup/export/stammdaten/json', { responseType: 'blob' }),
  importStammdaten: (data) => api.post('/backup/import/stammdaten/json', data)
}

export default api