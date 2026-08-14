from flask import Flask, jsonify, request
from flask_cors import CORS
from torneo import Torneo, Juvenil, Equipo, Grupo, Jugador, Partido
import random
import math

app = Flask(__name__)
CORS(app)

torneo = Torneo("Torneo Juvenil 2026")
torneo.cargar()

# ===== HEALTH =====
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend funcionando correctamente'})

# ===== CONFIGURACIÓN =====
@app.route('/api/configuracion', methods=['GET'])
def get_configuracion():
    return jsonify(torneo.configuracion)

@app.route('/api/configuracion', methods=['POST'])
def set_configuracion():
    data = request.json
    permitir_mismo_juvenil = data.get('permitir_mismo_juvenil')
    if permitir_mismo_juvenil is not None:
        torneo.configuracion['permitir_mismo_juvenil'] = permitir_mismo_juvenil
        torneo.guardar()
    return jsonify({'message': 'Configuración actualizada'})

# ===== JUVENILES =====
@app.route('/api/juveniles', methods=['GET'])
def get_juveniles():
    juveniles_data = []
    for j in torneo.juveniles:
        juveniles_data.append({
            'id': j.id,
            'nombre': j.nombre,
            'equipos': [{'id': e.id, 'nombre': e.nombre} for e in j.equipos]
        })
    return jsonify(juveniles_data)

@app.route('/api/juveniles', methods=['POST'])
def add_juvenil():
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre es requerido'}), 400
    
    juvenil_id = torneo.generar_id('juvenil')
    juvenil = Juvenil(juvenil_id, nombre)
    torneo.juveniles.append(juvenil)
    torneo.guardar()
    
    return jsonify({
        'message': 'Juvenil agregado correctamente',
        'juvenil': {'id': juvenil.id, 'nombre': juvenil.nombre}
    }), 201

@app.route('/api/juveniles/<int:id>', methods=['DELETE'])
def delete_juvenil(id):
    juvenil = next((j for j in torneo.juveniles if j.id == id), None)
    if not juvenil:
        return jsonify({'error': 'Juvenil no encontrado'}), 404
    
    for equipo in juvenil.equipos:
        torneo.equipos = [e for e in torneo.equipos if e.id != equipo.id]
    
    torneo.juveniles = [j for j in torneo.juveniles if j.id != id]
    torneo.grupos = []
    torneo.partidos = []
    torneo.guardar()
    
    return jsonify({'message': 'Juvenil eliminado correctamente'})

# ===== EQUIPOS =====
@app.route('/api/equipos', methods=['GET'])
def get_equipos():
    equipos_data = []
    for e in torneo.equipos:
        equipos_data.append({
            'id': e.id,
            'nombre': e.nombre,
            'juvenil_id': e.juvenil_id,
            'jugadores': [{'id': j.id, 'nombre': j.nombre, 'edad': j.edad} for j in e.jugadores],
            'puntos': e.puntos,
            'ganados': e.ganados,
            'empatados': e.empatados,
            'perdidos': e.perdidos,
            'goles_favor': e.goles_favor,
            'goles_contra': e.goles_contra
        })
    return jsonify(equipos_data)

@app.route('/api/equipos', methods=['POST'])
def add_equipo():
    data = request.json
    nombre = data.get('nombre')
    juvenil_id = data.get('juvenil_id')
    
    if not juvenil_id:
        return jsonify({'error': 'Juvenil es requerido'}), 400
    
    juvenil = next((j for j in torneo.juveniles if j.id == juvenil_id), None)
    if not juvenil:
        return jsonify({'error': 'Juvenil no encontrado'}), 404
    
    equipos_juvenil = [e for e in torneo.equipos if e.juvenil_id == juvenil_id]
    if len(equipos_juvenil) >= 3:
        return jsonify({'error': 'Este juvenil ya tiene 3 equipos'}), 400
    
    if not nombre or nombre.strip() == '':
        contador = len(equipos_juvenil) + 1
        nombre = f"{juvenil.nombre} {contador}"
    
    equipo_id = torneo.generar_id('equipo')
    equipo = Equipo(equipo_id, nombre, juvenil_id)
    torneo.equipos.append(equipo)
    juvenil.equipos.append(equipo)
    torneo.grupos = []
    torneo.partidos = []
    torneo.guardar()
    
    return jsonify({
        'message': 'Equipo agregado correctamente',
        'equipo': {'id': equipo.id, 'nombre': equipo.nombre, 'juvenil_id': equipo.juvenil_id}
    }), 201

@app.route('/api/equipos/<int:id>', methods=['DELETE'])
def delete_equipo(id):
    equipo = next((e for e in torneo.equipos if e.id == id), None)
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404
    
    juvenil = next((j for j in torneo.juveniles if j.id == equipo.juvenil_id), None)
    if juvenil:
        juvenil.equipos = [e for e in juvenil.equipos if e.id != id]
    
    torneo.equipos = [e for e in torneo.equipos if e.id != id]
    torneo.grupos = []
    torneo.partidos = []
    torneo.guardar()
    
    return jsonify({'message': 'Equipo eliminado correctamente'})

# ===== JUGADORES =====
@app.route('/api/equipos/<int:equipo_id>/jugadores', methods=['POST'])
def add_jugador(equipo_id):
    data = request.json
    nombre = data.get('nombre')
    edad = data.get('edad')
    
    if not nombre or not edad:
        return jsonify({'error': 'Nombre y edad son requeridos'}), 400
    
    equipo = next((e for e in torneo.equipos if e.id == equipo_id), None)
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404
    
    jugador_id = torneo.generar_id('jugador')
    jugador = Jugador(jugador_id, nombre, edad)
    equipo.jugadores.append(jugador)
    torneo.guardar()
    
    return jsonify({
        'message': 'Jugador agregado correctamente',
        'jugador': {'id': jugador.id, 'nombre': jugador.nombre, 'edad': jugador.edad}
    }), 201

@app.route('/api/equipos/<int:equipo_id>/jugadores/<int:jugador_id>', methods=['DELETE'])
def delete_jugador(equipo_id, jugador_id):
    equipo = next((e for e in torneo.equipos if e.id == equipo_id), None)
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404
    
    equipo.jugadores = [j for j in equipo.jugadores if j.id != jugador_id]
    torneo.guardar()
    
    return jsonify({'message': 'Jugador eliminado correctamente'})

# ===== GRUPOS =====
@app.route('/api/grupos', methods=['POST'])
def crear_grupos():
    data = request.json
    equipos_por_grupo = data.get('equipos_por_grupo', 4)
    
    total_equipos = len(torneo.equipos)
    if total_equipos < 2:
        return jsonify({'error': 'Se necesitan al menos 2 equipos'}), 400
    
    if equipos_por_grupo < 3:
        return jsonify({'error': 'Cada grupo debe tener al menos 3 equipos'}), 400
    
    # Calcular cantidad de grupos (debe ser potencia de 2)
    cantidad_grupos = math.ceil(total_equipos / equipos_por_grupo)
    
    # Forzar a potencia de 2
    opciones = [2, 4, 8]
    cantidad_grupos = min(opciones, key=lambda x: abs(x - cantidad_grupos))
    
    if total_equipos / cantidad_grupos < 3:
        return jsonify({'error': f'Con {total_equipos} equipos no se pueden crear {cantidad_grupos} grupos (mínimo 3 por grupo)'}), 400
    
    # Limpiar datos anteriores
    torneo.grupos = []
    torneo.partidos = []
    
    # Crear grupos
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i in range(cantidad_grupos):
        grupo = Grupo(f"Grupo {letras[i]}")
        torneo.grupos.append(grupo)
    
    # Distribución balanceada
    equipos_mezclados = torneo.equipos.copy()
    random.shuffle(equipos_mezclados)
    
    grupos_equipos = [[] for _ in range(cantidad_grupos)]
    
    for i, equipo in enumerate(equipos_mezclados):
        grupo_idx = i % cantidad_grupos
        grupos_equipos[grupo_idx].append(equipo)
    
    # Obtener configuración
    permitir_mismo_juvenil = torneo.configuracion.get('permitir_mismo_juvenil', False)
    
    # Resolver conflictos de mismo juvenil (solo si no está permitido)
    if not permitir_mismo_juvenil:
        for _ in range(100):
            hubo_cambio = False
            
            for grupo_idx in range(cantidad_grupos):
                grupo_actual = grupos_equipos[grupo_idx]
                juveniles_en_grupo = {}
                
                for equipo in grupo_actual:
                    if equipo.juvenil_id not in juveniles_en_grupo:
                        juveniles_en_grupo[equipo.juvenil_id] = []
                    juveniles_en_grupo[equipo.juvenil_id].append(equipo)
                
                for juvenil_id, equipos in juveniles_en_grupo.items():
                    if len(equipos) > 1:
                        for equipo_extra in equipos[1:]:
                            for otro_idx in range(cantidad_grupos):
                                if otro_idx == grupo_idx:
                                    continue
                                otro_grupo = grupos_equipos[otro_idx]
                                juvenil_en_otro = any(e.juvenil_id == juvenil_id for e in otro_grupo)
                                if not juvenil_en_otro:
                                    for equipo_otro in otro_grupo:
                                        juvenil_otro_en_grupo_actual = any(e.juvenil_id == equipo_otro.juvenil_id for e in grupo_actual)
                                        if not juvenil_otro_en_grupo_actual:
                                            if equipo_extra in grupo_actual and equipo_otro in otro_grupo:
                                                grupo_actual.remove(equipo_extra)
                                                otro_grupo.remove(equipo_otro)
                                                grupo_actual.append(equipo_otro)
                                                otro_grupo.append(equipo_extra)
                                                hubo_cambio = True
                                                break
                                if hubo_cambio:
                                    break
                        if hubo_cambio:
                            break
                if hubo_cambio:
                    break
            
            if not hubo_cambio:
                break
    
    # Asignar equipos a grupos
    for i, grupo in enumerate(torneo.grupos):
        grupo.equipos = grupos_equipos[i]
    
    # Generar partidos de grupos
    partido_id = 1
    for grupo in torneo.grupos:
        equipos_grupo = grupo.equipos
        for i in range(len(equipos_grupo)):
            for j in range(i + 1, len(equipos_grupo)):
                if not permitir_mismo_juvenil and equipos_grupo[i].juvenil_id == equipos_grupo[j].juvenil_id:
                    continue
                partido = Partido(
                    partido_id,
                    equipos_grupo[i].id,
                    equipos_grupo[j].id,
                    grupo.nombre,
                    'grupos'
                )
                torneo.partidos.append(partido)
                grupo.partidos.append(partido)
                partido_id += 1
    
    # Generar llaves con CRUCE CRUZADO
    llaves = generar_llaves_cruzadas()
    
    grupos_data = []
    for grupo in torneo.grupos:
        partidos_grupo = [p for p in torneo.partidos if p.grupo == grupo.nombre]
        grupos_data.append({
            'nombre': grupo.nombre,
            'equipos': [{'id': e.id, 'nombre': e.nombre, 'juvenil_id': e.juvenil_id} for e in grupo.equipos],
            'partidos': [{
                'id': p.id,
                'equipo1': p.equipo1,
                'equipo2': p.equipo2,
                'jugado': p.jugado,
                'goles1': p.goles1,
                'goles2': p.goles2
            } for p in partidos_grupo]
        })
    
    torneo.guardar()
    
    return jsonify({
        'message': f'Grupos creados correctamente: {cantidad_grupos} grupos',
        'grupos': grupos_data,
        'llaves': llaves,
        'total_grupos': cantidad_grupos,
        'equipos_por_grupo': equipos_por_grupo,
        'total_equipos': total_equipos,
        'clasificados': cantidad_grupos * 2,
        'configuracion': torneo.configuracion
    })

@app.route('/api/grupos', methods=['GET'])
def get_grupos():
    if not torneo.grupos:
        return jsonify({'message': 'No hay grupos creados', 'grupos': [], 'llaves': None})
    
    grupos_data = []
    for grupo in torneo.grupos:
        partidos_grupo = [p for p in torneo.partidos if p.grupo == grupo.nombre]
        grupos_data.append({
            'nombre': grupo.nombre,
            'equipos': [{'id': e.id, 'nombre': e.nombre, 'juvenil_id': e.juvenil_id} for e in grupo.equipos],
            'partidos': [{
                'id': p.id,
                'equipo1': p.equipo1,
                'equipo2': p.equipo2,
                'jugado': p.jugado,
                'goles1': p.goles1,
                'goles2': p.goles2
            } for p in partidos_grupo]
        })
    
    llaves = generar_llaves_cruzadas()
    
    return jsonify({
        'grupos': grupos_data,
        'llaves': llaves,
        'configuracion': torneo.configuracion
    })

# ===== PARTIDOS =====
@app.route('/api/partidos', methods=['GET'])
def get_partidos():
    partidos_data = []
    for p in torneo.partidos:
        equipo1_nombre = next((e.nombre for e in torneo.equipos if e.id == p.equipo1), p.equipo1)
        equipo2_nombre = next((e.nombre for e in torneo.equipos if e.id == p.equipo2), p.equipo2)
        partidos_data.append({
            'id': p.id,
            'equipo1': equipo1_nombre,
            'equipo1_id': p.equipo1,
            'equipo2': equipo2_nombre,
            'equipo2_id': p.equipo2,
            'grupo': p.grupo,
            'etapa': p.etapa,
            'goles1': p.goles1,
            'goles2': p.goles2,
            'ganador': p.ganador,
            'jugado': p.jugado
        })
    return jsonify(partidos_data)

@app.route('/api/partidos/<int:partido_id>/resultado', methods=['POST'])
def registrar_resultado(partido_id):
    data = request.json
    goles1 = data.get('goles1')
    goles2 = data.get('goles2')
    
    if goles1 is None or goles2 is None:
        return jsonify({'error': 'Goles son requeridos'}), 400
    
    partido = next((p for p in torneo.partidos if p.id == partido_id), None)
    if not partido:
        return jsonify({'error': 'Partido no encontrado'}), 404
    
    partido.goles1 = goles1
    partido.goles2 = goles2
    partido.jugado = True
    
    equipo1 = next((e for e in torneo.equipos if e.id == partido.equipo1), None)
    equipo2 = next((e for e in torneo.equipos if e.id == partido.equipo2), None)
    
    if not equipo1 or not equipo2:
        return jsonify({'error': 'Equipo no encontrado'}), 404
    
    if goles1 > goles2:
        partido.ganador = equipo1.nombre
        equipo1.ganados += 1
        equipo1.puntos += 3
        equipo2.perdidos += 1
    elif goles2 > goles1:
        partido.ganador = equipo2.nombre
        equipo2.ganados += 1
        equipo2.puntos += 3
        equipo1.perdidos += 1
    else:
        partido.ganador = 'Empate'
        equipo1.empatados += 1
        equipo1.puntos += 1
        equipo2.empatados += 1
        equipo2.puntos += 1
    
    equipo1.goles_favor += goles1
    equipo1.goles_contra += goles2
    equipo2.goles_favor += goles2
    equipo2.goles_contra += goles1
    
    torneo.guardar()
    
    return jsonify({
        'message': 'Resultado registrado correctamente',
        'partido': {
            'id': partido.id,
            'equipo1': equipo1.nombre,
            'equipo2': equipo2.nombre,
            'goles1': partido.goles1,
            'goles2': partido.goles2,
            'ganador': partido.ganador,
            'jugado': partido.jugado
        }
    })

# ===== LLAVES CRUZADAS =====
def generar_llaves_cruzadas():
    """
    Genera llaves con cruce cruzado estilo mundial:
    1A vs 2B, 1C vs 2D, 1B vs 2A, 1D vs 2C
    """
    if not torneo.grupos:
        return None
    
    # Obtener clasificados (1° y 2° de cada grupo)
    clasificados = {}
    for grupo in torneo.grupos:
        equipos_ordenados = sorted(grupo.equipos, key=lambda e: (-e.puntos, -e.goles_favor, e.goles_contra))
        if len(equipos_ordenados) >= 2:
            clasificados[grupo.nombre] = {
                'primero': equipos_ordenados[0].nombre,
                'segundo': equipos_ordenados[1].nombre
            }
    
    if len(clasificados) < 2:
        return None
    
    # Obtener lista de grupos ordenados
    grupos_ordenados = sorted(clasificados.keys())
    
    # CRUCE CRUZADO
    # Los grupos se emparejan: A-B, C-D, etc.
    cuartos = []
    
    for i in range(0, len(grupos_ordenados), 2):
        if i + 1 < len(grupos_ordenados):
            grupo1 = grupos_ordenados[i]
            grupo2 = grupos_ordenados[i + 1]
            
            # 1° del grupo1 vs 2° del grupo2
            cuartos.append({
                'id': f'P{len(cuartos) + 1}',
                'equipo1': clasificados[grupo1]['primero'],
                'equipo2': clasificados[grupo2]['segundo'],
                'grupo_origen': f'{grupo1} (1°) vs {grupo2} (2°)'
            })
            
            # 1° del grupo2 vs 2° del grupo1
            cuartos.append({
                'id': f'P{len(cuartos) + 1}',
                'equipo1': clasificados[grupo2]['primero'],
                'equipo2': clasificados[grupo1]['segundo'],
                'grupo_origen': f'{grupo2} (1°) vs {grupo1} (2°)'
            })
    
    # Construir árbol para D3
    def construir_arbol_desde_cuartos(cuartos, inicio, fin):
        if fin - inicio == 1:
            # Nodo hoja: un partido de cuartos
            partido = cuartos[inicio]
            return {
                'id': partido['id'],
                'equipo1': partido['equipo1'],
                'equipo2': partido['equipo2'],
                'children': [],
                'grupo_origen': partido['grupo_origen']
            }
        
        mitad = (inicio + fin) // 2
        izquierda = construir_arbol_desde_cuartos(cuartos, inicio, mitad)
        derecha = construir_arbol_desde_cuartos(cuartos, mitad, fin)
        
        # Nodo padre (semifinal o final)
        partido_id = f'P{len(cuartos) + (fin - inicio) // 2}'
        
        return {
            'id': partido_id,
            'equipo1': f'Ganador {izquierda["id"]}',
            'equipo2': f'Ganador {derecha["id"]}',
            'children': [izquierda, derecha]
        }
    
    if len(cuartos) == 0:
        return None
    
    # Construir el árbol completo
    arbol = construir_arbol_desde_cuartos(cuartos, 0, len(cuartos))
    
    # Ajustar IDs para que sean secuenciales
    def renombrar_ids(nodo, contador):
        if nodo['id'].startswith('P'):
            contador[0] += 1
            nodo['id'] = f'P{contador[0]}'
        for child in nodo.get('children', []):
            renombrar_ids(child, contador)
    
    renombrar_ids(arbol, [0])
    
    return arbol

@app.route('/api/vaciar', methods=['POST'])
def vaciar_datos():
    torneo.juveniles = []
    torneo.equipos = []
    torneo.grupos = []
    torneo.partidos = []
    torneo.guardar()
    return jsonify({'message': 'Datos vaciados correctamente'})

@app.route('/api/reiniciar', methods=['POST'])
def reiniciar_torneo():
    torneo.grupos = []
    torneo.partidos = []
    for equipo in torneo.equipos:
        equipo.ganados = 0
        equipo.empatados = 0
        equipo.perdidos = 0
        equipo.goles_favor = 0
        equipo.goles_contra = 0
        equipo.puntos = 0
    torneo.guardar()
    return jsonify({'message': 'Torneo reiniciado correctamente'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
