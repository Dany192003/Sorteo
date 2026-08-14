<template>
  <div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ juveniles.length }}</div>
        <div class="stat-label">👥 Juveniles</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ equipos.length }}</div>
        <div class="stat-label">🏆 Equipos</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ totalJugadores }}</div>
        <div class="stat-label">👤 Jugadores</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ grupos.length }}</div>
        <div class="stat-label">📋 Grupos</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ partidosPendientes }}</div>
        <div class="stat-label">⏳ Partidos Pendientes</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ partidosJugados }}</div>
        <div class="stat-label">✅ Partidos Jugados</div>
      </div>
    </div>

    <div class="dashboard-actions">
      <button @click="$emit('cambiarVista', 'juveniles')" class="btn-primary">👥 Gestionar Juveniles</button>
      <button @click="$emit('cambiarVista', 'equipos')" class="btn-secondary">📋 Gestionar Equipos</button>
      <button @click="$emit('cambiarVista', 'jugadores')" class="btn-secondary">👤 Gestionar Jugadores</button>
      <button @click="$emit('generarTorneo')" class="btn-success">🔄 Generar Torneo</button>
      <button @click="$emit('cambiarVista', 'torneo')" class="btn-secondary">🏆 Ver Torneo</button>
      <button @click="$emit('cambiarVista', 'configuracion')" class="btn-secondary">⚙️ Configuración</button>
      <button @click="$emit('vaciarDatos')" class="btn-danger">🗑️ Vaciar BD</button>
      <button @click="$emit('reiniciarTorneo')" class="btn-danger" style="background: linear-gradient(135deg, #f39c12, #e67e22);">🔄 Reiniciar</button>
    </div>

    <div v-if="juveniles.length > 0" class="info-section">
      <h3>📊 Distribución de Equipos por Juvenil</h3>
      <div class="juvenil-stats">
        <div v-for="juvenil in juveniles" :key="juvenil.id" class="juvenil-stat">
          <span class="juvenil-nombre">👤 {{ juvenil.nombre }}</span>
          <span class="juvenil-equipos">{{ juvenil.equipos.length }}</span>
        </div>
      </div>
    </div>

    <div v-if="grupos.length > 0" class="torneo-preview">
      <h2>📋 Vista previa del torneo</h2>
      <div class="grupos-container">
        <div v-for="(grupo, idx) in grupos" :key="idx" class="grupo-card">
          <h3>Grupo {{ String.fromCharCode(65 + idx) }}</h3>
          <div v-for="equipo in grupo.equipos" :key="equipo.id" class="equipo-item">⚽ {{ equipo.nombre }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  props: {
    juveniles: Array,
    equipos: Array,
    grupos: Array,
    totalJugadores: Number,
    partidos: Array
  },
  emits: ['cambiarVista', 'generarTorneo', 'vaciarDatos', 'reiniciarTorneo'],
  computed: {
    partidosPendientes() {
      return this.partidos ? this.partidos.filter(p => !p.jugado).length : 0
    },
    partidosJugados() {
      return this.partidos ? this.partidos.filter(p => p.jugado).length : 0
    }
  }
}
</script>
