<template>
  <div>
    <div class="section-header">
      <h2>⚙️ Configuración del Torneo</h2>
    </div>

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
              @change="guardar"
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

    <div class="config-card">
      <h3>📊 Estado del Torneo</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="status-label">Total de equipos</span>
          <span class="status-value">{{ totalEquipos }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Total de juveniles</span>
          <span class="status-value">{{ totalJuveniles }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Grupos creados</span>
          <span class="status-value">{{ totalGrupos }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Configuración actual</span>
          <span class="status-value" :style="{ color: permitirMismoJuvenil ? '#f1c40f' : '#00b894' }">
            {{ permitirMismoJuvenil ? 'Mismo juvenil permitido' : 'Mismo juvenil bloqueado' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Configuracion',
  props: {
    configuracion: {
      type: Object,
      default: () => ({ permitir_mismo_juvenil: false })
    }
  },
  data() {
    return {
      permitirMismoJuvenil: false
    }
  },
  computed: {
    totalEquipos() {
      return this.$parent?.equipos?.length || 0
    },
    totalJuveniles() {
      return this.$parent?.juveniles?.length || 0
    },
    totalGrupos() {
      return this.$parent?.grupos?.length || 0
    }
  },
  watch: {
    configuracion: {
      handler(val) {
        this.permitirMismoJuvenil = val?.permitir_mismo_juvenil || false
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    guardar() {
      this.$emit('guardarConfiguracion', {
        permitir_mismo_juvenil: this.permitirMismoJuvenil
      })
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
  color: #f1c40f;
  font-size: 1.1rem;
  margin-bottom: 20px;
  font-weight: 600;
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
  color: #e0e0e0;
  font-size: 1rem;
  margin-bottom: 5px;
}

.option-desc {
  color: #bdc3c7;
  font-size: 0.85rem;
  line-height: 1.4;
}

.option-toggle {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* Toggle Switch */
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
  background: linear-gradient(135deg, #667eea, #764ba2);
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.toggle-label {
  color: #e0e0e0;
  font-weight: 600;
  font-size: 0.9rem;
  min-width: 100px;
}

.info-box {
  margin-top: 15px;
  padding: 12px 16px;
  background: rgba(241, 196, 15, 0.08);
  border: 1px solid rgba(241, 196, 15, 0.15);
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-icon {
  font-size: 1.2rem;
}

.info-text {
  color: #f1c40f;
  font-size: 0.9rem;
}

/* Status Grid */
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
  color: #bdc3c7;
  font-size: 0.8rem;
  margin-bottom: 5px;
}

.status-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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
  background: linear-gradient(135deg, #667eea, #764ba2);
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
}
</style>
