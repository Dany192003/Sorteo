<template>
  <div>
    <div class="section-header">
      <h2>📋 Gestión de Equipos</h2>
      <button @click="mostrarFormEquipo = !mostrarFormEquipo" class="btn-primary">
        {{ mostrarFormEquipo ? '✖ Cerrar' : '➕ Agregar Equipo' }}
      </button>
    </div>

    <div v-if="mostrarFormEquipo" class="form-card">
      <div class="form-row">
        <div class="form-group">
          <label>Nombre del Equipo (opcional)</label>
          <input v-model="nuevoEquipo.nombre" placeholder="Dejar vacío para auto-generar" class="input">
        </div>
        <div class="form-group">
          <label>Juvenil Responsable</label>
          <select v-model="nuevoEquipo.juvenil_id" class="input">
            <option value="">Seleccionar...</option>
            <option v-for="j in juveniles" :key="j.id" :value="j.id">
              {{ j.nombre }} ({{ j.equipos.length }} equipos)
            </option>
          </select>
        </div>
        <div class="form-group" style="display: flex; align-items: flex-end;">
          <button @click="guardarEquipo()" class="btn-success">💾 Guardar</button>
        </div>
      </div>
      <div v-if="nuevoEquipo.juvenil_id" class="info-message">
        ℹ️ Este juvenil tiene {{ equiposPorJuvenil(nuevoEquipo.juvenil_id) }} de 3 equipos permitidos
      </div>
    </div>

    <div class="equipos-grid">
      <div v-for="equipo in equipos" :key="equipo.id" class="equipo-card">
        <div class="equipo-header">
          <h3>🏆 {{ equipo.nombre }}</h3>
          <div class="equipo-actions">
            <button @click="$emit('verJugadores', equipo)" class="btn-small-success">👤 Jugadores</button>
            <button @click="eliminarEquipo(equipo.id)" class="btn-small-danger">🗑️</button>
          </div>
        </div>
        <p class="equipo-juvenil">👤 {{ getJuvenilNombre(equipo.juvenil_id) }}</p>
        <p class="equipo-jugadores">👥 {{ equipo.jugadores.length }} jugadores</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Equipos',
  props: {
    juveniles: Array,
    equipos: Array
  },
  data() {
    return {
      mostrarFormEquipo: false,
      nuevoEquipo: {
        nombre: '',
        juvenil_id: null
      }
    }
  },
  emits: ['agregarEquipo', 'eliminarEquipo', 'verJugadores'],
  methods: {
    equiposPorJuvenil(juvenilId) {
      return this.equipos.filter(e => e.juvenil_id === juvenilId).length
    },
    getJuvenilNombre(juvenilId) {
      const juvenil = this.juveniles.find(j => j.id === juvenilId)
      return juvenil ? juvenil.nombre : 'Sin asignar'
    },
    guardarEquipo() {
      if (!this.nuevoEquipo.juvenil_id) {
        alert('Selecciona un juvenil responsable')
        return
      }
      
      const count = this.equiposPorJuvenil(this.nuevoEquipo.juvenil_id)
      if (count >= 3) {
        alert('❌ Este juvenil ya tiene 3 equipos (máximo permitido)')
        return
      }
      
      this.$emit('agregarEquipo', this.nuevoEquipo)
      this.nuevoEquipo = { nombre: '', juvenil_id: null }
      this.mostrarFormEquipo = false
    },
    eliminarEquipo(id) {
      this.$emit('eliminarEquipo', id)
    }
  }
}
</script>
