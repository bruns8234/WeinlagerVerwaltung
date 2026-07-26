<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">🍷 Weinlager Verwaltung</h1>
        <nav class="app-nav">
          <router-link to="/" class="nav-link">Dashboard</router-link>
          <router-link to="/weine" class="nav-link">Weine</router-link>
          <router-link to="/lager" class="nav-link">Lagerstatus</router-link>
          <router-link to="/lagerung" class="nav-link">Lagerung</router-link>
          <router-link to="/stammdaten" class="nav-link">Stammdaten</router-link>
          <router-link to="/backup" class="nav-link">Backup</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>Weinlager Verwaltung &copy; {{ new Date().getFullYear() }}</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'MainLayout'
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #722F37 0%, #4A1C23 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.app-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.app-nav {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 500;
}

.app-main {
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.app-footer {
  background: #f8f9fa;
  padding: 1rem 2rem;
  text-align: center;
  color: #6c757d;
  font-size: 0.875rem;
  border-top: 1px solid #e9ecef;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .app-nav {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .nav-link {
    display: block;
    text-align: left;
  }
}
</style>