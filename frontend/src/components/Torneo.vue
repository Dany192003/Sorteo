<template>
  <div>
    <div class="section-header">
      <h2>🏆 Torneo Generado</h2>
      <div class="header-actions">
        <button @click="$emit('generarTorneo')" class="btn-success">🔄 Regenerar</button>
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
      <p style="color: #bdc3c7; margin-bottom: 15px; font-size: 0.9rem;">
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

      <!-- LLAVES DE ELIMINACIÓN CON D3 -->
      <h3 style="margin-top: 30px;">🏆 LLAVES DE ELIMINACIÓN</h3>

      <div v-if="llaves && (llaves.equipo1 || llaves.equipo2)" class="llaves-wrapper">
        <!-- Controles de zoom -->
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
  </div>
</template>

<script>
import * as d3 from 'd3'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

// ===== Constantes de layout =====
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
    partidos: Array
  },
  emits: ['generarTorneo'],
  data() {
    return {
      zoomLevel: 1,
      zoomTransform: null,
      svgWidth: 0,
      svgHeight: 0
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
        
        // Calcular escala base para que quepa en el contenedor
        const scaleX = containerWidth / (this.svgWidth || 1)
        const scaleY = containerHeight / (this.svgHeight || 1)
        const baseScale = Math.min(scaleX, scaleY, 1) * 0.92
        
        // Aplicar zoom sobre la escala base
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
          backgroundColor: '#1a1a2e',
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

      // Obtener dimensiones del contenedor padre
      const parentRect = this.$refs.llavesContainer
      const containerWidth = parentRect ? parentRect.clientWidth - 40 : 900
      const containerHeight = parentRect ? parentRect.clientHeight - 40 : 600

      // ===== Jerarquía D3 =====
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

      // Calcular dimensiones del árbol
      const treeWidth = maxY - minY + NODE_WIDTH + MARGIN * 2
      const treeHeight = maxX - minX + NODE_HEIGHT + MARGIN * 2

      // Calcular escala para que quepa en el contenedor
      const scaleX = (containerWidth - 20) / treeWidth
      const scaleY = (containerHeight - 20) / treeHeight
      const scale = Math.min(scaleX, scaleY, 1) * 0.95

      // Dimensiones finales del SVG
      const svgWidth = Math.max(treeWidth * scale, containerWidth)
      const svgHeight = Math.max(treeHeight * scale, containerHeight)

      this.svgWidth = svgWidth
      this.svgHeight = svgHeight

      // SVG con viewBox para responsive
      const svg = d3
        .select(container)
        .append('svg')
        .attr('viewBox', `0 0 ${svgWidth} ${svgHeight}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .style('width', '100%')
        .style('height', '100%')
        .style('min-width', `${Math.max(500, svgWidth)}px`)
        .style('min-height', `${Math.max(400, svgHeight)}px`)

      // Calcular offset para centrar el árbol
      const offsetX = (svgWidth - treeWidth * scale) / 2 + MARGIN
      const offsetY = (svgHeight - treeHeight * scale) / 2 + MARGIN

      const g = svg
        .append('g')
        .attr('transform', `translate(${offsetX - minY * scale},${offsetY - minX * scale})`)
        .style('transform-origin', 'top left')

      // Escalar las posiciones de los nodos
      const scalePos = (d) => ({
        x: d.x * scale,
        y: d.y * scale
      })

      // ===== Conectores en L =====
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
        .style('stroke', 'rgba(102, 126, 234, 0.3)')
        .style('stroke-width', `${1.2 * scale}px`)

      // ===== Nodos de partido =====
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

      // Caja contenedora
      nodeGroups
        .append('rect')
        .attr('width', nodeW)
        .attr('height', nodeH)
        .attr('rx', 6 * scale)
        .attr('ry', 6 * scale)
        .style('fill', d => (esFinal(d) ? 'rgba(241, 196, 15, 0.12)' : 'rgba(102, 126, 234, 0.12)'))
        .style('stroke', d => (esFinal(d) ? 'rgba(241, 196, 15, 0.4)' : 'rgba(102, 126, 234, 0.3)'))
        .style('stroke-width', `${1.2 * scale}px`)

      // Línea divisoria
      nodeGroups
        .append('line')
        .attr('x1', 4 * scale)
        .attr('x2', nodeW - 4 * scale)
        .attr('y1', rowH)
        .attr('y2', rowH)
        .style('stroke', 'rgba(255, 255, 255, 0.06)')
        .style('stroke-width', `${0.5 * scale}px`)
        .style('stroke-dasharray', `${4 * scale},${4 * scale}`)

      // Equipo 1
      nodeGroups
        .append('text')
        .attr('x', 10 * scale)
        .attr('y', rowH / 2 + 1)
        .attr('dominant-baseline', 'central')
        .style('fill', '#8fa3f3')
        .style('font-size', `${fontSize}px`)
        .style('font-weight', '500')
        .style('font-family', 'Segoe UI, sans-serif')
        .style('pointer-events', 'none')
        .text(d => truncar(d.data.equipo1))
        .append('title')
        .text(d => d.data.equipo1 || 'Por definir')

      // Equipo 2
      nodeGroups
        .append('text')
        .attr('x', 10 * scale)
        .attr('y', rowH + rowH / 2 + 1)
        .attr('dominant-baseline', 'central')
        .style('fill', '#a58ee0')
        .style('font-size', `${fontSize}px`)
        .style('font-weight', '500')
        .style('font-family', 'Segoe UI, sans-serif')
        .style('pointer-events', 'none')
        .text(d => truncar(d.data.equipo2))
        .append('title')
        .text(d => d.data.equipo2 || 'Por definir')

      // ⚡ para partidos de eliminación (no final)
      nodeGroups
        .filter(d => d.depth > 0 && d.data.equipo1 && d.data.equipo2)
        .append('text')
        .attr('x', nodeW - 14 * scale)
        .attr('y', rowH / 2 + 1)
        .attr('dominant-baseline', 'central')
        .style('fill', '#f1c40f')
        .style('font-size', `${fontSize + 1}px`)
        .style('pointer-events', 'none')
        .text('⚡')
        .append('title')
        .text('Partido de eliminación')

      // ID del partido (esquina superior derecha)
      nodeGroups
        .filter(d => !!d.data.id)
        .append('text')
        .attr('x', nodeW - 6 * scale)
        .attr('y', -6 * scale)
        .attr('text-anchor', 'end')
        .style('fill', '#7f8c8d')
        .style('font-size', `${Math.max(7, fontSize - 2)}px`)
        .style('font-weight', '600')
        .style('font-family', 'monospace')
        .style('pointer-events', 'none')
        .text(d => d.data.id)

      // Hover
      nodeGroups
        .on('mouseenter', function () {
          d3.select(this).select('rect')
            .transition()
            .duration(150)
            .style('stroke-width', `${2 * scale}px`)
            .style('stroke', 'rgba(102, 126, 234, 0.6)')
        })
        .on('mouseleave', function (event, d) {
          d3.select(this)
            .select('rect')
            .transition()
            .duration(150)
            .style('stroke-width', `${1.2 * scale}px`)
            .style('stroke', esFinal(d) ? 'rgba(241, 196, 15, 0.4)' : 'rgba(102, 126, 234, 0.3)')
        })

      // Aplicar zoom inicial
      this.$nextTick(() => {
        this.applyZoom()
      })
    }
  }
}
</script>

<style scoped>
/* ===== HEADER ===== */
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
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-success {
  background: linear-gradient(135deg, #00b894, #00a381);
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
  box-shadow: 0 5px 20px rgba(0, 184, 148, 0.4);
}

.btn-pdf {
  background: linear-gradient(135deg, #e17055, #c0392b);
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
  box-shadow: 0 5px 20px rgba(225, 112, 85, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
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
  background: linear-gradient(135deg, #667eea, #764ba2);
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
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

/* ===== GRUPOS ===== */
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
  color: #f1c40f;
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
  border-left: 3px solid #667eea;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.equipo-item.clasificado {
  border-left-color: #00b894;
  background: rgba(0, 184, 148, 0.08);
}

.clasificado-badge {
  font-size: 0.6rem;
  background: #00b894;
  padding: 2px 8px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
}

/* ===== LLAVES ===== */
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
  color: #fff;
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
  color: #bdc3c7;
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

/* ===== CAMPEÓN ===== */
.campeon-box {
  text-align: center;
  padding: 15px;
  margin-top: 15px;
  background: linear-gradient(135deg, rgba(241, 196, 15, 0.15), rgba(241, 196, 15, 0.05));
  border-radius: 12px;
  border: 2px solid rgba(241, 196, 15, 0.2);
}

.trofeo {
  font-size: 2.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.campeon {
  font-size: 1rem;
  font-weight: 700;
  color: #f1c40f;
  letter-spacing: 2px;
}

/* ===== GENERAL ===== */
.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-state p {
  font-size: 1.1rem;
  color: #bdc3c7;
  margin-bottom: 15px;
}

/* Scrollbar personalizado */
.llaves-container::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.llaves-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.llaves-container::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 10px;
}

.llaves-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2, #667eea);
}

/* ===== RESPONSIVE ===== */
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
}
</style>
