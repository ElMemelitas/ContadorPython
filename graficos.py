from tkinter import messagebox
import matplotlib.pyplot as plt
from database import obtener_datos_proyecto
from collections import defaultdict

def mostrar_grafica(proyecto_id, proyecto_nombre, save_path=None):
    datos = obtener_datos_proyecto(proyecto_id)
    
    if not datos:
        messagebox.showinfo("Información", "No hay actividades registradas en este proyecto.")
        return

    # Agrupar actividades por nombre y sumar sus duraciones
    actividades_duracion = defaultdict(float)
    interrupcion_total = 0
    for nombre, duracion, fecha, interrupcion in datos:
        actividades_duracion[nombre] += duracion
        interrupcion_total += interrupcion if interrupcion is not None else 0

    # Calcular el tiempo total del proyecto
    tiempo_total = sum(actividades_duracion.values()) + interrupcion_total

    # Preparar datos para el gráfico
    actividades = list(actividades_duracion.keys()) + ["Interrupciones"]
    porcentajes = [(duracion / tiempo_total) * 100 for duracion in actividades_duracion.values()] + [(interrupcion_total / tiempo_total) * 100]

    # Definir un conjunto fijo de colores
    colores_fijos = [
        "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF",
        "#33FFF5", "#FF8C33", "#8CFF33", "#338CFF", "#FF338C",
        "#8C33FF", "#33FF8C", "#FF5733", "#33A1FF", "#A1FF33"
    ]

    # Asignar colores a las barras
    colores = [colores_fijos[i % len(colores_fijos)] for i in range(len(actividades))]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(actividades, porcentajes, color=colores)

    # Añadir texto de porcentaje dentro de las barras
    for bar, porcentaje in zip(bars, porcentajes):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f"{round(porcentaje, 2)}%", ha='center', va='bottom')

    plt.xlabel("Actividades")
    plt.ylabel("Porcentaje del tiempo total (%)")
    plt.title(f"Porcentaje de tiempo por actividad en {proyecto_nombre}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()