import json
import os
import random

class Jugador:
    def __init__(self, id, nombre, edad):
        self.id = id
        self.nombre = nombre
        self.edad = edad

class Equipo:
    def __init__(self, id, nombre, juvenil_id):
        self.id = id
        self.nombre = nombre
        self.juvenil_id = juvenil_id
        self.jugadores = []
        self.ganados = 0
        self.empatados = 0
        self.perdidos = 0
        self.goles_favor = 0
        self.goles_contra = 0
        self.puntos = 0

class Juvenil:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.equipos = []

class Grupo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.equipos = []
        self.partidos = []

class Partido:
    def __init__(self, id, equipo1_id, equipo2_id, grupo, etapa):
        self.id = id
        self.equipo1 = equipo1_id
        self.equipo2 = equipo2_id
        self.grupo = grupo
        self.etapa = etapa
        self.goles1 = None
        self.goles2 = None
        self.ganador = None
        self.jugado = False

class Torneo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.juveniles = []
        self.equipos = []
        self.grupos = []
        self.partidos = []
        self.archivo = 'torneo_data.json'
        self.contadores = {
            'juvenil': 0,
            'equipo': 0,
            'jugador': 0
        }
        # Configuración
        self.configuracion = {
            'permitir_mismo_juvenil': False  # False = no se enfrentan, True = pueden enfrentarse
        }
    
    def generar_id(self, tipo):
        if tipo not in self.contadores:
            self.contadores[tipo] = 0
        self.contadores[tipo] += 1
        return self.contadores[tipo]
    
    def guardar(self):
        data = {
            'nombre': self.nombre,
            'contadores': self.contadores,
            'juveniles': [],
            'equipos': [],
            'grupos': [],
            'partidos': [],
            'total_equipos': len(self.equipos),
            'configuracion': self.configuracion
        }
        
        for j in self.juveniles:
            data['juveniles'].append({
                'id': j.id,
                'nombre': j.nombre,
                'equipos': [{'id': e.id, 'nombre': e.nombre} for e in j.equipos]
            })
        
        for e in self.equipos:
            data['equipos'].append({
                'id': e.id,
                'nombre': e.nombre,
                'juvenil_id': e.juvenil_id,
                'jugadores': [{'id': j.id, 'nombre': j.nombre, 'edad': j.edad} for j in e.jugadores],
                'ganados': e.ganados,
                'empatados': e.empatados,
                'perdidos': e.perdidos,
                'goles_favor': e.goles_favor,
                'goles_contra': e.goles_contra,
                'puntos': e.puntos
            })
        
        for g in self.grupos:
            data['grupos'].append({
                'nombre': g.nombre,
                'equipos': [{'id': e.id, 'nombre': e.nombre} for e in g.equipos],
                'partidos': [p.id for p in g.partidos]
            })
        
        for p in self.partidos:
            data['partidos'].append({
                'id': p.id,
                'equipo1': p.equipo1,
                'equipo2': p.equipo2,
                'grupo': p.grupo,
                'etapa': p.etapa,
                'goles1': p.goles1,
                'goles2': p.goles2,
                'ganador': p.ganador,
                'jugado': p.jugado
            })
        
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def cargar(self):
        if not os.path.exists(self.archivo):
            return False
        
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.nombre = data.get('nombre', 'Torneo Juvenil 2026')
            self.contadores = data.get('contadores', {'juvenil': 0, 'equipo': 0, 'jugador': 0})
            self.configuracion = data.get('configuracion', {'permitir_mismo_juvenil': False})
            
            self.juveniles = []
            for j_data in data.get('juveniles', []):
                juvenil = Juvenil(j_data['id'], j_data['nombre'])
                self.juveniles.append(juvenil)
            
            self.equipos = []
            for e_data in data.get('equipos', []):
                equipo = Equipo(e_data['id'], e_data['nombre'], e_data['juvenil_id'])
                equipo.ganados = e_data.get('ganados', 0)
                equipo.empatados = e_data.get('empatados', 0)
                equipo.perdidos = e_data.get('perdidos', 0)
                equipo.goles_favor = e_data.get('goles_favor', 0)
                equipo.goles_contra = e_data.get('goles_contra', 0)
                equipo.puntos = e_data.get('puntos', 0)
                for j_data in e_data.get('jugadores', []):
                    jugador = Jugador(j_data['id'], j_data['nombre'], j_data['edad'])
                    equipo.jugadores.append(jugador)
                self.equipos.append(equipo)
            
            for juvenil in self.juveniles:
                juvenil.equipos = [e for e in self.equipos if e.juvenil_id == juvenil.id]
            
            self.partidos = []
            for p_data in data.get('partidos', []):
                partido = Partido(
                    p_data['id'],
                    p_data['equipo1'],
                    p_data['equipo2'],
                    p_data['grupo'],
                    p_data['etapa']
                )
                partido.goles1 = p_data.get('goles1')
                partido.goles2 = p_data.get('goles2')
                partido.ganador = p_data.get('ganador')
                partido.jugado = p_data.get('jugado', False)
                self.partidos.append(partido)
            
            self.grupos = []
            for g_data in data.get('grupos', []):
                grupo = Grupo(g_data['nombre'])
                for e_data in g_data.get('equipos', []):
                    equipo = next((e for e in self.equipos if e.id == e_data['id']), None)
                    if equipo:
                        grupo.equipos.append(equipo)
                for p_id in g_data.get('partidos', []):
                    partido = next((p for p in self.partidos if p.id == p_id), None)
                    if partido:
                        grupo.partidos.append(partido)
                self.grupos.append(grupo)
            
            return True
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            return False
# Agregar al final de la clase Torneo, antes de guardar()

    def get_puntos_config(self):
        """Retorna la configuración de puntos"""
        return {
            'ganado': self.configuracion.get('puntos_ganado', 3),
            'empate': self.configuracion.get('puntos_empate', 1),
            'perdido': self.configuracion.get('puntos_perdido', 0)
        }
