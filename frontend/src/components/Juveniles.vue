<template>
  <div>
    <div class="section-header">
      <h2>👥 Gestión de Juveniles</h2>
      <div class="form-row">
        <input v-model="nuevoJuvenilNombre" placeholder="Nombre del juvenil" class="input" @keyup.enter="agregarJuvenil()">
        <button @click="agregarJuvenil()" class="btn-primary">➕ Agregar</button>
      </div>
    </div>

    <div class="juveniles-grid">
      <div v-for="juvenil in juveniles" :key="juvenil.id" class="juvenil-card">
        <span>👤 {{ juvenil.nombre }}</span>
        <span class="juvenil-equipos-badge">{{ juvenil.equipos.length }}</span>
        <button @click="eliminarJuvenil(juvenil.id)" class="btn-small-danger">🗑️</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Juveniles',
  props: {
    juveniles: Array
  },
  data() {
    return {
      nuevoJuvenilNombre: ''
    }
  },
  emits: ['agregarJuvenil', 'eliminarJuvenil'],
  methods: {
    agregarJuvenil() {
      if (!this.nuevoJuvenilNombre) return
      this.$emit('agregarJuvenil', this.nuevoJuvenilNombre)
      this.nuevoJuvenilNombre = ''
    },
    eliminarJuvenil(id) {
      this.$emit('eliminarJuvenil', id)
    }
  }
}
</script>
