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
            <input v-model="nuevoJugadorNombre" placeholder="Nombre del jugador" class="input">
          </div>
          <div class="form-group">
            <label>Edad</label>
            <input v-model="nuevaJugadorEdad" placeholder="Edad" class="input" type="number" style="width: 100px;">
          </div>
          <div class="form-group" style="display: flex; align-items: flex-end;">
            <button @click="agregarJugador()" class="btn-success">➕ Agregar</button>
          </div>
        </div>
      </div>

      <div class="jugadores-list">
        <div v-for="jugador in equipoSeleccionado.jugadores" :key="jugador.id" class="jugador-card">
          <span>👤 {{ jugador.nombre }}</span>
          <span class="edad-badge">{{ jugador.edad }} años</span>
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
      nuevoJugadorNombre: '',
      nuevaJugadorEdad: ''
    }
  },
  emits: ['agregarJugador', 'eliminarJugador', 'cerrarJugadores', 'cambiarVista'],
  methods: {
    getJuvenilNombre(juvenilId) {
      const juvenil = this.juveniles.find(j => j.id === juvenilId)
      return juvenil ? juvenil.nombre : 'Sin asignar'
    },
    agregarJugador() {
      if (!this.nuevoJugadorNombre || !this.nuevaJugadorEdad) {
        alert('Completa nombre y edad del jugador')
        return
      }
      
      this.$emit('agregarJugador', {
        equipoId: this.equipoSeleccionado.id,
        nombre: this.nuevoJugadorNombre,
        edad: parseInt(this.nuevaJugadorEdad)
      })
      this.nuevoJugadorNombre = ''
      this.nuevaJugadorEdad = ''
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
