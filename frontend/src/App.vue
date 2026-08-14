<template>
  <div id="app">
    <header>
      <div class="header-content">
        <div>
          <h1>⚽ TORNEO DE FÚTBOL JUVENIL</h1>
          <p class="subtitle">Parroquia Juvenil 2026</p>
        </div>
        <div v-if="backendStatus" class="status success">✅ Conectado</div>
        <div v-else class="status error">❌ Desconectado</div>
      </div>
      <div class="nav-buttons">
        <button @click="vista = 'dashboard'" :class="{ active: vista === 'dashboard' }">📊 Dashboard</button>
        <button @click="vista = 'juveniles'" :class="{ active: vista === 'juveniles' }">👥 Juveniles</button>
        <button @click="vista = 'equipos'" :class="{ active: vista === 'equipos' }">📋 Equipos</button>
        <button @click="vista = 'jugadores'" :class="{ active: vista === 'jugadores' }">👤 Jugadores</button>
        <button @click="vista = 'torneo'" :class="{ active: vista === 'torneo' }">🏆 Torneo</button>
        <button @click="vista = 'configuracion'" :class="{ active: vista === 'configuracion' }">⚙️ Configuración</button>
      </div>
    </header>

    <main>
      <Dashboard
        v-if="vista === 'dashboard'"
        :juveniles="juveniles"
        :equipos="equipos"
        :grupos="grupos"
        :totalJugadores="totalJugadores"
        :partidos="partidos"
        @cambiarVista="vista = $event"
        @generarTorneo="mostrarDialogoGrupos"
        @vaciarDatos="vaciarDatos"
        @reiniciarTorneo="reiniciarTorneo"
      />

      <Juveniles
        v-if="vista === 'juveniles'"
        :juveniles="juveniles"
        @agregarJuvenil="agregarJuvenil"
        @eliminarJuvenil="eliminarJuvenil"
      />

      <Equipos
        v-if="vista === 'equipos'"
        :juveniles="juveniles"
        :equipos="equipos"
        @agregarEquipo="guardarEquipo"
        @eliminarEquipo="eliminarEquipo"
        @verJugadores="verJugadores"
      />

      <Jugadores
        v-if="vista === 'jugadores'"
        :juveniles="juveniles"
        :equipos="equipos"
        :equipoSeleccionado="equipoSeleccionado"
        @agregarJugador="agregarJugador"
        @eliminarJugador="eliminarJugador"
        @cerrarJugadores="cerrarJugadores"
        @cambiarVista="vista = $event"
      />

      <Torneo
        v-if="vista === 'torneo'"
        :grupos="grupos"
        :llaves="llaves"
        :partidos="partidos"
        :configuracion="configuracion"
        @generarTorneo="mostrarDialogoGrupos"
        @registrarResultado="registrarResultado"
      />

      <Configuracion
        v-if="vista === 'configuracion'"
        :configuracion="configuracion"
        @guardarConfiguracion="guardarConfiguracion"
      />
    </main>
  </div>
</template>

<script>
import axios from 'axios'
import Dashboard from './components/Dashboard.vue'
import Juveniles from './components/Juveniles.vue'
import Equipos from './components/Equipos.vue'
import Jugadores from './components/Jugadores.vue'
import Torneo from './components/Torneo.vue'
import Configuracion from './components/Configuracion.vue'

const API_BASE_URL = 'http://localhost:5000/api'
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

export default {
  name: 'App',
  components: {
    Dashboard,
    Juveniles,
    Equipos,
    Jugadores,
    Torneo,
    Configuracion
  },
  data() {
    return {
      backendStatus: null,
      vista: 'dashboard',
      juveniles: [],
      equipos: [],
      grupos: [],
      llaves: {},
      partidos: [],
      equipoSeleccionado: null,
      configuracion: {
        permitir_mismo_juvenil: false,
        puntos_ganado: 3,
        puntos_empate: 1,
        puntos_perdido: 0
      }
    }
  },
  computed: {
    totalJugadores() {
      let total = 0
      this.equipos.forEach(e => {
        total += e.jugadores.length
      })
      return total
    }
  },
  mounted() {
    this.checkBackend()
    this.cargarDatos()
    this.cargarConfiguracion()
  },
  methods: {
    async checkBackend() {
      try {
        const response = await api.get('/health')
        this.backendStatus = response.data
      } catch (error) {
        console.error('Error conectando al backend:', error)
        this.backendStatus = null
        this.mostrarError('Error de conexión con el servidor')
      }
    },
    async cargarDatos() {
      try {
        const [juvenilesRes, equiposRes, gruposRes, partidosRes] = await Promise.all([
          api.get('/juveniles'),
          api.get('/equipos'),
          api.get('/grupos'),
          api.get('/partidos')
        ])
        this.juveniles = juvenilesRes.data
        this.equipos = equiposRes.data
        this.grupos = gruposRes.data.grupos || []
        this.llaves = gruposRes.data.llaves || {}
        this.partidos = partidosRes.data
        
        if (gruposRes.data.configuracion) {
          this.configuracion = {
            ...this.configuracion,
            ...gruposRes.data.configuracion
          }
        }
        
        if (this.equipoSeleccionado) {
          const equipoActualizado = this.equipos.find(e => e.id === this.equipoSeleccionado.id)
          if (equipoActualizado) {
            this.equipoSeleccionado = equipoActualizado
          }
        }
      } catch (error) {
        console.error('Error cargando datos:', error)
        this.mostrarError('Error al cargar los datos')
      }
    },
    async cargarConfiguracion() {
      try {
        const response = await api.get('/configuracion')
        this.configuracion = {
          ...this.configuracion,
          ...response.data
        }
      } catch (error) {
        console.error('Error cargando configuración:', error)
      }
    },
    async guardarConfiguracion(config) {
      try {
        await api.post('/configuracion', config)
        this.configuracion = { ...this.configuracion, ...config }
        this.mostrarExito('Configuración guardada correctamente')
        await this.cargarDatos()
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al guardar configuración')
      }
    },
    mostrarError(mensaje) {
      alert(`❌ ${mensaje}`)
    },
    mostrarExito(mensaje) {
      alert(`✅ ${mensaje}`)
    },
    async agregarJuvenil(nombre) {
      try {
        await api.post('/juveniles', { nombre })
        await this.cargarDatos()
        this.mostrarExito('Juvenil agregado correctamente')
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al agregar juvenil')
      }
    },
    async eliminarJuvenil(id) {
      try {
        await api.delete(`/juveniles/${id}`)
        await this.cargarDatos()
        this.mostrarExito('Juvenil eliminado correctamente')
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al eliminar juvenil')
      }
    },
    async guardarEquipo(equipo) {
      try {
        await api.post('/equipos', equipo)
        await this.cargarDatos()
        this.mostrarExito('Equipo agregado correctamente')
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError(`Error al agregar equipo: ${error.response?.data?.error || error.message}`)
      }
    },
    async eliminarEquipo(id) {
      try {
        await api.delete(`/equipos/${id}`)
        await this.cargarDatos()
        this.mostrarExito('Equipo eliminado correctamente')
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al eliminar equipo')
      }
    },
    verJugadores(equipo) {
      this.equipoSeleccionado = equipo
      this.vista = 'jugadores'
    },
    cerrarJugadores() {
      this.equipoSeleccionado = null
      this.vista = 'equipos'
    },
    async agregarJugador({ equipoId, nombre, edad }) {
      try {
        await api.post(`/equipos/${equipoId}/jugadores`, { nombre, edad })
        await this.cargarDatos()
        this.mostrarExito('Jugador agregado correctamente')
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al agregar jugador')
      }
    },
    async eliminarJugador({ equipoId, jugadorId }) {
      try {
        await api.delete(`/equipos/${equipoId}/jugadores/${jugadorId}`)
        await this.cargarDatos()
        this.mostrarExito('Jugador eliminado correctamente')
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al eliminar jugador')
      }
    },
    async mostrarDialogoGrupos() {
      const totalEquipos = this.equipos.length
      
      if (totalEquipos < 2) {
        this.mostrarError('Se necesitan al menos 2 equipos para crear grupos')
        return
      }
      
      let opciones = []
      let opcionesDetalle = []
      for (let grupos of [2, 4, 8]) {
        const equiposPorGrupo = Math.floor(totalEquipos / grupos)
        if (equiposPorGrupo >= 3 && grupos * 2 <= totalEquipos) {
          opciones.push(grupos)
          opcionesDetalle.push(`${grupos} grupos (${equiposPorGrupo} equipos por grupo)`)
        }
      }
      
      if (opciones.length === 0) {
        this.mostrarError(`⚠️ Con ${totalEquipos} equipos no hay combinación válida.\n\nNecesitas al menos ${Math.ceil(totalEquipos/3)} grupos con 3 equipos cada uno.\nOpciones: 2, 4 u 8 grupos`)
        return
      }
      
      const mensaje = `📊 Total de equipos: ${totalEquipos}\n\nOpciones válidas:\n${opcionesDetalle.join('\n')}\n\n¿Cuántos grupos quieres? (2, 4 u 8)`
      const cantidadGrupos = prompt(mensaje, opciones[0].toString())
      
      if (!cantidadGrupos) return
      
      const num = parseInt(cantidadGrupos)
      
      if (![2, 4, 8].includes(num)) {
        this.mostrarError('❌ La cantidad de grupos debe ser 2, 4 u 8')
        return
      }
      
      const equiposPorGrupo = Math.floor(totalEquipos / num)
      if (equiposPorGrupo < 3) {
        this.mostrarError(`❌ Con ${totalEquipos} equipos y ${num} grupos, algunos grupos tendrían menos de 3 equipos`)
        return
      }
      
      try {
        const response = await api.post('/grupos', {
          equipos_por_grupo: equiposPorGrupo
        })
        this.grupos = response.data.grupos
        this.llaves = response.data.llaves || {}
        this.vista = 'torneo'
        await this.cargarDatos()
        
        let mensajeExito = `✅ Torneo generado correctamente\n`
        mensajeExito += `📋 ${response.data.total_grupos} grupos creados\n`
        mensajeExito += `⚽ ${equiposPorGrupo} equipos por grupo\n`
        mensajeExito += `🏆 ${response.data.clasificados} clasificados a eliminación`
        
        if (response.data.configuracion?.permitir_mismo_juvenil) {
          mensajeExito += '\n⚠️ Se permiten enfrentamientos del mismo juvenil'
        } else {
          mensajeExito += '\n🚫 No se permiten enfrentamientos del mismo juvenil'
        }
        
        this.mostrarExito(mensajeExito)
      } catch (error) {
        console.error('Error:', error)
        const msg = error.response?.data?.error || error.message
        this.mostrarError(`Error al generar torneo: ${msg}`)
      }
    },
    async registrarResultado({ partidoId, goles1, goles2 }) {
      try {
        await api.post(`/partidos/${partidoId}/resultado`, {
          goles1,
          goles2
        })
        await this.cargarDatos()
        this.mostrarExito('✅ Resultado registrado correctamente')
        if (this.vista === 'dashboard') {
          this.$forceUpdate()
        }
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al registrar resultado')
      }
    },
    async vaciarDatos() {
      try {
        await api.post('/vaciar')
        await this.cargarDatos()
        this.mostrarExito('Datos eliminados correctamente')
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al vaciar datos')
      }
    },
    async reiniciarTorneo() {
      try {
        await api.post('/reiniciar')
        await this.cargarDatos()
        this.vista = 'dashboard'
        this.mostrarExito('Torneo reiniciado correctamente')
      } catch (error) {
        console.error('Error:', error)
        this.mostrarError('Error al reiniciar torneo')
      }
    }
  }
}
</script>

<style>
@import './style.css';
</style>
