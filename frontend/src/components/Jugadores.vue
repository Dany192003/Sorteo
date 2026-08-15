<template>
  <div>
    <div class="section-header">
      <h2>👤 Gestión de Jugadores</h2>
      <div v-if="equipoSeleccionado" class="equipo-info">
        <h3>🏆 {{ equipoSeleccionado.nombre }}</h3>
        <p>👤 {{ getJuvenilNombre(equipoSeleccionado.juvenil_id) }}</p>
      </div>
      <button v-if="equipoSeleccionado" @click="cerrarJugadores()" class="btn-secondary">✖ Cerrar</button>
    </div>

    <div v-if="!equipoSeleccionado" class="empty-state">
      <p>📭 Selecciona un equipo para ver sus jugadores</p>
      <button @click="$emit('cambiarVista', 'equipos')" class="btn-primary">Ir a Equipos</button>
    </div>

    <div v-else>
      <div class="form-card">
        <div class="form-row">
          <div class="form-group">
            <label>Nombre del Jugador</label>
            <input v-model="nuevoJugadorNombre" placeholder="Nombre del jugador" class="input" @keyup.enter="agregarJugador()">
          </div>
          <div class="form-group" style="display: flex; align-items: flex-end;">
            <button @click="agregarJugador()" class="btn-success">➕ Agregar</button>
          </div>
        </div>
      </div>

      <div class="jugadores-list">
        <div v-for="jugador in equipoSeleccionado.jugadores" :key="jugador.id" class="jugador-card">
          <span>👤 {{ jugador.nombre }}</span>
          <button @click="eliminarJugador(jugador.id)" class="btn-small-danger">🗑️</button>
        </div>
        <div v-if="equipoSeleccionado.jugadores.length === 0" class="empty-message">
          No hay jugadores en este equipo
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Jugadores',
  props: {
    juveniles: Array,
    equipos: Array,
    equipoSeleccionado: Object
  },
  data() {
    return {
      nuevoJugadorNombre: ''
    }
  },
  emits: ['agregarJugador', 'eliminarJugador', 'cerrarJugadores', 'cambiarVista'],
  methods: {
    getJuvenilNombre(juvenilId) {
      const juvenil = this.juveniles.find(j => j.id === juvenilId)
      return juvenil ? juvenil.nombre : 'Sin asignar'
    },
    agregarJugador() {
      if (!this.nuevoJugadorNombre) {
        alert('Completa el nombre del jugador')
        return
      }
      
      this.$emit('agregarJugador', {
        equipoId: this.equipoSeleccionado.id,
        nombre: this.nuevoJugadorNombre
      })
      this.nuevoJugadorNombre = ''
    },
    eliminarJugador(jugadorId) {
      this.$emit('eliminarJugador', {
        equipoId: this.equipoSeleccionado.id,
        jugadorId: jugadorId
      })
    },
    cerrarJugadores() {
      this.$emit('cerrarJugadores')
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

.equipo-info {
  background: rgba(255, 255, 255, 0.04);
  padding: 15px 20px;
  border-radius: 10px;
  border-left: 4px solid #2193b0;
  flex: 1;
}

.equipo-info h3 {
  color: #48cae4;
  margin-bottom: 5px;
}

.equipo-info p {
  color: #8ecae6;
  font-size: 0.9rem;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  color: #e8f0fe;
  padding: 10px 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.btn-primary {
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
  color: #fff;
  padding: 10px 24px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(33, 147, 176, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, #00b4d8, #0077b6);
  color: #fff;
  padding: 10px 24px;
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

.jugadores-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.jugador-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

.jugador-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(33, 147, 176, 0.2);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-state p {
  font-size: 1.2rem;
  color: #8ecae6;
  margin-bottom: 20px;
}

.empty-message {
  text-align: center;
  color: #7f8c8d;
  padding: 30px;
  font-style: italic;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-group {
    min-width: 100%;
  }
}
</style>
