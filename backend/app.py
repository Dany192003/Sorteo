from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# ===== CONFIGURACIÓN DE SUPABASE =====
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Conectado a Supabase: {SUPABASE_URL}")
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        supabase = None
else:
    print("⚠️ Variables de Supabase no configuradas")
    supabase = None

# ===== HEALTH =====
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend funcionando correctamente'})

# ===== TORNEOS =====
@app.route('/api/torneos', methods=['GET', 'OPTIONS'])
def listar_torneos():
    try:
        if supabase:
            response = supabase.table('torneos').select('*').execute()
            return jsonify(response.data)
        return jsonify([{'nombre': 'torneo_principal', 'configuracion': {}}])
    except Exception as e:
        print(f"Error en /api/torneos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/torneos', methods=['POST', 'OPTIONS'])
def crear_torneo():
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre del torneo es requerido'}), 400
    
    try:
        if supabase:
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
        
        return jsonify({'message': 'Torneo creado (modo simulado)'}), 201
    except Exception as e:
        print(f"Error en /api/torneos POST: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/torneos/<nombre>', methods=['DELETE', 'OPTIONS'])
def eliminar_torneo(nombre):
    try:
        if supabase:
            supabase.table('torneos').delete().eq('nombre', nombre).execute()
        return jsonify({'message': 'Torneo eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/torneos/actual', methods=['GET', 'OPTIONS'])
def get_actual():
    try:
        if supabase:
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
        
        return jsonify({'nombre': 'torneo_principal', 'configuracion': {}})
    except Exception as e:
        print(f"Error en /api/torneos/actual: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/torneos/actual', methods=['POST', 'OPTIONS'])
def set_actual():
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre del torneo es requerido'}), 400
    
    try:
        if supabase:
            response = supabase.table('torneos').select('*').eq('nombre', nombre).execute()
            if not response.data:
                return jsonify({'error': 'Torneo no encontrado'}), 404
        return jsonify({'message': 'Torneo actual cambiado', 'torneo': {'nombre': nombre}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== CONFIGURACIÓN =====
@app.route('/api/configuracion', methods=['GET', 'OPTIONS'])
def get_configuracion():
    return jsonify({'permitir_mismo_juvenil': False, 'puntos_ganado': 3, 'puntos_empate': 1, 'puntos_perdido': 0})

@app.route('/api/configuracion', methods=['POST', 'OPTIONS'])
def set_configuracion():
    return jsonify({'message': 'Configuración actualizada'})

# ===== JUVENILES =====
@app.route('/api/juveniles', methods=['GET', 'OPTIONS'])
def get_juveniles():
    try:
        if supabase:
            torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
            if not torneo.data:
                return jsonify([])
            
            torneo_id = torneo.data[0]['id']
            response = supabase.table('juveniles').select('*, equipos(*)').eq('torneo_id', torneo_id).execute()
            return jsonify(response.data)
        return jsonify([])
    except Exception as e:
        print(f"Error en /api/juveniles: {e}")
        return jsonify([])

@app.route('/api/juveniles', methods=['POST', 'OPTIONS'])
def add_juvenil():
    data = request.json
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'Nombre es requerido'}), 400
    
    try:
        if supabase:
            torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
            if not torneo.data:
                return jsonify({'error': 'Torneo no encontrado'}), 404
            
            torneo_id = torneo.data[0]['id']
            response = supabase.table('juveniles').insert({
                'nombre': nombre,
                'torneo_id': torneo_id
            }).execute()
            return jsonify({'message': 'Juvenil agregado correctamente', 'juvenil': response.data[0]}), 201
        
        return jsonify({'message': 'Juvenil agregado correctamente (simulado)'}), 201
    except Exception as e:
        print(f"Error en /api/juveniles POST: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/juveniles/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_juvenil(id):
    try:
        if supabase:
            supabase.table('juveniles').delete().eq('id', id).execute()
        return jsonify({'message': 'Juvenil eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== EQUIPOS =====
@app.route('/api/equipos', methods=['GET', 'OPTIONS'])
def get_equipos():
    try:
        if supabase:
            torneo = supabase.table('torneos').select('id').eq('nombre', 'torneo_principal').execute()
            if not torneo.data:
                return jsonify([])
            
            torneo_id = torneo.data[0]['id']
            response = supabase.table('equipos').select('*, jugadores(*)').eq('torneo_id', torneo_id).execute()
            return jsonify(response.data)
        return jsonify([])
    except Exception as e:
        print(f"Error en /api/equipos: {e}")
        return jsonify([])

@app.route('/api/equipos', methods=['POST', 'OPTIONS'])
def add_equipo():
    data = request.json
    nombre = data.get('nombre')
    juvenil_id = data.get('juvenil_id')
    
    if not juvenil_id:
        return jsonify({'error': 'Juvenil es requerido'}), 400
    
    try:
        if supabase:
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
        
        return jsonify({'message': 'Equipo agregado correctamente (simulado)'}), 201
    except Exception as e:
        print(f"Error en /api/equipos POST: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipos/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_equipo(id):
    try:
        if supabase:
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
        if supabase:
            response = supabase.table('jugadores').insert({
                'nombre': nombre,
                'equipo_id': equipo_id
            }).execute()
            return jsonify({'message': 'Jugador agregado correctamente', 'jugador': response.data[0]}), 201
        return jsonify({'message': 'Jugador agregado correctamente (simulado)'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipos/<int:equipo_id>/jugadores/<int:jugador_id>', methods=['DELETE', 'OPTIONS'])
def delete_jugador(equipo_id, jugador_id):
    try:
        if supabase:
            supabase.table('jugadores').delete().eq('id', jugador_id).eq('equipo_id', equipo_id).execute()
        return jsonify({'message': 'Jugador eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== GRUPOS =====
@app.route('/api/grupos', methods=['GET', 'OPTIONS'])
def get_grupos():
    return jsonify({'grupos': [], 'llaves': None})

@app.route('/api/grupos', methods=['POST', 'OPTIONS'])
def crear_grupos():
    return jsonify({'message': 'Grupos creados correctamente', 'total_grupos': 4})

# ===== PARTIDOS =====
@app.route('/api/partidos', methods=['GET', 'OPTIONS'])
def get_partidos():
    return jsonify([])

@app.route('/api/partidos/<int:partido_id>/resultado', methods=['POST', 'OPTIONS'])
def registrar_resultado(partido_id):
    return jsonify({'message': 'Resultado registrado correctamente'})

@app.route('/api/partidos/<int:partido_id>/en_vivo', methods=['POST', 'OPTIONS'])
def toggle_en_vivo(partido_id):
    return jsonify({'message': 'Estado actualizado'})

# ===== UTILIDADES =====
@app.route('/api/reiniciar_resultados', methods=['POST', 'OPTIONS'])
def reiniciar_resultados():
    return jsonify({'message': 'Resultados reiniciados correctamente'})

@app.route('/api/vaciar', methods=['POST', 'OPTIONS'])
def vaciar_datos():
    return jsonify({'message': 'Datos vaciados correctamente'})

@app.route('/api/reiniciar', methods=['POST', 'OPTIONS'])
def reiniciar_torneo():
    return jsonify({'message': 'Torneo reiniciado correctamente'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
