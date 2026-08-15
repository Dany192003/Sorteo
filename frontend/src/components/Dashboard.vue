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
        <div class="stat-label">⏳ Pendientes</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ partidosJugados }}</div>
        <div class="stat-label">✅ Jugados</div>
      </div>
    </div>

    <div class="dashboard-actions">
      <button @click="$emit('generarTorneo')" class="btn-success">🔄 Generar Torneo</button>
      <button @click="$emit('reiniciarResultados')" class="btn-warning">🔄 Reiniciar Resultados</button>
      <button @click="$emit('vaciarDatos')" class="btn-danger">🗑️ Vaciar</button>
      <button @click="$emit('reiniciarTorneo')" class="btn-danger" style="background: linear-gradient(135deg, #e63946, #c1121f);">🔄 Reiniciar</button>
    </div>

    <div v-if="grupos.length > 0" class="info-section">
      <h3>📊 Tabla de Posiciones por Grupo</h3>
      <p style="color: #8ecae6; font-size: 0.85rem; margin-bottom: 15px;">
        ⚡ Actualizado automáticamente con cada resultado registrado
      </p>
      
      <div v-for="grupo in grupos" :key="grupo.nombre" class="grupo-tabla">
        <h4>{{ grupo.nombre }}</h4>
        <div class="tabla-container">
          <table class="tabla-posiciones">
            <thead>
              <tr>
                <th>#</th>
                <th>Equipo</th>
                <th>PJ</th>
                <th>PG</th>
                <th>PE</th>
                <th>PP</th>
                <th>GF</th>
                <th>GC</th>
                <th>DG</th>
                <th>PTS</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(equipo, index) in getEquiposOrdenados(grupo.equipos)" :key="equipo.id">
                <td>{{ index + 1 }}</td>
                <td><strong>{{ equipo.nombre }}</strong></td>
                <td>{{ equipo.ganados + equipo.empatados + equipo.perdidos }}</td>
                <td>{{ equipo.ganados }}</td>
                <td>{{ equipo.empatados }}</td>
                <td>{{ equipo.perdidos }}</td>
                <td>{{ equipo.goles_favor }}</td>
                <td>{{ equipo.goles_contra }}</td>
                <td>{{ equipo.goles_favor - equipo.goles_contra }}</td>
                <td class="puntos">{{ equipo.puntos }}</td>
                <td>
                  <span v-if="index < 2" class="clasificado-badge">✅ Clasificado</span>
                  <span v-else class="eliminado-badge">❌ Eliminado</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
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
  emits: ['cambiarVista', 'generarTorneo', 'vaciarDatos', 'reiniciarTorneo', 'reiniciarResultados'],
  computed: {
    partidosPendientes() {
      return this.partidos ? this.partidos.filter(p => !p.jugado).length : 0
    },
    partidosJugados() {
      return this.partidos ? this.partidos.filter(p => p.jugado).length : 0
    }
  },
  methods: {
    getEquiposOrdenados(equipos) {
      return [...equipos].sort((a, b) => {
        if (b.puntos !== a.puntos) return b.puntos - a.puntos
        const dgA = a.goles_favor - a.goles_contra
        const dgB = b.goles_favor - b.goles_contra
        if (dgB !== dgA) return dgB - dgA
        return b.goles_favor - a.goles_favor
      })
    },
    getJuvenilNombre(juvenilId) {
      const juvenil = this.juveniles.find(j => j.id === juvenilId)
      return juvenil ? juvenil.nombre : 'Sin asignar'
    }
  }
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.04);
  padding: 15px;
  border-radius: 12px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 0.8rem;
  color: #8ecae6;
}

.dashboard-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 15px 0;
}

.btn-success {
  background: linear-gradient(135deg, #00b4d8, #0077b6);
  color: #fff;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 180, 216, 0.4);
}

.btn-warning {
  background: linear-gradient(135deg, #f39c12, #e67e22);
  color: #fff;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.btn-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(243, 156, 18, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #e63946, #c1121f);
  color: #fff;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(230, 57, 70, 0.4);
}

.info-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 20px;
  margin: 20px 0;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.info-section h3 {
  color: #8ecae6;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.grupo-tabla {
  margin: 20px 0;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.grupo-tabla h4 {
  color: #48cae4;
  margin-bottom: 10px;
  font-size: 1rem;
  font-weight: 700;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.tabla-container {
  overflow-x: auto;
}

.tabla-posiciones {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  overflow: hidden;
}

.tabla-posiciones th {
  background: rgba(33, 147, 176, 0.15);
  padding: 10px 8px;
  text-align: center;
  font-weight: 600;
  color: #8ecae6;
  border-bottom: 1px solid rgba(33, 147, 176, 0.15);
}

.tabla-posiciones td {
  padding: 8px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.tabla-posiciones tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.puntos {
  font-weight: 700;
  color: #48cae4;
  font-size: 1rem;
}

.clasificado-badge {
  font-size: 0.6rem;
  background: #00b4d8;
  padding: 2px 8px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
}

.eliminado-badge {
  font-size: 0.6rem;
  background: #e63946;
  padding: 2px 8px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
}

.juvenil-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.juvenil-stat {
  background: rgba(255, 255, 255, 0.04);
  padding: 10px 15px;
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.juvenil-nombre {
  font-weight: 600;
}

.juvenil-equipos {
  background: rgba(33, 147, 176, 0.15);
  padding: 3px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #8ecae6;
}

.grupos-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.grupo-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.grupo-card h3 {
  text-align: center;
  color: #48cae4;
  margin-bottom: 10px;
  font-size: 1rem;
  font-weight: 700;
}

.equipo-item {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  margin: 4px 0;
  font-size: 0.85rem;
  border-left: 3px solid #2193b0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.torneo-preview {
  margin-top: 20px;
}

.torneo-preview h2 {
  font-size: 1.1rem;
  color: #8ecae6;
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .dashboard-actions {
    flex-direction: column;
  }

  .dashboard-actions button {
    width: 100%;
  }

  .tabla-posiciones {
    font-size: 0.75rem;
  }

  .tabla-posiciones th,
  .tabla-posiciones td {
    padding: 5px 4px;
  }
}
</style>
