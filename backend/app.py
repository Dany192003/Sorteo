from flask import Flask, jsonify, request
from flask_cors import CORS
from torneo import Torneo, Juvenil, Equipo, Grupo, Jugador, Partido
import random
import math
import os
import json

app = Flask(__name__)

# ===== CONFIGURACIÓN CORS =====
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning"]
    }
})

# ===== VARIABLES GLOBALES =====
torneos = {}
torneo_actual = None
TORNEOS_DIR = 'torneos'

if not os.path.exists(TORNEOS_DIR):
    os.makedirs(TORNEOS_DIR)

def get_torneo(nombre):
    if nombre not in torneos:
        archivo = os.path.join(TORNEOS_DIR, f'{nombre.replace(" ", "_")}.json')
        torneo = Torneo(nombre, archivo)
        torneo.cargar()
        torneos[nombre] = torneo
    return torneos[nombre]

def get_torneo_actual():
    global torneo_actual
    if torneo_actual is None:
        if os.path.exists(os.path.join(TORNEOS_DIR, 'torneo_principal.json')):
            torneo_actual = get_torneo('torneo_principal')
        else:
            torneo_actual = Torneo('torneo_principal', os.path.join(TORNEOS_DIR, 'torneo_principal.json'))
            torneo_actual.cargar()
            torneos['torneo_principal'] = torneo_actual
    return torneo_actual

# ===== HEALTH =====
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend funcionando correctamente'})

# ===== TORNEOS =====
@app.route('/api/torneos', methods=['GET', 'OPTIONS'])
def listar_torneos():
    archivos = [f for f in os.listdir(TORNEOS_DIR) if f.endswith('.json')]
    torneos_list = []
    for archivo in archivos:
        nombre = archivo.replace('.json', '').replace('_', ' ')
        torneos_list.append({
            'nombre': nombre,
            'archivo': archivo
        })
    return jsonify(torneos_list)

@app.route('/api/torneos', methods=['POST', 'OPTIONS'])
def crear_torneo():
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre del torneo es requerido'}), 400
    
    archivo = os.path.join(TORNEOS_DIR, f'{nombre.replace(" ", "_")}.json')
    if os.path.exists(archivo):
        return jsonify({'error': 'Ya existe un torneo con ese nombre'}), 400
    
    nuevo_torneo = Torneo(nombre, archivo)
    nuevo_torneo.guardar()
    torneos[nombre] = nuevo_torneo
    
    return jsonify({
        'message': 'Torneo creado correctamente',
        'torneo': {'nombre': nombre}
    }), 201

@app.route('/api/torneos/<nombre>', methods=['DELETE', 'OPTIONS'])
def eliminar_torneo(nombre):
    archivo = os.path.join(TORNEOS_DIR, f'{nombre.replace(" ", "_")}.json')
    if not os.path.exists(archivo):
        return jsonify({'error': 'Torneo no encontrado'}), 404
    
    os.remove(archivo)
    if nombre in torneos:
        del torneos[nombre]
    
    return jsonify({'message': 'Torneo eliminado correctamente'})

@app.route('/api/torneos/actual', methods=['GET', 'OPTIONS'])
def get_actual():
    torneo = get_torneo_actual()
    return jsonify({
        'nombre': torneo.nombre,
        'configuracion': torneo.configuracion
    })

@app.route('/api/torneos/actual', methods=['POST', 'OPTIONS'])
def set_actual():
    global torneo_actual
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre del torneo es requerido'}), 400
    
    archivo = os.path.join(TORNEOS_DIR, f'{nombre.replace(" ", "_")}.json')
    if not os.path.exists(archivo):
        return jsonify({'error': 'Torneo no encontrado'}), 404
    
    torneo_actual = get_torneo(nombre)
    return jsonify({
        'message': 'Torneo actual cambiado',
        'torneo': {'nombre': torneo_actual.nombre}
    })

# ===== CONFIGURACIÓN =====
@app.route('/api/configuracion', methods=['GET', 'OPTIONS'])
def get_configuracion():
    torneo = get_torneo_actual()
    return jsonify(torneo.configuracion)

@app.route('/api/configuracion', methods=['POST', 'OPTIONS'])
def set_configuracion():
    torneo = get_torneo_actual()
    data = request.json
    permitir_mismo_juvenil = data.get('permitir_mismo_juvenil')
    puntos_ganado = data.get('puntos_ganado')
    puntos_empate = data.get('puntos_empate')
    puntos_perdido = data.get('puntos_perdido')
    
    if permitir_mismo_juvenil is not None:
        torneo.configuracion['permitir_mismo_juvenil'] = permitir_mismo_juvenil
    
    if puntos_ganado is not None:
        torneo.configuracion['puntos_ganado'] = int(puntos_ganado)
    if puntos_empate is not None:
        torneo.configuracion['puntos_empate'] = int(puntos_empate)
    if puntos_perdido is not None:
        torneo.configuracion['puntos_perdido'] = int(puntos_perdido)
    
    torneo.guardar()
    return jsonify({'message': 'Configuración actualizada'})

# ===== JUVENILES =====
@app.route('/api/juveniles', methods=['GET', 'OPTIONS'])
def get_juveniles():
    torneo = get_torneo_actual()
    juveniles_data = []
    for j in torneo.juveniles:
        juveniles_data.append({
            'id': j.id,
            'nombre': j.nombre,
            'equipos': [{'id': e.id, 'nombre': e.nombre} for e in j.equipos]
        })
    return jsonify(juveniles_data)

@app.route('/api/juveniles', methods=['POST', 'OPTIONS'])
def add_juvenil():
    torneo = get_torneo_actual()
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

@app.route('/api/juveniles/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_juvenil(id):
    torneo = get_torneo_actual()
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
@app.route('/api/equipos', methods=['GET', 'OPTIONS'])
def get_equipos():
    torneo = get_torneo_actual()
    equipos_data = []
    for e in torneo.equipos:
        equipos_data.append({
            'id': e.id,
            'nombre': e.nombre,
            'juvenil_id': e.juvenil_id,
            'jugadores': [{'id': j.id, 'nombre': j.nombre} for j in e.jugadores],
            'puntos': e.puntos,
            'ganados': e.ganados,
            'empatados': e.empatados,
            'perdidos': e.perdidos,
            'goles_favor': e.goles_favor,
            'goles_contra': e.goles_contra
        })
    return jsonify(equipos_data)

@app.route('/api/equipos', methods=['POST', 'OPTIONS'])
def add_equipo():
    torneo = get_torneo_actual()
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

@app.route('/api/equipos/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_equipo(id):
    torneo = get_torneo_actual()
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
@app.route('/api/equipos/<int:equipo_id>/jugadores', methods=['POST', 'OPTIONS'])
def add_jugador(equipo_id):
    torneo = get_torneo_actual()
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre es requerido'}), 400
    
    equipo = next((e for e in torneo.equipos if e.id == equipo_id), None)
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404
    
    jugador_id = torneo.generar_id('jugador')
    jugador = Jugador(jugador_id, nombre)
    equipo.jugadores.append(jugador)
    torneo.guardar()
    
    return jsonify({
        'message': 'Jugador agregado correctamente',
        'jugador': {'id': jugador.id, 'nombre': jugador.nombre}
    }), 201

@app.route('/api/equipos/<int:equipo_id>/jugadores/<int:jugador_id>', methods=['DELETE', 'OPTIONS'])
def delete_jugador(equipo_id, jugador_id):
    torneo = get_torneo_actual()
    equipo = next((e for e in torneo.equipos if e.id == equipo_id), None)
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404
    
    equipo.jugadores = [j for j in equipo.jugadores if j.id != jugador_id]
    torneo.guardar()
    
    return jsonify({'message': 'Jugador eliminado correctamente'})

# ===== GRUPOS =====
@app.route('/api/grupos', methods=['GET', 'OPTIONS'])
def get_grupos():
    torneo = get_torneo_actual()
    if not torneo.grupos:
        return jsonify({'message': 'No hay grupos creados', 'grupos': [], 'llaves': None})
    
    grupos_data = []
    for grupo in torneo.grupos:
        partidos_grupo = [p for p in torneo.partidos if p.grupo == grupo.nombre]
        grupos_data.append({
            'nombre': grupo.nombre,
            'equipos': [{
                'id': e.id,
                'nombre': e.nombre,
                'juvenil_id': e.juvenil_id,
                'ganados': e.ganados,
                'empatados': e.empatados,
                'perdidos': e.perdidos,
                'goles_favor': e.goles_favor,
                'goles_contra': e.goles_contra,
                'puntos': e.puntos
            } for e in grupo.equipos],
            'partidos': [{
                'id': p.id,
                'equipo1': p.equipo1,
                'equipo2': p.equipo2,
                'jugado': p.jugado,
                'goles1': p.goles1,
                'goles2': p.goles2
            } for p in partidos_grupo]
        })
    
    llaves = generar_llaves_cruzadas(torneo)
    
    return jsonify({
        'grupos': grupos_data,
        'llaves': llaves,
        'configuracion': torneo.configuracion
    })

@app.route('/api/grupos', methods=['POST', 'OPTIONS'])
def crear_grupos():
    torneo = get_torneo_actual()
    data = request.json
    equipos_por_grupo = data.get('equipos_por_grupo', 4)
    
    total_equipos = len(torneo.equipos)
    if total_equipos < 2:
        return jsonify({'error': 'Se necesitan al menos 2 equipos'}), 400
    
    if equipos_por_grupo < 3:
        return jsonify({'error': 'Cada grupo debe tener al menos 3 equipos'}), 400
    
    cantidad_grupos = math.ceil(total_equipos / equipos_por_grupo)
    opciones = [2, 4, 8]
    cantidad_grupos = min(opciones, key=lambda x: abs(x - cantidad_grupos))
    
    if total_equipos / cantidad_grupos < 3:
        return jsonify({'error': f'Con {total_equipos} equipos no se pueden crear {cantidad_grupos} grupos (mínimo 3 por grupo)'}), 400
    
    for equipo in torneo.equipos:
        equipo.ganados = 0
        equipo.empatados = 0
        equipo.perdidos = 0
        equipo.goles_favor = 0
        equipo.goles_contra = 0
        equipo.puntos = 0
    
    torneo.grupos = []
    torneo.partidos = []
    
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i in range(cantidad_grupos):
        grupo = Grupo(f"Grupo {letras[i]}")
        torneo.grupos.append(grupo)
    
    equipos_mezclados = torneo.equipos.copy()
    random.shuffle(equipos_mezclados)
    
    grupos_equipos = [[] for _ in range(cantidad_grupos)]
    
    for i, equipo in enumerate(equipos_mezclados):
        grupo_idx = i % cantidad_grupos
        grupos_equipos[grupo_idx].append(equipo)
    
    permitir_mismo_juvenil = torneo.configuracion.get('permitir_mismo_juvenil', False)
    
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
    
    for i, grupo in enumerate(torneo.grupos):
        grupo.equipos = grupos_equipos[i]
    
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
    
    llaves = generar_llaves_cruzadas(torneo)
    
    grupos_data = []
    for grupo in torneo.grupos:
        partidos_grupo = [p for p in torneo.partidos if p.grupo == grupo.nombre]
        grupos_data.append({
            'nombre': grupo.nombre,
            'equipos': [{
                'id': e.id,
                'nombre': e.nombre,
                'juvenil_id': e.juvenil_id,
                'ganados': e.ganados,
                'empatados': e.empatados,
                'perdidos': e.perdidos,
                'goles_favor': e.goles_favor,
                'goles_contra': e.goles_contra,
                'puntos': e.puntos
            } for e in grupo.equipos],
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

# ===== PARTIDOS =====
@app.route('/api/partidos', methods=['GET', 'OPTIONS'])
def get_partidos():
    torneo = get_torneo_actual()
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

@app.route('/api/partidos/<int:partido_id>/resultado', methods=['OPTIONS'])
def options_resultado(partido_id):
    return '', 200

@app.route('/api/partidos/<int:partido_id>/resultado', methods=['POST'])
def registrar_resultado(partido_id):
    torneo = get_torneo_actual()
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
    
    puntos_ganado = torneo.configuracion.get('puntos_ganado', 3)
    puntos_empate = torneo.configuracion.get('puntos_empate', 1)
    puntos_perdido = torneo.configuracion.get('puntos_perdido', 0)
    
    if goles1 > goles2:
        partido.ganador = equipo1.nombre
        equipo1.ganados += 1
        equipo1.puntos += puntos_ganado
        equipo2.perdidos += 1
        equipo2.puntos += puntos_perdido
    elif goles2 > goles1:
        partido.ganador = equipo2.nombre
        equipo2.ganados += 1
        equipo2.puntos += puntos_ganado
        equipo1.perdidos += 1
        equipo1.puntos += puntos_perdido
    else:
        partido.ganador = 'Empate'
        equipo1.empatados += 1
        equipo1.puntos += puntos_empate
        equipo2.empatados += 1
        equipo2.puntos += puntos_empate
    
    equipo1.goles_favor += goles1
    equipo1.goles_contra += goles2
    equipo2.goles_favor += goles2
    equipo2.goles_contra += goles1
    
    llaves = generar_llaves_cruzadas(torneo)
    
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
        },
        'llaves_actualizadas': llaves
    })

# ===== REINICIAR RESULTADOS =====
@app.route('/api/reiniciar_resultados', methods=['POST', 'OPTIONS'])
def reiniciar_resultados():
    torneo = get_torneo_actual()
    
    for partido in torneo.partidos:
        partido.goles1 = None
        partido.goles2 = None
        partido.ganador = None
        partido.jugado = False
    
    for equipo in torneo.equipos:
        equipo.ganados = 0
        equipo.empatados = 0
        equipo.perdidos = 0
        equipo.goles_favor = 0
        equipo.goles_contra = 0
        equipo.puntos = 0
    
    torneo.guardar()
    
    return jsonify({'message': 'Resultados reiniciados correctamente'})

# ===== LLAVES CRUZADAS (CORREGIDO) =====
def generar_llaves_cruzadas(torneo):
    if not torneo.grupos:
        return None
    
    # Obtener clasificados (1° y 2° de cada grupo)
    clasificados = {}
    for grupo in torneo.grupos:
        equipos_ordenados = sorted(grupo.equipos, key=lambda e: (-e.puntos, -e.goles_favor, e.goles_contra))
        if len(equipos_ordenados) >= 2:
            clasificados[grupo.nombre] = {
                'primero': equipos_ordenados[0].nombre,
                'segundo': equipos_ordenados[1].nombre,
                'primero_id': equipos_ordenados[0].id,
                'segundo_id': equipos_ordenados[1].id
            }
    
    if len(clasificados) < 2:
        return None
    
    grupos_ordenados = sorted(clasificados.keys())
    
    # Crear partidos de cuartos de final (cruce cruzado)
    # 1A vs 2B, 1C vs 2D, 1B vs 2A, 1D vs 2C
    cuartos = []
    for i in range(0, len(grupos_ordenados), 2):
        if i + 1 < len(grupos_ordenados):
            grupo1 = grupos_ordenados[i]
            grupo2 = grupos_ordenados[i + 1]
            
            # Partido 1: 1° del grupo1 vs 2° del grupo2
            cuartos.append({
                'id': f'P{len(cuartos) + 1}',
                'equipo1': clasificados[grupo1]['primero'],
                'equipo2': clasificados[grupo2]['segundo'],
                'equipo1_id': clasificados[grupo1]['primero_id'],
                'equipo2_id': clasificados[grupo2]['segundo_id']
            })
            
            # Partido 2: 1° del grupo2 vs 2° del grupo1
            cuartos.append({
                'id': f'P{len(cuartos) + 1}',
                'equipo1': clasificados[grupo2]['primero'],
                'equipo2': clasificados[grupo1]['segundo'],
                'equipo1_id': clasificados[grupo2]['primero_id'],
                'equipo2_id': clasificados[grupo1]['segundo_id']
            })
    
    # Construir árbol de eliminación
    def construir_arbol(partidos, inicio, fin):
        if fin - inicio == 1:
            p = partidos[inicio]
            return {
                'id': p['id'],
                'equipo1': p['equipo1'],
                'equipo2': p['equipo2'],
                'children': []
            }
        
        mitad = (inicio + fin) // 2
        izquierda = construir_arbol(partidos, inicio, mitad)
        derecha = construir_arbol(partidos, mitad, fin)
        
        nuevo_id = f'P{len(partidos) + (fin - inicio) // 2}'
        
        return {
            'id': nuevo_id,
            'equipo1': f'Ganador {izquierda["id"]}',
            'equipo2': f'Ganador {derecha["id"]}',
            'children': [izquierda, derecha]
        }
    
    if len(cuartos) == 0:
        return None
    
    # Construir el árbol completo
    arbol = construir_arbol(cuartos, 0, len(cuartos))
    
    # Renombrar IDs para que sean secuenciales
    def renombrar(nodo, contador):
        if nodo['id'].startswith('P'):
            contador[0] += 1
            nodo['id'] = f'P{contador[0]}'
        for child in nodo.get('children', []):
            renombrar(child, contador)
    
    renombrar(arbol, [0])
    
    return arbol

@app.route('/api/vaciar', methods=['POST', 'OPTIONS'])
def vaciar_datos():
    torneo = get_torneo_actual()
    torneo.juveniles = []
    torneo.equipos = []
    torneo.grupos = []
    torneo.partidos = []
    torneo.guardar()
    return jsonify({'message': 'Datos vaciados correctamente'})

@app.route('/api/reiniciar', methods=['POST', 'OPTIONS'])
def reiniciar_torneo():
    torneo = get_torneo_actual()
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
