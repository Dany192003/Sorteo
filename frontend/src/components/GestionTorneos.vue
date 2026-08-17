<template>
  <div>
    <div class="section-header">
      <h2>📁 Gestión de Torneos</h2>
    </div>

    <div class="form-card">
      <div class="form-row">
        <div class="form-group">
          <label>Nombre del nuevo torneo</label>
          <input v-model="nuevoTorneo" placeholder="Ej: Torneo 2025" class="input" @keyup.enter="crearTorneo">
        </div>
        <div class="form-group" style="display: flex; align-items: flex-end;">
          <button @click="crearTorneo" class="btn-success">➕ Crear Torneo</button>
        </div>
      </div>
    </div>

    <div class="info-section">
      <h3>📋 Torneos disponibles</h3>
      <div v-if="torneos.length === 0" class="empty-message">
        No hay torneos creados aún
      </div>
      <div v-for="torneo in torneos" :key="torneo.nombre" class="torneo-item" :class="{ 'torneo-activo': torneo.nombre === torneoActual }">
        <div class="torneo-info">
          <span class="torneo-nombre">{{ torneo.nombre }}</span>
          <span v-if="torneo.nombre === torneoActual" class="torneo-badge">✅ Actual</span>
        </div>
        <div class="torneo-actions">
          <button v-if="torneo.nombre !== torneoActual" @click="cambiarTorneo(torneo.nombre)" class="btn-small-success">📂 Cargar</button>
          <button @click="eliminarTorneo(torneo.nombre)" class="btn-small-danger">🗑️</button>
        </div>
      </div>
    </div>

    <div class="info-box">
      <span class="info-icon">ℹ️</span>
      <span class="info-text">
        Cada torneo tiene su propia base de datos independiente.
        Los datos se guardan automáticamente en archivos JSON separados.
      </span>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = 'https://torneo-futbol-juvenil.onrender.com/api'
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

export default {
  name: 'GestionTorneos',
  props: {
    torneoActual: String
  },
  data() {
    return {
      torneos: [],
      nuevoTorneo: ''
    }
  },
  emits: ['cambiarTorneo', 'crearTorneo', 'eliminarTorneo', 'recargar'],
  mounted() {
    this.cargarTorneos()
  },
  methods: {
    async cargarTorneos() {
      try {
        const response = await api.get('/torneos')
        this.torneos = response.data
      } catch (error) {
        console.error('Error cargando torneos:', error)
        alert('❌ Error al cargar torneos')
      }
    },
    async crearTorneo() {
      if (!this.nuevoTorneo.trim()) {
        alert('Ingresa un nombre para el torneo')
        return
      }
      this.$emit('crearTorneo', this.nuevoTorneo.trim())
      this.nuevoTorneo = ''
      await this.cargarTorneos()
    },
    async cambiarTorneo(nombre) {
      this.$emit('cambiarTorneo', nombre)
      await this.cargarTorneos()
    },
    async eliminarTorneo(nombre) {
      this.$emit('eliminarTorneo', nombre)
      await this.cargarTorneos()
    }
  }
}
</script>

<style scoped>
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-header h2 {
  font-size: 1.6rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.form-card {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.form-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.form-group {
  flex: 1;
  min-width: 200px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.85rem;
  color: #8ecae6;
  font-weight: 500;
}

.input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  color: #e8f0fe;
  font-size: 14px;
  transition: all 0.3s ease;
}

.input:focus {
  outline: none;
  border-color: #2193b0;
  box-shadow: 0 0 0 3px rgba(33, 147, 176, 0.15);
}

.btn-success {
  background: linear-gradient(135deg, #00b4d8, #0077b6);
  color: #fff;
  padding: 10px 28px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 25px rgba(0, 180, 216, 0.4);
}

.btn-small-success {
  padding: 5px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  background: #00b4d8;
  color: #fff;
}

.btn-small-success:hover {
  background: #0077b6;
  transform: scale(1.05);
}

.btn-small-danger {
  padding: 5px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  background: #e63946;
  color: #fff;
}

.btn-small-danger:hover {
  background: #c1121f;
  transform: scale(1.05);
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

.torneo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  margin: 8px 0;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

.torneo-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(33, 147, 176, 0.2);
}

.torneo-activo {
  border-color: rgba(0, 180, 216, 0.3);
  background: rgba(0, 180, 216, 0.05);
}

.torneo-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.torneo-nombre {
  font-weight: 600;
  font-size: 1rem;
}

.torneo-badge {
  font-size: 0.65rem;
  background: #00b4d8;
  padding: 2px 10px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
}

.torneo-actions {
  display: flex;
  gap: 8px;
}

.empty-message {
  text-align: center;
  color: #7f8c8d;
  padding: 30px;
  font-style: italic;
}

.info-box {
  margin-top: 20px;
  padding: 15px 20px;
  background: rgba(72, 202, 228, 0.08);
  border: 1px solid rgba(72, 202, 228, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-icon {
  font-size: 1.2rem;
}

.info-text {
  color: #48cae4;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
  }
  
  .form-group {
    min-width: 100%;
  }
  
  .torneo-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .torneo-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
