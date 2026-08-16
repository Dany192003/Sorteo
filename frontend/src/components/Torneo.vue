<template>
  <div>
    <div class="section-header">
      <h2>🏆 Torneo Generado</h2>
      <div class="header-actions">
        <button @click="confirmarRegenerar" class="btn-success">🔄 Regenerar</button>
        <button @click="exportarPDF" class="btn-pdf">📄 Exportar PDF</button>
        <button @click="resetZoom" class="btn-secondary">🔍 Resetear Zoom</button>
      </div>
    </div>

    <div v-if="grupos.length === 0" class="empty-state">
      <p>📭 Aún no se ha generado el torneo</p>
      <button @click="$emit('generarTorneo')" class="btn-primary">Generar Torneo</button>
    </div>

    <div v-else>
      <!-- FASE DE GRUPOS -->
      <h3>📋 FASE DE GRUPOS</h3>
      <p style="color: #8ecae6; margin-bottom: 15px; font-size: 0.9rem;">
        🏅 Los 2 primeros de cada grupo pasan a la siguiente fase
      </p>
      <div class="grupos-container">
        <div v-for="(grupo, idx) in grupos" :key="idx" class="grupo-card">
          <h3>{{ grupo.nombre }}</h3>
          <div v-for="(equipo, eIdx) in grupo.equipos" :key="equipo.id" class="equipo-item" :class="{ 'clasificado': eIdx < 2 }">
            ⚽ {{ equipo.nombre }}
            <span v-if="eIdx < 2" class="clasificado-badge">✅ Clasificado</span>
          </div>
        </div>
      </div>

      <!-- PARTIDOS Y RESULTADOS AGRUPADOS POR GRUPO -->
      <h3 style="margin-top: 30px;">📝 Partidos y Resultados</h3>
      
      <div v-if="partidos.length === 0" class="empty-message">
        No hay partidos para mostrar
      </div>
      
      <div v-else class="partidos-por-grupo">
        <div v-for="grupo in grupos" :key="grupo.nombre" class="grupo-partidos">
          <h4 class="grupo-partidos-titulo">{{ grupo.nombre }}</h4>
          <div class="partidos-grid">
            <div v-for="partido in getPartidosDelGrupo(grupo.nombre)" :key="partido.id" class="partido-card">
              <div class="partido-header">
                <span class="partido-etapa">{{ getNombreEtapa(partido.etapa) }}</span>
                <span v-if="partido.en_vivo" class="en-vivo-tag">🔴 EN VIVO</span>
                <span v-if="partido.jugado" class="finalizado-tag">✅ Finalizado</span>
              </div>
              <div class="partido-equipos">
                <span class="equipo1-nombre">{{ partido.equipo1 }}</span>
                <span class="vs-text">vs</span>
                <span class="equipo2-nombre">{{ partido.equipo2 }}</span>
              </div>
              <div class="partido-detalle">
                <span v-if="partido.jugado" class="resultado-text">
                  🏆 {{ partido.goles1 }} - {{ partido.goles2 }}
                  <span v-if="partido.ganador && partido.ganador !== 'Empate'" class="ganador-tag">
                    {{ partido.ganador }}
                  </span>
                  <span v-else-if="partido.ganador === 'Empate'" class="empate-tag">🤝 Empate</span>
                </span>
                <span v-else class="pendiente-tag">⏳ Pendiente</span>
              </div>
              <div class="partido-actions">
                <button v-if="!partido.jugado && !partido.en_vivo" @click="iniciarPartido(partido.id)" class="btn-small-live">▶️ Iniciar</button>
                <button v-if="partido.en_vivo" class="btn-small-live" style="background: #e63946; animation: pulse 1s infinite;">🔴 EN VIVO</button>
                <button v-if="!partido.jugado && partido.en_vivo" @click="mostrarFormResultado(partido)" class="btn-small-success">📝 Finalizar</button>
                <button v-if="partido.jugado" @click="mostrarFormResultado(partido)" class="btn-small-edit">✏️ Editar</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- LLAVES DE ELIMINACIÓN CON D3 -->
      <h3 style="margin-top: 30px;">🏆 LLAVES DE ELIMINACIÓN</h3>

      <div v-if="llaves && (llaves.equipo1 || llaves.equipo2)" class="llaves-wrapper">
        <div class="zoom-controls">
          <button @click="zoomIn" class="zoom-btn" title="Acercar">🔍+</button>
          <button @click="zoomOut" class="zoom-btn" title="Alejar">🔍−</button>
          <button @click="resetZoom" class="zoom-btn" title="Resetear">⟲</button>
          <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
        </div>
        
        <div ref="llavesContainer" class="llaves-container">
          <div ref="llavesChart" class="llaves-chart"></div>
        </div>
        
        <div class="campeon-box">
          <div class="trofeo">🏆</div>
          <div class="campeon">CAMPEÓN</div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>📭 Las llaves de eliminación aún no están disponibles</p>
      </div>
    </div>

    <!-- MODAL PARA REGISTRAR RESULTADO -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">
        <h3>📝 Registrar Resultado</h3>
        <div class="modal-body">
          <div class="modal-partido">
            <span class="modal-equipo1">{{ partidoSeleccionado?.equipo1 }}</span>
            <span class="modal-vs">vs</span>
            <span class="modal-equipo2">{{ partidoSeleccionado?.equipo2 }}</span>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>{{ partidoSeleccionado?.equipo1 }}</label>
              <input v-model.number="goles1" type="number" min="0" class="input" placeholder="Goles">
            </div>
            <div class="form-group">
              <label>{{ partidoSeleccionado?.equipo2 }}</label>
              <input v-model.number="goles2" type="number" min="0" class="input" placeholder="Goles">
            </div>
          </div>
          <div class="info-puntos">
            <span>🏆 Sistema de puntos: Ganar = {{ configPuntos?.puntos_ganado || 3 }} | Empate = {{ configPuntos?.puntos_empate || 1 }} | Perder = {{ configPuntos?.puntos_perdido || 0 }}</span>
          </div>
          <div class="modal-actions">
            <button @click="guardarResultado" class="btn-success">💾 Guardar</button>
            <button @click="cerrarModal" class="btn-secondary">Cancelar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

const NODE_WIDTH = 180
const NODE_HEIGHT = 52
const ROW_HEIGHT = NODE_HEIGHT / 2
const LEVEL_GAP = 70
const NODE_V_GAP = 20
const MAX_CHARS = 18
const MARGIN = 50

function truncar(nombre) {
  if (!nombre) return 'Por definir'
  return nombre.length > MAX_CHARS ? nombre.slice(0, MAX_CHARS - 1) + '…' : nombre
}

export default {
  name: 'Torneo',
  props: {
    grupos: Array,
    llaves: Object,
    partidos: Array,
    configuracion: Object
  },
  emits: ['generarTorneo', 'registrarResultado', 'recargarDatos'],
  data() {
    return {
      mostrarModal: false,
      partidoSeleccionado: null,
      goles1: 0,
      goles2: 0,
      zoomLevel: 1,
      zoomTransform: null,
      svgWidth: 0,
      svgHeight: 0
    }
  },
  computed: {
    configPuntos() {
      return this.configuracion || { puntos_ganado: 3, puntos_empate: 1, puntos_perdido: 0 }
    }
  },
  watch: {
    llaves: {
      handler() {
        this.$nextTick(() => {
          setTimeout(() => this.renderTree(), 100)
        })
      },
      deep: true
    }
  },
  mounted() {
    this.renderTree()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    if (this._resizeTimeout) {
      clearTimeout(this._resizeTimeout)
    }
    if (this._wheelListener) {
      const container = this.$refs.llavesContainer
      if (container) {
        container.removeEventListener('wheel', this._wheelListener)
      }
    }
  },
  methods: {
    getPartidosDelGrupo(nombreGrupo) {
      return this.partidos.filter(p => p.grupo === nombreGrupo)
    },
    confirmarRegenerar() {
      if (this.partidos.some(p => p.jugado)) {
        if (!confirm('⚠️ Hay partidos ya jugados. ¿Estás seguro de que quieres regenerar el torneo? Se perderán todos los resultados.')) {
          return
        }
      }
      this.$emit('generarTorneo')
    },
    getNombreEtapa(etapa) {
      const nombres = {
        'grupos': '📋 Grupos',
        'cuartos': '🎯 Cuartos',
        'semifinal': '🏅 Semis',
        'final': '🏆 Final'
      }
      return nombres[etapa] || etapa
    },
    async iniciarPartido(partidoId) {
      try {
        await api.post(`/partidos/${partidoId}/en_vivo`, { en_vivo: true })
        // Recargar datos después de iniciar el partido
        this.$emit('recargarDatos')
      } catch (error) {
        console.error('Error:', error)
        alert('❌ Error al iniciar partido')
      }
    },
    mostrarFormResultado(partido) {
      this.partidoSeleccionado = partido
      this.goles1 = partido.goles1 || 0
      this.goles2 = partido.goles2 || 0
      this.mostrarModal = true
    },
    cerrarModal() {
      this.mostrarModal = false
      this.partidoSeleccionado = null
    },
    guardarResultado() {
      if (this.goles1 === undefined || this.goles2 === undefined || this.goles1 < 0 || this.goles2 < 0) {
        alert('Completa los goles correctamente')
        return
      }
      this.$emit('registrarResultado', {
        partidoId: this.partidoSeleccionado.id,
        goles1: this.goles1,
        goles2: this.goles2
      })
      this.cerrarModal()
    },
    handleResize() {
      clearTimeout(this._resizeTimeout)
      this._resizeTimeout = setTimeout(() => {
        this.renderTree()
      }, 300)
    },
    zoomIn() {
      this.zoomLevel = Math.min(this.zoomLevel + 0.15, 2.5)
      this.applyZoom()
    },
    zoomOut() {
      this.zoomLevel = Math.max(this.zoomLevel - 0.15, 0.4)
      this.applyZoom()
    },
    resetZoom() {
      this.zoomLevel = 1
      this.applyZoom()
      const container = this.$refs.llavesContainer
      if (container) {
        container.scrollLeft = 0
        container.scrollTop = 0
      }
    },
    applyZoom() {
      const chart = this.$refs.llavesChart
      if (chart) {
        const container = this.$refs.llavesContainer
        const containerWidth = container ? container.clientWidth - 40 : 800
        const containerHeight = container ? container.clientHeight - 40 : 500
        
        const scaleX = containerWidth / (this.svgWidth || 1)
        const scaleY = containerHeight / (this.svgHeight || 1)
        const baseScale = Math.min(scaleX, scaleY, 1) * 0.92
        
        const finalScale = baseScale * this.zoomLevel
        
        chart.style.transform = `scale(${finalScale})`
        chart.style.transformOrigin = 'top left'
        chart.style.width = `${100 / finalScale}%`
        chart.style.height = `${100 / finalScale}%`
      }
    },
    async exportarPDF() {
      const container = this.$refs.llavesContainer
      if (!container) return

      try {
        const loadingMsg = document.createElement('div')
        loadingMsg.style.cssText = `
          position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
          background: rgba(0,0,0,0.8); color: #fff; padding: 20px 40px;
          border-radius: 12px; font-size: 18px; z-index: 9999;
        `
        loadingMsg.textContent = '⏳ Generando PDF...'
        document.body.appendChild(loadingMsg)

        const canvas = await html2canvas(container, {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#0a1628',
          logging: false,
          width: container.scrollWidth,
          height: container.scrollHeight
        })

        const imgData = canvas.toDataURL('image/png')
        const pdf = new jsPDF({
          orientation: 'landscape',
          unit: 'px',
          format: [canvas.width, canvas.height]
        })

        const pdfWidth = pdf.internal.pageSize.getWidth()
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width

        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)
        pdf.save('torneo_llaves.pdf')

        document.body.removeChild(loadingMsg)
      } catch (error) {
        console.error('Error exportando PDF:', error)
        alert('❌ Error al exportar PDF: ' + error.message)
      }
    },
    renderTree() {
      const container = this.$refs.llavesChart
      if (!container) return
      if (!this.llaves || (!this.llaves.equipo1 && !this.llaves.equipo2)) return

      container.innerHTML = ''

      const parentRect = this.$refs.llavesContainer
      const containerWidth = parentRect ? parentRect.clientWidth - 40 : 900
      const containerHeight = parentRect ? parentRect.clientHeight - 40 : 600

      const root = d3.hierarchy(this.llaves)
      const treeLayout = d3
        .tree()
        .nodeSize([NODE_HEIGHT + NODE_V_GAP, NODE_WIDTH + LEVEL_GAP])

      const treeData = treeLayout(root)

      const nodos = treeData.descendants()
      const xs = nodos.map(d => d.x)
      const ys = nodos.map(d => d.y)
      const minX = Math.min(...xs)
      const maxX = Math.max(...xs)
      const minY = Math.min(...ys)
      const maxY = Math.max(...ys)

      const treeWidth = maxY - minY + NODE_WIDTH + MARGIN * 2
      const treeHeight = maxX - minX + NODE_HEIGHT + MARGIN * 2

      const scaleX = (containerWidth - 20) / treeWidth
      const scaleY = (containerHeight - 20) / treeHeight
      const scale = Math.min(scaleX, scaleY, 1) * 0.95

      const svgWidth = Math.max(treeWidth * scale, containerWidth)
      const svgHeight = Math.max(treeHeight * scale, containerHeight)

      this.svgWidth = svgWidth
      this.svgHeight = svgHeight

      const svg = d3
        .select(container)
        .append('svg')
        .attr('viewBox', `0 0 ${svgWidth} ${svgHeight}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .style('width', '100%')
        .style('height', '100%')
        .style('min-width', `${Math.max(500, svgWidth)}px`)
        .style('min-height', `${Math.max(400, svgHeight)}px`)

      const offsetX = (svgWidth - treeWidth * scale) / 2 + MARGIN
      const offsetY = (svgHeight - treeHeight * scale) / 2 + MARGIN

      const g = svg
        .append('g')
        .attr('transform', `translate(${offsetX - minY * scale},${offsetY - minX * scale})`)
        .style('transform-origin', 'top left')

      const scalePos = (d) => ({
        x: d.x * scale,
        y: d.y * scale
      })

      g.selectAll('.link')
        .data(treeData.links())
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', d => {
          const source = scalePos(d.source)
          const target = scalePos(d.target)
          const sx = source.y + NODE_WIDTH * scale / 2
          const sy = source.x
          const tx = target.y - NODE_WIDTH * scale / 2
          const ty = target.x
          const midX = sx + (tx - sx) / 2
          return `M${sx},${sy} H${midX} V${ty} H${tx}`
        })
        .style('fill', 'none')
        .style('stroke', 'rgba(33, 147, 176, 0.35)')
        .style('stroke-width', `${1.2 * scale}px`)

      const nodeGroups = g
        .selectAll('.node')
        .data(nodos)
        .enter()
        .append('g')
        .attr('class', 'node')
        .attr('transform', d => {
          const pos = scalePos(d)
          return `translate(${pos.y - NODE_WIDTH * scale / 2},${pos.x - NODE_HEIGHT * scale / 2})`
        })

      const esFinal = d => d.depth === 0
      const nodeW = NODE_WIDTH * scale
      const nodeH = NODE_HEIGHT * scale
      const rowH = nodeH / 2
      const fontSize = Math.max(8, Math.min(11, 11 * scale))

      nodeGroups
        .append('rect')
        .attr('width', nodeW)
        .attr('height', nodeH)
        .attr('rx', 6 * scale)
        .attr('ry', 6 * scale)
        .style('fill', d => (esFinal(d) ? 'rgba(72, 202, 228, 0.12)' : 'rgba(33, 147, 176, 0.12)'))
        .style('stroke', d => (esFinal(d) ? 'rgba(72, 202, 228, 0.4)' : 'rgba(33, 147, 176, 0.3)'))
        .style('stroke-width', `${1.2 * scale}px`)

      nodeGroups
        .append('line')
        .attr('x1', 4 * scale)
        .attr('x2', nodeW - 4 * scale)
        .attr('y1', rowH)
        .attr('y2', rowH)
        .style('stroke', 'rgba(255, 255, 255, 0.06)')
        .style('stroke-width', `${0.5 * scale}px`)
        .style('stroke-dasharray', `${4 * scale},${4 * scale}`)

      nodeGroups
        .append('text')
        .attr('x', 10 * scale)
        .attr('y', rowH / 2 + 1)
        .attr('dominant-baseline', 'central')
        .style('fill', '#6dd5ed')
        .style('font-size', `${fontSize}px`)
        .style('font-weight', '500')
        .style('font-family', 'Segoe UI, sans-serif')
        .style('pointer-events', 'none')
        .text(d => truncar(d.data.equipo1))
        .append('title')
        .text(d => d.data.equipo1 || 'Por definir')

      nodeGroups
        .append('text')
        .attr('x', 10 * scale)
        .attr('y', rowH + rowH / 2 + 1)
        .attr('dominant-baseline', 'central')
        .style('fill', '#2193b0')
        .style('font-size', `${fontSize}px`)
        .style('font-weight', '500')
        .style('font-family', 'Segoe UI, sans-serif')
        .style('pointer-events', 'none')
        .text(d => truncar(d.data.equipo2))
        .append('title')
        .text(d => d.data.equipo2 || 'Por definir')

      nodeGroups
        .filter(d => d.depth > 0 && d.data.equipo1 && d.data.equipo2)
        .append('text')
        .attr('x', nodeW - 14 * scale)
        .attr('y', rowH / 2 + 1)
        .attr('dominant-baseline', 'central')
        .style('fill', '#48cae4')
        .style('font-size', `${fontSize + 1}px`)
        .style('pointer-events', 'none')
        .text('⚡')
        .append('title')
        .text('Partido de eliminación')

      nodeGroups
        .filter(d => !!d.data.id)
        .append('text')
        .attr('x', nodeW - 6 * scale)
        .attr('y', -6 * scale)
        .attr('text-anchor', 'end')
        .style('fill', '#8ecae6')
        .style('font-size', `${Math.max(7, fontSize - 2)}px`)
        .style('font-weight', '600')
        .style('font-family', 'monospace')
        .style('pointer-events', 'none')
        .text(d => d.data.id)

      nodeGroups
        .on('mouseenter', function () {
          d3.select(this).select('rect')
            .transition()
            .duration(150)
            .style('stroke-width', `${2 * scale}px`)
            .style('stroke', 'rgba(33, 147, 176, 0.6)')
        })
        .on('mouseleave', function (event, d) {
          d3.select(this)
            .select('rect')
            .transition()
            .duration(150)
            .style('stroke-width', `${1.2 * scale}px`)
            .style('stroke', esFinal(d) ? 'rgba(72, 202, 228, 0.4)' : 'rgba(33, 147, 176, 0.3)')
        })

      this.$nextTick(() => {
        this.applyZoom()
      })
    }
  }
}
</script>

<style scoped>
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.section-header h2 {
  font-size: 1.4rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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

.btn-pdf {
  background: linear-gradient(135deg, #e63946, #c1121f);
  color: #fff;
  padding: 10px 24px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.btn-pdf:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(230, 57, 70, 0.4);
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

.btn-small-live {
  padding: 5px 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.3s ease;
  background: #00b4d8;
  color: #fff;
}

.btn-small-live:hover {
  background: #0077b6;
  transform: scale(1.05);
}

.btn-small-success {
  padding: 5px 16px;
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

.btn-small-edit {
  padding: 5px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  background: rgba(72, 202, 228, 0.15);
  color: #48cae4;
  border: 1px solid rgba(72, 202, 228, 0.15);
}

.btn-small-edit:hover {
  background: rgba(72, 202, 228, 0.25);
  transform: scale(1.05);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.en-vivo-tag {
  font-size: 0.6rem;
  background: #e63946;
  padding: 2px 10px;
  border-radius: 10px;
  color: #fff;
  font-weight: 700;
  animation: pulse 1s infinite;
}

.finalizado-tag {
  font-size: 0.6rem;
  background: #00b4d8;
  padding: 2px 10px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
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

.equipo-item.clasificado {
  border-left-color: #00b4d8;
  background: rgba(0, 180, 216, 0.08);
}

.clasificado-badge {
  font-size: 0.6rem;
  background: #00b4d8;
  padding: 2px 8px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
}

.partidos-por-grupo {
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-top: 15px;
}

.grupo-partidos {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.grupo-partidos-titulo {
  color: #48cae4;
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.partidos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 15px;
}

.partido-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

.partido-card:hover {
  border-color: rgba(33, 147, 176, 0.3);
  background: rgba(255, 255, 255, 0.06);
}

.partido-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
  flex-wrap: wrap;
}

.partido-etapa {
  font-size: 0.7rem;
  color: #8ecae6;
  background: rgba(33, 147, 176, 0.1);
  padding: 2px 12px;
  border-radius: 10px;
}

.partido-equipos {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 0.95rem;
  font-weight: 500;
  margin-bottom: 8px;
}

.equipo1-nombre {
  color: #6dd5ed;
}

.equipo2-nombre {
  color: #2193b0;
}

.vs-text {
  color: #e63946;
  font-weight: 700;
  font-size: 0.75rem;
}

.partido-detalle {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 0.85rem;
}

.resultado-text {
  font-weight: 700;
  color: #00b4d8;
}

.ganador-tag {
  font-size: 0.65rem;
  color: #48cae4;
  background: rgba(72, 202, 228, 0.15);
  padding: 2px 10px;
  border-radius: 10px;
}

.empate-tag {
  font-size: 0.65rem;
  color: #8ecae6;
  background: rgba(142, 202, 230, 0.15);
  padding: 2px 10px;
  border-radius: 10px;
}

.pendiente-tag {
  color: #e63946;
  font-weight: 600;
}

.partido-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.llaves-wrapper {
  position: relative;
}

.zoom-controls {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  width: fit-content;
}

.zoom-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #e8f0fe;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.zoom-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.05);
}

.zoom-level {
  color: #8ecae6;
  font-size: 13px;
  font-weight: 600;
  min-width: 50px;
  text-align: center;
}

.llaves-container {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: auto;
  width: 100%;
  height: 600px;
  min-height: 400px;
  max-height: 75vh;
  position: relative;
}

.llaves-chart {
  width: 100%;
  height: 100%;
  transform-origin: top left;
  transition: transform 0.15s ease;
}

.llaves-chart svg {
  display: block;
  width: 100%;
  height: 100%;
}

.campeon-box {
  text-align: center;
  padding: 15px;
  margin-top: 15px;
  background: linear-gradient(135deg, rgba(72, 202, 228, 0.15), rgba(72, 202, 228, 0.05));
  border-radius: 12px;
  border: 2px solid rgba(72, 202, 228, 0.2);
}

.trofeo {
  font-size: 2.5rem;
  animation: pulse 2s infinite;
}

.campeon {
  font-size: 1rem;
  font-weight: 700;
  color: #48cae4;
  letter-spacing: 2px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal {
  background: #0a1628;
  border: 1px solid rgba(33, 147, 176, 0.2);
  border-radius: 16px;
  padding: 30px;
  max-width: 450px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal h3 {
  color: #48cae4;
  margin-bottom: 20px;
  text-align: center;
}

.modal-partido {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.modal-equipo1 {
  color: #6dd5ed;
}

.modal-equipo2 {
  color: #2193b0;
}

.modal-vs {
  color: #e63946;
  font-weight: 700;
}

.form-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 100px;
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
  text-align: center;
  transition: all 0.3s ease;
}

.input:focus {
  outline: none;
  border-color: #2193b0;
  box-shadow: 0 0 0 3px rgba(33, 147, 176, 0.15);
}

.info-puntos {
  text-align: center;
  margin: 12px 0;
  padding: 8px;
  background: rgba(72, 202, 228, 0.08);
  border-radius: 8px;
  font-size: 0.8rem;
  color: #8ecae6;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 15px;
}

.modal-actions button {
  padding: 10px 30px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-state p {
  font-size: 1.1rem;
  color: #8ecae6;
  margin-bottom: 15px;
}

.empty-message {
  text-align: center;
  color: #7f8c8d;
  padding: 30px;
  font-style: italic;
}

.llaves-container::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.llaves-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.llaves-container::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
  border-radius: 10px;
}

.llaves-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #6dd5ed, #2193b0);
}

@media (max-width: 768px) {
  .grupos-container {
    grid-template-columns: 1fr 1fr;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .header-actions button {
    flex: 1;
    min-width: 70px;
    font-size: 11px;
    padding: 8px 12px;
  }
  
  .llaves-container {
    height: 400px;
    max-height: 50vh;
    padding: 10px;
  }
  
  .partidos-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .grupos-container {
    grid-template-columns: 1fr;
  }
  
  .zoom-controls {
    width: 100%;
    justify-content: center;
  }
  
  .llaves-container {
    height: 300px;
  }

  .modal {
    padding: 20px;
  }

  .form-row {
    flex-direction: column;
  }

  .form-group {
    min-width: 100%;
  }
}
</style>
