import sqlite3
import os
from datetime import datetime
import sys

def obtener_ruta_db():
    if getattr(sys, 'frozen', False):  # Si es un ejecutable
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, "data", "actividades.db")

DB_PATH = obtener_ruta_db()

# Asegurar que la carpeta 'data' existe
os.makedirs("data", exist_ok=True)

def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_db():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            fecha_creacion TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            nombre TEXT,
            fecha TEXT,
            inicio TEXT,
            fin TEXT,
            duracion REAL,
            comentario TEXT,
            interrupcion REAL,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS defectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            numero INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            encontrado TEXT NOT NULL,
            removido TEXT NOT NULL,
            tiempo_de_compostura REAL NOT NULL,
            defecto_arreglado BOOLEAN NOT NULL,
            descripcion TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def obtener_proyectos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM proyectos")
    proyectos = [p[0] for p in cursor.fetchall()]
    conn.close()
    return proyectos

def agregar_proyecto(nombre):
    conn = conectar()
    cursor = conn.cursor()
    fecha_creacion = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT OR IGNORE INTO proyectos (nombre, fecha_creacion) VALUES (?, ?)", (nombre, fecha_creacion))
    conn.commit()
    conn.close()

def obtener_id_proyecto(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM proyectos WHERE nombre = ?", (nombre,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def guardar_actividad(proyecto_id, nombre, fecha, inicio, fin, duracion, comentario, interrupcion):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO actividades (proyecto_id, nombre, fecha, inicio, fin, duracion, comentario, interrupcion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (proyecto_id, nombre, fecha, inicio, fin, duracion, comentario, interrupcion))
    conn.commit()
    conn.close()
    
def obtener_datos_proyecto(proyecto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre, duracion, fecha, interrupcion FROM actividades WHERE proyecto_id = ?
    """, (proyecto_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_actividades_proyecto(proyecto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, nombre, inicio, fin, interrupcion, duracion, comentario FROM actividades WHERE proyecto_id = ?
    """, (proyecto_id,))
    actividades = cursor.fetchall()
    conn.close()
    return actividades

def borrar_proyecto(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proyectos WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()
