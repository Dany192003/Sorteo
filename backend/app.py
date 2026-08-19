from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
import os
import math
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ===== CONFIGURACIÓN DE SUPABASE =====
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # Usar SOLO service_role

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_KEY son requeridos")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== HEALTH =====
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend funcionando correctamente'})

# ===== TORNEOS =====
@app.route('/api/torneos', methods=['GET', 'OPTIONS'])
def listar_torneos():
    try:
        response = supabase.table('torneos').select('*').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/torneos', methods=['POST', 'OPTIONS'])
def crear_torneo():
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre del torneo es requerido'}), 400
    
    try:
        existing = supabase.table('torneos').select('*').eq('nombre', nombre).execute()
        if existing.data:
            return jsonify({'error': 'Ya existe un torneo con ese nombre'}), 400
        
        response = supabase.table('torneos').insert({
            'nombre': nombre,
            'configuracion': {
                'permitir_mismo_juvenil': False,
                'puntos_ganado': 3,
                'puntos_empate': 1,
                'puntos_perdido': 0
            }
        }).execute()
        
        return jsonify({'message': 'Torneo creado correctamente', 'torneo': response.data[0]}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/torneos/<nombre>', methods=['DELETE', 'OPTIONS'])
def eliminar_torneo(nombre):
    try:
        supabase.table('torneos').delete().eq('nombre', nombre).execute()
        return jsonify({'message': 'Torneo eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/torneos/actual', methods=['GET', 'OPTIONS'])
def get_actual():
    try:
        response = supabase.table('torneos').select('*').eq('nombre', 'torneo_principal').execute()
        if not response.data:
            response = supabase.table('torneos').insert({
                'nombre': 'torneo_principal',
                'configuracion': {
                    'permitir_mismo_juvenil': False,
                    'puntos_ganado': 3,
                    'puntos_empate': 1,
                    'puntos_perdido': 0
                }
            }).execute()
        
        return jsonify({'nombre': response.data[0]['nombre'], 'configuracion': response.data[0]['configuracion']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/torneos/actual', methods=['POST', 'OPTIONS'])
def set_actual():
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre del torneo es requerido'}), 400
    
    try:
        response = supabase.table('torneos').select('*').eq('nombre', nombre).execute()
        if not response.data:
            return jsonify({'error': 'Torneo no encontrado'}), 404
        
        return jsonify({'message': 'Torneo actual cambiado', 'torneo': response.data[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== CONFIGURACIÓN =====
@app.route('/api/configuracion', methods=['GET', 'OPTIONS'])
def get_configuracion():
    try:
        response = supabase.table('torneos').select('configuracion').eq('nombre', 'torneo_principal').execute()
        if response.data:
            return jsonify(response.data[0]['configuracion'])
        return jsonify({'permitir_mismo_juvenil': False, 'puntos_ganado': 3, 'puntos_empate': 1, 'puntos_perdido': 0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuracion', methods=['POST', 'OPTIONS'])
def set_configuracion():
    data = request.json
    
    try:
        response = supabase.table('torneos').select('*').eq('nombre', 'torneo_principal').execute()
        if not response.data:
            return jsonify({'error': 'Torneo no encontrado'}), 404
        
        config = response.data[0].get('configuracion', {})
        config.update(data)
        
        supabase.table('torneos').update({'configuracion': config}).eq('nombre', 'torneo_principal').execute()
        return jsonify({'message': 'Configuración actualizada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== JUVENILES =====
@app.route('/api/juveniles', methods=['GET', 'OPTIONS'])
def get_juveniles():
    try:
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify([])
        
        torneo_id = torneo.data[0]['id']
        response = supabase.table('juveniles').select('*, equipos(*)').eq('torneo_id', torneo_id).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/juveniles', methods=['POST', 'OPTIONS'])
def add_juvenil():
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre es requerido'}), 400
    
    try:
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify({'error': 'Torneo no encontrado'}), 404
        
        torneo_id = torneo.data[0]['id']
        response = supabase.table('juveniles').insert({
            'nombre': nombre,
            'torneo_id': torneo_id
        }).execute()
        
        return jsonify({'message': 'Juvenil agregado correctamente', 'juvenil': response.data[0]}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/juveniles/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_juvenil(id):
    try:
        supabase.table('juveniles').delete().eq('id', id).execute()
        return jsonify({'message': 'Juvenil eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== EQUIPOS =====
@app.route('/api/equipos', methods=['GET', 'OPTIONS'])
def get_equipos():
    try:
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify([])
        
        torneo_id = torneo.data[0]['id']
        response = supabase.table('equipos').select('*, jugadores(*)').eq('torneo_id', torneo_id).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipos', methods=['POST', 'OPTIONS'])
def add_equipo():
    data = request.json
    nombre = data.get('nombre')
    juvenil_id = data.get('juvenil_id')
    
    if not juvenil_id:
        return jsonify({'error': 'Juvenil es requerido'}), 400
    
    try:
        equipos = supabase.table('equipos').select('*').eq('juvenil_id', juvenil_id).execute()
        if len(equipos.data) >= 3:
            return jsonify({'error': 'Este juvenil ya tiene 3 equipos'}), 400
        
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify({'error': 'Torneo no encontrado'}), 404
        
        torneo_id = torneo.data[0]['id']
        
        if not nombre or nombre.strip() == '':
            contador = len(equipos.data) + 1
            juvenil = supabase.table('juveniles').select('nombre').eq('id', juvenil_id).execute()
            if juvenil.data:
                nombre = f"{juvenil.data[0]['nombre']} {contador}"
            else:
                nombre = f"Equipo {contador}"
        
        response = supabase.table('equipos').insert({
            'nombre': nombre,
            'juvenil_id': juvenil_id,
            'torneo_id': torneo_id
        }).execute()
        
        return jsonify({'message': 'Equipo agregado correctamente', 'equipo': response.data[0]}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipos/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_equipo(id):
    try:
        supabase.table('equipos').delete().eq('id', id).execute()
        return jsonify({'message': 'Equipo eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== JUGADORES =====
@app.route('/api/equipos/<int:equipo_id>/jugadores', methods=['POST', 'OPTIONS'])
def add_jugador(equipo_id):
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre es requerido'}), 400
    
    try:
        response = supabase.table('jugadores').insert({
            'nombre': nombre,
            'equipo_id': equipo_id
        }).execute()
        
        return jsonify({'message': 'Jugador agregado correctamente', 'jugador': response.data[0]}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipos/<int:equipo_id>/jugadores/<int:jugador_id>', methods=['DELETE', 'OPTIONS'])
def delete_jugador(equipo_id, jugador_id):
    try:
        supabase.table('jugadores').delete().eq('id', jugador_id).eq('equipo_id', equipo_id).execute()
        return jsonify({'message': 'Jugador eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== GRUPOS =====
@app.route('/api/grupos', methods=['GET', 'OPTIONS'])
def get_grupos():
    try:
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify({'grupos': [], 'llaves': None})
        
        return jsonify({'grupos': [], 'llaves': None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/grupos', methods=['POST', 'OPTIONS'])
def crear_grupos():
    data = request.json
    equipos_por_grupo = data.get('equipos_por_grupo', 4)
    
    try:
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify({'error': 'Torneo no encontrado'}), 404
        
        torneo_id = torneo.data[0]['id']
        equipos = supabase.table('equipos').select('*').eq('torneo_id', torneo_id).execute()
        total_equipos = len(equipos.data)
        
        if total_equipos < 2:
            return jsonify({'error': 'Se necesitan al menos 2 equipos'}), 400
        
        if equipos_por_grupo < 3:
            return jsonify({'error': 'Cada grupo debe tener al menos 3 equipos'}), 400
        
        cantidad_grupos = math.ceil(total_equipos / equipos_por_grupo)
        opciones = [2, 4, 8]
        cantidad_grupos = min(opciones, key=lambda x: abs(x - cantidad_grupos))
        
        return jsonify({
            'message': f'Grupos creados correctamente: {cantidad_grupos} grupos',
            'total_grupos': cantidad_grupos,
            'equipos_por_grupo': equipos_por_grupo,
            'total_equipos': total_equipos,
            'clasificados': cantidad_grupos * 2
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== PARTIDOS =====
@app.route('/api/partidos', methods=['GET', 'OPTIONS'])
def get_partidos():
    try:
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/partidos/<int:partido_id>/resultado', methods=['POST', 'OPTIONS'])
def registrar_resultado(partido_id):
    return jsonify({'message': 'Resultado registrado correctamente'})

@app.route('/api/partidos/<int:partido_id>/en_vivo', methods=['POST', 'OPTIONS'])
def toggle_en_vivo(partido_id):
    return jsonify({'message': 'Estado actualizado'})

# ===== UTILIDADES =====
@app.route('/api/reiniciar_resultados', methods=['POST', 'OPTIONS'])
def reiniciar_resultados():
    try:
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify({'error': 'Torneo no encontrado'}), 404
        
        torneo_id = torneo.data[0]['id']
        
        supabase.table('partidos').update({
            'goles1': None,
            'goles2': None,
            'ganador': None,
            'jugado': False,
            'en_vivo': False
        }).eq('torneo_id', torneo_id).execute()
        
        supabase.table('equipos').update({
            'ganados': 0,
            'empatados': 0,
            'perdidos': 0,
            'goles_favor': 0,
            'goles_contra': 0,
            'puntos': 0
        }).eq('torneo_id', torneo_id).execute()
        
        return jsonify({'message': 'Resultados reiniciados correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vaciar', methods=['POST', 'OPTIONS'])
def vaciar_datos():
    try:
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify({'error': 'Torneo no encontrado'}), 404
        
        torneo_id = torneo.data[0]['id']
        
        supabase.table('partidos').delete().eq('torneo_id', torneo_id).execute()
        supabase.table('grupo_equipos').delete().execute()
        supabase.table('grupos').delete().eq('torneo_id', torneo_id).execute()
        supabase.table('jugadores').delete().execute()
        supabase.table('equipos').delete().eq('torneo_id', torneo_id).execute()
        supabase.table('juveniles').delete().eq('torneo_id', torneo_id).execute()
        
        return jsonify({'message': 'Datos vaciados correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reiniciar', methods=['POST', 'OPTIONS'])
def reiniciar_torneo():
    try:
        torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
        if not torneo.data:
            return jsonify({'error': 'Torneo no encontrado'}), 404
        
        torneo_id = torneo.data[0]['id']
        
        supabase.table('partidos').delete().eq('torneo_id', torneo_id).execute()
        supabase.table('grupo_equipos').delete().execute()
        supabase.table('grupos').delete().eq('torneo_id', torneo_id).execute()
        
        supabase.table('equipos').update({
            'ganados': 0,
            'empatados': 0,
            'perdidos': 0,
            'goles_favor': 0,
            'goles_contra': 0,
            'puntos': 0
        }).eq('torneo_id', torneo_id).execute()
        
        return jsonify({'message': 'Torneo reiniciado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
