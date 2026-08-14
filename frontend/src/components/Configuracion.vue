<template>
  <div>
    <div class="section-header">
      <h2>⚙️ Configuración del Torneo</h2>
    </div>

    <!-- Configuración de Puntos -->
    <div class="config-card">
      <h3>🏆 Sistema de Puntos</h3>
      <div class="form-row">
        <div class="form-group">
          <label>Puntos por Ganar</label>
          <input v-model.number="puntosGanado" type="number" min="1" max="10" class="input">
        </div>
        <div class="form-group">
          <label>Puntos por Empate</label>
          <input v-model.number="puntosEmpate" type="number" min="0" max="5" class="input">
        </div>
        <div class="form-group">
          <label>Puntos por Perder</label>
          <input v-model.number="puntosPerdido" type="number" min="0" max="5" class="input">
        </div>
        <div class="form-group" style="display: flex; align-items: flex-end;">
          <button @click="guardarPuntos" class="btn-success">💾 Guardar Puntos</button>
        </div>
      </div>
      <div class="info-message" style="margin-top: 10px;">
        ℹ️ Actualmente: Ganar = <strong>{{ puntosGanado }}</strong> pts | Empate = <strong>{{ puntosEmpate }}</strong> pts | Perder = <strong>{{ puntosPerdido }}</strong> pts
      </div>
    </div>

    <!-- Configuración de Enfrentamientos -->
    <div class="config-card">
      <h3>👥 Reglas de Enfrentamiento</h3>
      
      <div class="config-option">
        <div class="option-info">
          <h4>Permitir equipos del mismo juvenil en fase de grupos</h4>
          <p class="option-desc">
            Si está desactivado, los equipos del mismo juvenil NO se enfrentarán en la fase de grupos.
            Esto garantiza que cada juvenil tenga equipos en diferentes grupos.
          </p>
        </div>
        <div class="option-toggle">
          <label class="switch">
            <input 
              type="checkbox" 
              v-model="permitirMismoJuvenil"
              @change="guardarConfiguracion"
            >
            <span class="slider"></span>
          </label>
          <span class="toggle-label">{{ permitirMismoJuvenil ? '✅ Permitido' : '🚫 No permitido' }}</span>
        </div>
      </div>

      <div class="info-box">
        <span class="info-icon">ℹ️</span>
        <span class="info-text">
          {{ permitirMismoJuvenil ? 
            'Los equipos del mismo juvenil PODRÁN enfrentarse en fase de grupos.' : 
            'Los equipos del mismo juvenil NO podrán enfrentarse en fase de grupos.' }}
        </span>
      </div>
    </div>

    <!-- Resumen -->
    <div class="config-card">
      <h3>📊 Resumen de Configuración</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="status-label">Puntos por Ganar</span>
          <span class="status-value">{{ puntosGanado }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Puntos por Empate</span>
          <span class="status-value">{{ puntosEmpate }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Puntos por Perder</span>
          <span class="status-value">{{ puntosPerdido }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Mismo Juvenil en Grupos</span>
          <span class="status-value" :style="{ color: permitirMismoJuvenil ? '#48cae4' : '#00b4d8' }">
            {{ permitirMismoJuvenil ? '✅ Permitido' : '🚫 No permitido' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

export default {
  name: 'Configuracion',
  props: {
    configuracion: {
      type: Object,
      default: () => ({ 
        permitir_mismo_juvenil: false,
        puntos_ganado: 3,
        puntos_empate: 1,
        puntos_perdido: 0
      })
    }
  },
  data() {
    return {
      permitirMismoJuvenil: false,
      puntosGanado: 3,
      puntosEmpate: 1,
      puntosPerdido: 0,
      mensaje: ''
    }
  },
  watch: {
    configuracion: {
      handler(val) {
        this.permitirMismoJuvenil = val?.permitir_mismo_juvenil || false
        this.puntosGanado = val?.puntos_ganado || 3
        this.puntosEmpate = val?.puntos_empate || 1
        this.puntosPerdido = val?.puntos_perdido || 0
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    async guardarPuntos() {
      try {
        await api.post('/configuracion', {
          puntos_ganado: this.puntosGanado,
          puntos_empate: this.puntosEmpate,
          puntos_perdido: this.puntosPerdido
        })
        this.mensaje = '✅ Configuración de puntos guardada correctamente'
        setTimeout(() => this.mensaje = '', 3000)
        this.$emit('guardarConfiguracion', {
          permitir_mismo_juvenil: this.permitirMismoJuvenil,
          puntos_ganado: this.puntosGanado,
          puntos_empate: this.puntosEmpate,
          puntos_perdido: this.puntosPerdido
        })
      } catch (error) {
        console.error('Error:', error)
        this.mensaje = '❌ Error al guardar configuración de puntos'
      }
    },
    async guardarConfiguracion() {
      try {
        await api.post('/configuracion', {
          permitir_mismo_juvenil: this.permitirMismoJuvenil,
          puntos_ganado: this.puntosGanado,
          puntos_empate: this.puntosEmpate,
          puntos_perdido: this.puntosPerdido
        })
        this.mensaje = '✅ Configuración guardada correctamente'
        setTimeout(() => this.mensaje = '', 3000)
        this.$emit('guardarConfiguracion', {
          permitir_mismo_juvenil: this.permitirMismoJuvenil,
          puntos_ganado: this.puntosGanado,
          puntos_empate: this.puntosEmpate,
          puntos_perdido: this.puntosPerdido
        })
      } catch (error) {
        console.error('Error:', error)
        this.mensaje = '❌ Error al guardar configuración'
      }
    }
  }
}
</script>

<style scoped>
.config-card {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.config-card h3 {
  color: #48cae4;
  font-size: 1.1rem;
  margin-bottom: 20px;
  font-weight: 600;
}

.form-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.form-group {
  flex: 1;
  min-width: 120px;
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
  padding: 10px 14px;
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

.info-message {
  background: rgba(72, 202, 228, 0.1);
  border: 1px solid rgba(72, 202, 228, 0.15);
  padding: 10px 18px;
  border-radius: 8px;
  color: #48cae4;
  font-size: 0.9rem;
}

.config-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.option-info {
  flex: 1;
  min-width: 200px;
}

.option-info h4 {
  color: #e8f0fe;
  font-size: 1rem;
  margin-bottom: 5px;
}

.option-desc {
  color: #8ecae6;
  font-size: 0.85rem;
  line-height: 1.4;
}

.option-toggle {
  display: flex;
  align-items: center;
  gap: 15px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #555;
  transition: .4s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.toggle-label {
  color: #e8f0fe;
  font-weight: 600;
  font-size: 0.9rem;
  min-width: 100px;
}

.info-box {
  margin-top: 15px;
  padding: 12px 16px;
  background: rgba(72, 202, 228, 0.08);
  border: 1px solid rgba(72, 202, 228, 0.15);
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-icon {
  font-size: 1.2rem;
}

.info-text {
  color: #48cae4;
  font-size: 0.9rem;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.status-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 15px;
  border-radius: 10px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.status-label {
  display: block;
  color: #8ecae6;
  font-size: 0.8rem;
  margin-bottom: 5px;
}

.status-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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

@media (max-width: 768px) {
  .config-option {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .option-toggle {
    width: 100%;
    justify-content: space-between;
  }
  
  .status-grid {
    grid-template-columns: 1fr 1fr;
  }

  .form-row {
    flex-direction: column;
  }

  .form-group {
    min-width: 100%;
  }
}
</style>
