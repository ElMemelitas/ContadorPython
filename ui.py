import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
from datetime import datetime
from database import *
from graficos import mostrar_grafica

from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from datetime import datetime
import os

from time import ctime
import pygame

# Inicializar pygame mixer
pygame.mixer.init()

proyecto_actual = None
actividad_actual = None
inicio_tiempo = None
pausado = False
pausa_inicio = 0
total_pausa = 0
alerta_mostrada = False
modo_rapido = False

ACTIVIDADES_PREDEFINIDAS = [
    "Planificación", "Diseño", 
    "Código", "Compilación", "Pruebas", "Post Mórtem", "Otra..."
]

def actualizar_proyectos():
    proyectos = obtener_proyectos()
    combo_proyectos["values"] = proyectos
    if proyectos:
        combo_proyectos.current(0)
        seleccionar_proyecto()

def seleccionar_proyecto(*args):
    global proyecto_actual
    proyecto_actual = combo_proyectos.get()
    label_proyecto.config(text=f"Proyecto: {proyecto_actual}")

def crear_proyecto():
    nombre = simpledialog.askstring("Nuevo Proyecto", "Nombre del nuevo proyecto:")
    if nombre:
        agregar_proyecto(nombre)
        actualizar_proyectos()
        combo_proyectos.set(nombre)

def actualizar_reloj():
    global alerta_mostrada
    tiempo_actual = time.strftime("%H:%M:%S")
    label_reloj.config(text=tiempo_actual)
    
    if actividad_actual and inicio_tiempo:
        tiempo_transcurrido = time.time() - inicio_tiempo - total_pausa
        tiempo_pausa = total_pausa if pausado else total_pausa + (time.time() - pausa_inicio if pausado else 0)
        
        if modo_rapido:
            duracion_activa = tiempo_transcurrido * 60  # Cada segundo cuenta como un minuto
            duracion_inactiva = tiempo_pausa * 60
        else:
            duracion_activa = tiempo_transcurrido
            duracion_inactiva = tiempo_pausa

        tiempo_total = duracion_activa + duracion_inactiva

        if not pausado:
            label_tiempo_activo.config(text=f"Tiempo Activo: {int(duracion_activa // 60)}:{int(duracion_activa % 60):02d}")
        """else:
            label_tiempo_inactivo.config(text=f"Tiempo Inactivo: {int(duracion_inactiva // 60)}:{int(duracion_inactiva % 60):02d}")"""

        # Ajustar la condición de la alerta
        if not alerta_mostrada and ((modo_rapido and tiempo_total >= 60) or (not modo_rapido and tiempo_total >= 3600)):
            alerta_mostrada = True
            # Reproducir archivo MP3
            pygame.mixer.music.load("banger.mp3")
            pygame.mixer.music.play(-1)  # Reproducir en bucle

            # Mostrar alerta y esperar a que el usuario la cierre
            messagebox.showwarning("Alerta", "La actividad actual ha durado 60 minutos o más en total.")
            
            # Detener la música después de que el usuario cierre la alerta
            pygame.mixer.music.stop()

    label_reloj.after(1000, actualizar_reloj)

def cambiar_modo():
    global modo_rapido
    modo_rapido = not modo_rapido
    if modo_rapido:
        btn_cambiar_modo.config(text="Modo Normal")
    else:
        btn_cambiar_modo.config(text="Modo Rápido")

def verificar_actividad(*args):
    if combo_actividades.get() == "Otra...":
        nueva_actividad = simpledialog.askstring("Nueva Actividad", "Nombre de la actividad:")
        if nueva_actividad:
            combo_actividades.set(nueva_actividad)
        else:
            combo_actividades.set(ACTIVIDADES_PREDEFINIDAS[0])



# Reemplaza las llamadas a time.time() con obtener_tiempo_ntp()
def disable_close_button():
    root.protocol("WM_DELETE_WINDOW", lambda: None)

def enable_close_button():
    root.protocol("WM_DELETE_WINDOW", root.destroy)

def iniciar():
    global actividad_actual, inicio_tiempo, total_pausa, alerta_mostrada
    if not proyecto_actual:
        messagebox.showwarning("Proyecto", "Selecciona un proyecto primero.")
        return

    actividad_actual = combo_actividades.get()
    if not actividad_actual or actividad_actual == "Otra...":
        messagebox.showwarning("Actividad", "Selecciona una actividad válida.")
        return

    comentario = simpledialog.askstring("Comentario", "Agrega un comentario para esta actividad:")
    if comentario is None:
        comentario = ""

    inicio_tiempo = time.time()
    total_pausa = 0
    alerta_mostrada = False
    label_estado.config(text=f"Actividad: {actividad_actual}")
    btn_iniciar.config(state=tk.DISABLED)
    btn_pausar.config(state=tk.NORMAL)
    btn_parar.config(state=tk.NORMAL)
    btn_defecto.config(state=tk.NORMAL)  # Habilitar el botón de defecto
    combo_actividades.config(state=tk.DISABLED)  # Deshabilitar la selección de actividad

    # Deshabilitar botones adicionales
    combo_proyectos.config(state=tk.DISABLED)
    btn_nuevo_proyecto.config(state=tk.DISABLED)
    btn_cambiar_modo.config(state=tk.DISABLED)
    btn_pdf.config(state=tk.DISABLED)
    
    global comentario_actividad
    comentario_actividad = comentario

    # Deshabilitar el botón de cerrar la ventana
    disable_close_button()

def pausar():
    global pausado, pausa_inicio, total_pausa
    if not pausado:
        pausado = True
        pausa_inicio = time.time()
        btn_pausar.config(text="Reanudar")
        actualizar_tiempo_inactivo()
    else:
        pausado = False
        total_pausa += time.time() - pausa_inicio
        pausa_inicio = 0
        btn_pausar.config(text="Pausar")
        actualizar_tiempo_activo()

def actualizar_tiempo_activo():
    if not pausado and actividad_actual and inicio_tiempo:
        tiempo_transcurrido = time.time() - inicio_tiempo - total_pausa
        if modo_rapido:
            duracion_activa = tiempo_transcurrido * 60
        else:
            duracion_activa = tiempo_transcurrido
        label_tiempo_activo.config(text=f"Tiempo Activo: {int(duracion_activa // 60)}:{int(duracion_activa % 60):02d}")
        label_tiempo_activo.after(1000, actualizar_tiempo_activo)

def actualizar_tiempo_inactivo():
    if pausado and actividad_actual and pausa_inicio:
        tiempo_pausa = total_pausa + (time.time() - pausa_inicio)
        if modo_rapido:
            duracion_inactiva = tiempo_pausa * 60
        else:
            duracion_inactiva = tiempo_pausa
        label_tiempo_inactivo.config(text=f"Tiempo Inactivo: {int(duracion_inactiva // 60)}:{int(duracion_inactiva % 60):02d}")
        label_tiempo_inactivo.after(1000, actualizar_tiempo_inactivo)


def parar():
    global actividad_actual, inicio_tiempo, total_pausa, pausado, alerta_mostrada, comentario_actividad
    if actividad_actual is None or inicio_tiempo is None:
        return

    fin_tiempo = time.time()

    if pausado:
        total_pausa += fin_tiempo - pausa_inicio
        pausado = False

    if modo_rapido:
        duracion = (fin_tiempo - inicio_tiempo - total_pausa) * 60
        total_pausa *= 60  # Ajustar total_pausa para modo rápido
    else:
        duracion = (fin_tiempo - inicio_tiempo) - total_pausa

    if duracion <= 0:
        messagebox.showwarning("Error", "Duración inválida.")
        return

    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    inicio_str = datetime.fromtimestamp(inicio_tiempo).strftime("%H:%M:%S")
    fin_str = datetime.fromtimestamp(fin_tiempo).strftime("%H:%M:%S")

    proyecto_id = obtener_id_proyecto(proyecto_actual)
    guardar_actividad(proyecto_id, actividad_actual, fecha_actual, inicio_str, fin_str, round(duracion / 60, 2), comentario_actividad, round(total_pausa / 60, 2))

    messagebox.showinfo("Guardado", f"Actividad '{actividad_actual}' guardada con {round(duracion / 60, 2)} minutos y {round(total_pausa / 60, 2)} minutos de interrupción.")

    actividad_actual = None
    inicio_tiempo = None
    pausado = False
    alerta_mostrada = False
    comentario_actividad = ""
    label_estado.config(text="Sin actividad")
    btn_iniciar.config(state=tk.NORMAL)
    btn_pausar.config(state=tk.DISABLED, text="Pausar")
    btn_parar.config(state=tk.DISABLED)
    btn_defecto.config(state=tk.DISABLED)  # Deshabilitar el botón de defecto
    combo_actividades.config(state=tk.NORMAL)  # Habilitar la selección de actividad

    # Habilitar botones adicionales
    combo_proyectos.config(state=tk.NORMAL)
    btn_nuevo_proyecto.config(state=tk.NORMAL)
    btn_cambiar_modo.config(state=tk.NORMAL)
    btn_pdf.config(state=tk.NORMAL)
    
    # Reiniciar contadores
    label_tiempo_activo.config(text="Tiempo Activo: 0:00")
    label_tiempo_inactivo.config(text="Tiempo Inactivo: 0:00")

    # Habilitar el botón de cerrar la ventana
    enable_close_button()

def ver_grafica():
    if not proyecto_actual:
        messagebox.showwarning("Proyecto", "Selecciona un proyecto primero.")
        return

    proyecto_id = obtener_id_proyecto(proyecto_actual)
    mostrar_grafica(proyecto_id, proyecto_actual)

def mostrar_tabla():
    if not proyecto_actual:
        messagebox.showwarning("Proyecto", "Selecciona un proyecto primero.")
        return

    proyecto_id = obtener_id_proyecto(proyecto_actual)
    actividades = obtener_actividades_proyecto(proyecto_id)

    if not actividades:
        messagebox.showinfo("Información", "No hay actividades registradas en este proyecto.")
        return

    ventana_tabla = tk.Toplevel(root)
    ventana_tabla.title(f"Actividades de {proyecto_actual}")

    cols = ("Fecha", "Nombre", "Inicio", "Fin", "Interrupción", "Duración", "Comentario")
    tree = ttk.Treeview(ventana_tabla, columns=cols, show='headings')

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, minwidth=0, width=100)

    for actividad in actividades:
        tree.insert("", "end", values=actividad)

    tree.pack(expand=True, fill='both')

def mostrar_tabla_defectos():
    if not proyecto_actual:
        messagebox.showwarning("Proyecto", "Selecciona un proyecto primero.")
        return

    proyecto_id = obtener_id_proyecto(proyecto_actual)
    defectos = obtener_defectos_proyecto(proyecto_id)

    if not defectos:
        messagebox.showinfo("Información", "No hay defectos registrados en este proyecto.")
        return

    ventana_tabla_defectos = tk.Toplevel(root)
    ventana_tabla_defectos.title(f"Defectos de {proyecto_actual}")

    cols = ("Fecha", "Número", "Tipo", "Encontrado", "Removido", "Tiempo de Compostura", "Defecto Arreglado", "Descripción")
    tree = ttk.Treeview(ventana_tabla_defectos, columns=cols, show='headings')

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, minwidth=0, width=100)

    for defecto in defectos:
        tree.insert("", "end", values=defecto)

    tree.pack(expand=True, fill='both')

def obtener_defectos_proyecto(proyecto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, numero, tipo, encontrado, removido, tiempo_de_compostura, defecto_arreglado, descripcion 
        FROM defectos 
        WHERE proyecto_id = ?
    """, (proyecto_id,))
    defectos = cursor.fetchall()
    conn.close()
    return defectos

def generar_pdf(proyecto_id, proyecto_nombre, alumno, instructor):
    actividades = obtener_actividades_proyecto(proyecto_id)
    
    if not actividades:
        messagebox.showinfo("Información", "No hay actividades registradas en este proyecto.")
        return

    archivo_pdf = f"{proyecto_nombre}.pdf"
    doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)
    elements = []

    # Datos del proyecto
    fecha_inicio = actividades[0][0] if actividades else "N/A"
    fecha_descarga = datetime.now().strftime("%Y-%m-%d")

    # Título del proyecto
    styles = getSampleStyleSheet()
    title = f"Proyecto: {proyecto_nombre}"
    elements.append(Paragraph(title, styles['Title']))

    # Alumno e Instructor con más espacio en blanco
    alumno_instructor_text = f"Alumno: {alumno} {' ' * 20} Instructor: {instructor}"
    elements.append(Paragraph(alumno_instructor_text, styles['Normal']))

    # Fecha de inicio
    fecha_inicio_text = f"Fecha de Inicio: {fecha_inicio}"
    elements.append(Paragraph(fecha_inicio_text, styles['Normal']))

    # Fecha de descarga del PDF
    fecha_descarga_text = f"Fecha de Descarga: {fecha_descarga}"
    elements.append(Paragraph(fecha_descarga_text, styles['Normal']))

    # Espacio antes de la tabla
    elements.append(Spacer(1, 12))

    # Encabezados de la tabla
    data = [["Fecha", "Nombre", "Inicio", "Fin", "Interrupción", "Duración", "Comentario"]]

    # Datos de las actividades
    total_duracion = 0
    total_interrupcion = 0
    for actividad in actividades:
        fecha, nombre, inicio, fin, interrupcion, duracion, comentario = actividad
        interrupcion = interrupcion if interrupcion is not None else 0
        duracion = duracion if duracion is not None else 0
        total_duracion += duracion
        total_interrupcion += interrupcion
        data.append([
            str(fecha) if fecha else "",
            str(nombre) if nombre else "",
            str(inicio) if inicio else "",
            str(fin) if fin else "",
            str(interrupcion) if interrupcion else "",
            str(duracion) if duracion else "",
            str(comentario) if comentario else ""
        ])

    # Crear la tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Calcular tiempos en minutos
    tiempo_activo_minutos = total_duracion
    tiempo_inactivo_minutos = total_interrupcion

    # Añadir textos de tiempos en minutos
    elements.append(Spacer(1, 12))
    texto_activo = f"Tiempo Activo: {tiempo_activo_minutos:.2f} minutos"
    elements.append(Paragraph(texto_activo, styles['Normal']))
    texto_inactivo = f"Tiempo Muerto: {tiempo_inactivo_minutos:.2f} minutos"
    elements.append(Paragraph(texto_inactivo, styles['Normal']))

    # Guardar la gráfica como imagen
    grafica_path = f"{proyecto_nombre}_grafica.png"
    mostrar_grafica(proyecto_id, proyecto_nombre, save_path=grafica_path)

    # Añadir una nueva página para la gráfica
    elements.append(PageBreak())
    elements.append(Image(grafica_path, width=500, height=300))

    # Construir el PDF
    doc.build(elements)
    messagebox.showinfo("PDF Generado", f"El PDF ha sido generado: {archivo_pdf}")

    # Eliminar la imagen de la gráfica después de generar el PDF
    os.remove(grafica_path)

def generar_reporte_pdf():
    if not proyecto_actual:
        messagebox.showwarning("Proyecto", "Selecciona un proyecto primero.")
        return

    def guardar_datos():
        alumno = entry_alumno.get().strip()
        instructor = entry_instructor.get().strip()
        if not alumno or not instructor:
            messagebox.showwarning("Campos vacíos", "Por favor, rellena ambos campos.")
            return
        ventana_datos.destroy()
        proyecto_id = obtener_id_proyecto(proyecto_actual)
        generar_pdf(proyecto_id, proyecto_actual, alumno, instructor)

    ventana_datos = tk.Toplevel(root)
    ventana_datos.title("Datos del Reporte")

    tk.Label(ventana_datos, text="Alumno:").grid(row=0, column=0, padx=10, pady=5)
    entry_alumno = tk.Entry(ventana_datos)
    entry_alumno.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(ventana_datos, text="Instructor:").grid(row=1, column=0, padx=10, pady=5)
    entry_instructor = tk.Entry(ventana_datos)
    entry_instructor.grid(row=1, column=1, padx=10, pady=5)

    btn_guardar = tk.Button(ventana_datos, text="Generar PDF", command=guardar_datos)
    btn_guardar.grid(row=2, column=0, columnspan=2, pady=10)

def generar_pdf_defectos(proyecto_id, proyecto_nombre, alumno, instructor):
    defectos = obtener_defectos_proyecto(proyecto_id)
    
    if not defectos:
        messagebox.showinfo("Información", "No hay defectos registrados en este proyecto.")
        return

    archivo_pdf = f"{proyecto_nombre}_defectos.pdf"
    doc = SimpleDocTemplate(archivo_pdf, pagesize=landscape(letter))
    elements = []

    # Datos del proyecto
    fecha_inicio = defectos[0][0] if defectos else "N/A"
    fecha_descarga = datetime.now().strftime("%Y-%m-%d")

    # Título del proyecto
    styles = getSampleStyleSheet()
    title = f"Proyecto: {proyecto_nombre} - Defectos"
    elements.append(Paragraph(title, styles['Title']))

    # Alumno e Instructor con más espacio en blanco
    alumno_instructor_text = f"Alumno: {alumno} {' ' * 20} Instructor: {instructor}"
    elements.append(Paragraph(alumno_instructor_text, styles['Normal']))

    # Fecha de inicio
    fecha_inicio_text = f"Fecha de Inicio: {fecha_inicio}"
    elements.append(Paragraph(fecha_inicio_text, styles['Normal']))

    # Fecha de descarga del PDF
    fecha_descarga_text = f"Fecha de Descarga: {fecha_descarga}"
    elements.append(Paragraph(fecha_descarga_text, styles['Normal']))

    # Espacio antes de la tabla
    elements.append(Spacer(1, 12))

    # Encabezados de la tabla
    data = [["Fecha", "Número", "Tipo", "Encontrado", "Removido", "Tiempo de Compostura", "Defecto Arreglado", "Descripción"]]

    # Datos de los defectos
    total_tiempo_compostura = 0
    for defecto in defectos:
        fecha, numero, tipo, encontrado, removido, tiempo_de_compostura, defecto_arreglado, descripcion = defecto
        tiempo_de_compostura = tiempo_de_compostura if tiempo_de_compostura is not None else 0
        total_tiempo_compostura += tiempo_de_compostura
        defecto_arreglado_text = "Sí" if int(defecto_arreglado) == 1 else "No"
        data.append([
            str(fecha) if fecha else "",
            str(numero) if numero else "",
            str(tipo) if tipo else "",
            str(encontrado) if encontrado else "",
            str(removido) if removido else "",
            str(tiempo_de_compostura) if tiempo_de_compostura else "",
            defecto_arreglado_text,
            str(descripcion) if descripcion else ""
        ])

    # Crear la tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Añadir texto de tiempo total de compostura
    elements.append(Spacer(1, 12))
    texto_tiempo_compostura = f"Tiempo Total de Compostura: {total_tiempo_compostura:.2f} minutos"
    elements.append(Paragraph(texto_tiempo_compostura, styles['Normal']))

    # Construir el PDF
    doc.build(elements)
    messagebox.showinfo("PDF Generado", f"El PDF de defectos ha sido generado: {archivo_pdf}")

def generar_reporte_pdf_defectos():
    if not proyecto_actual:
        messagebox.showwarning("Proyecto", "Selecciona un proyecto primero.")
        return

    def guardar_datos_defectos():
        alumno = entry_alumno.get().strip()
        instructor = entry_instructor.get().strip()
        if not alumno or not instructor:
            messagebox.showwarning("Campos vacíos", "Por favor, rellena ambos campos.")
            return
        ventana_datos.destroy()
        proyecto_id = obtener_id_proyecto(proyecto_actual)
        generar_pdf_defectos(proyecto_id, proyecto_actual, alumno, instructor)

    ventana_datos = tk.Toplevel(root)
    ventana_datos.title("Datos del Reporte de Defectos")

    tk.Label(ventana_datos, text="Alumno:").grid(row=0, column=0, padx=10, pady=5)
    entry_alumno = tk.Entry(ventana_datos)
    entry_alumno.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(ventana_datos, text="Instructor:").grid(row=1, column=0, padx=10, pady=5)
    entry_instructor = tk.Entry(ventana_datos)
    entry_instructor.grid(row=1, column=1, padx=10, pady=5)

    btn_guardar = tk.Button(ventana_datos, text="Generar PDF", command=guardar_datos_defectos)
    btn_guardar.grid(row=2, column=0, columnspan=2, pady=10)

def borrar_proyecto_ui():
    global proyecto_actual
    if not proyecto_actual:
        messagebox.showwarning("Proyecto", "Selecciona un proyecto primero.")
        return

    respuesta = messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas borrar el proyecto '{proyecto_actual}'?")
    if respuesta:
        borrar_proyecto(proyecto_actual)  # Llamada a la función en database.py
        actualizar_proyectos()
        proyecto_actual = None
        label_proyecto.config(text="Proyecto: Ninguno")
        messagebox.showinfo("Proyecto", "Proyecto borrado exitosamente.")

def defecto_encontrado():
    def guardar_defecto():
        fecha = datetime.now().strftime("%Y-%m-%d")
        numero = int(label_numero.cget("text"))
        tipo = combo_tipo.get()
        encontrado = label_encontrado.cget("text")
        removido = combo_removido.get()
        tiempo_de_compostura = round((time.time() - inicio_tiempo_compostura) / 60, 2)  # Convertir a minutos y limitar a 2 decimales
        defecto_arreglado = var_defecto_arreglado.get()
        descripcion = entry_descripcion.get("1.0", tk.END).strip()
        proyecto_id = obtener_id_proyecto(proyecto_actual)

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO defectos (proyecto_id, fecha, numero, tipo, encontrado, removido, tiempo_de_compostura, defecto_arreglado, descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (proyecto_id, fecha, numero, tipo, encontrado, removido, tiempo_de_compostura, defecto_arreglado, descripcion))
        conn.commit()
        conn.close()

        messagebox.showinfo("Guardado", "Defecto guardado exitosamente.")
        ventana_defecto.destroy()

    def obtener_siguiente_numero_defecto():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(numero) FROM defectos")
        max_numero = cursor.fetchone()[0]
        conn.close()
        return (max_numero + 1) if max_numero is not None else 1

    def actualizar_tiempo_compostura():
        tiempo_transcurrido = time.time() - inicio_tiempo_compostura
        label_tiempo_de_compostura.config(text=f"{int(tiempo_transcurrido // 60)}:{int(tiempo_transcurrido % 60):02d}")
        label_tiempo_de_compostura.after(1000, actualizar_tiempo_compostura)

    ventana_defecto = tk.Toplevel(root)
    ventana_defecto.title("Defecto encontrado")

    tk.Label(ventana_defecto, text="Fecha:").grid(row=0, column=0, padx=10, pady=5)
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    label_fecha = tk.Label(ventana_defecto, text=fecha_actual)
    label_fecha.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(ventana_defecto, text="Número:").grid(row=1, column=0, padx=10, pady=5)
    siguiente_numero = obtener_siguiente_numero_defecto()
    label_numero = tk.Label(ventana_defecto, text=siguiente_numero)
    label_numero.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(ventana_defecto, text="Tipo:").grid(row=2, column=0, padx=10, pady=5)
    tipos_defecto = ["Documentación", "Sintaxis", "Construcción/Empacar", "Asignación", "Interfaz", "Chequeo", "Datos", "Función", "Sistema", "Ambiente"]
    combo_tipo = ttk.Combobox(ventana_defecto, values=tipos_defecto, state="readonly")
    combo_tipo.grid(row=2, column=1, padx=10, pady=5)
    combo_tipo.current(0)

    tk.Label(ventana_defecto, text="Encontrado:").grid(row=3, column=0, padx=10, pady=5)
    label_encontrado = tk.Label(ventana_defecto, text=actividad_actual)
    label_encontrado.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(ventana_defecto, text="Removido:").grid(row=4, column=0, padx=10, pady=5)
    actividades_removido = [actividad for actividad in ACTIVIDADES_PREDEFINIDAS if actividad != "Otra..."]
    combo_removido = ttk.Combobox(ventana_defecto, values=actividades_removido, state="readonly")
    combo_removido.grid(row=4, column=1, padx=10, pady=5)
    combo_removido.current(0)

    tk.Label(ventana_defecto, text="Tiempo de compostura:").grid(row=5, column=0, padx=10, pady=5)
    label_tiempo_de_compostura = tk.Label(ventana_defecto, text="0:00")
    label_tiempo_de_compostura.grid(row=5, column=1, padx=10, pady=5)
    inicio_tiempo_compostura = time.time()
    actualizar_tiempo_compostura()

    tk.Label(ventana_defecto, text="Defecto arreglado:").grid(row=6, column=0, padx=10, pady=5)
    var_defecto_arreglado = tk.BooleanVar()
    tk.Checkbutton(ventana_defecto, variable=var_defecto_arreglado).grid(row=6, column=1, padx=10, pady=5)

    tk.Label(ventana_defecto, text="Descripción:").grid(row=7, column=0, padx=10, pady=5)
    entry_descripcion = tk.Text(ventana_defecto, height=5, width=40)
    entry_descripcion.grid(row=7, column=1, padx=10, pady=5)

    btn_guardar_defecto = tk.Button(ventana_defecto, text="Guardar", command=guardar_defecto)
    btn_guardar_defecto.grid(row=8, column=0, columnspan=2, pady=10)

# Crear ventana
root = tk.Tk()
root.title("Contador de Actividades")
root.geometry("600x660")  # Aumentar el tamaño de la ventana

# Aplicar estilo
style = ttk.Style()
style.configure("TLabel", font=("Arial", 12))
style.configure("TButton", font=("Arial", 12))
style.configure("TCombobox", font=("Arial", 12))

# Selección de Proyecto
frame_proyecto = tk.Frame(root, padx=10, pady=10)
frame_proyecto.pack(pady=10)

label_proyecto = ttk.Label(frame_proyecto, text="Selecciona un proyecto:")
label_proyecto.pack(side=tk.LEFT, padx=5)

combo_proyectos = ttk.Combobox(frame_proyecto, state="readonly")
combo_proyectos.pack(side=tk.LEFT, padx=5)
combo_proyectos.bind("<<ComboboxSelected>>", seleccionar_proyecto)

btn_nuevo_proyecto = ttk.Button(frame_proyecto, text="+", command=crear_proyecto)
btn_nuevo_proyecto.pack(side=tk.LEFT, padx=5)

btn_borrar_proyecto = ttk.Button(frame_proyecto, text="Borrar", command=borrar_proyecto_ui)
btn_borrar_proyecto.pack(side=tk.LEFT, padx=5)

# Selección de Actividad
frame_actividad = tk.Frame(root, padx=10, pady=10)
frame_actividad.pack(pady=10)

label_actividad = ttk.Label(frame_actividad, text="Selecciona una actividad:")
label_actividad.pack(side=tk.LEFT, padx=5)

combo_actividades = ttk.Combobox(frame_actividad, state="readonly", values=ACTIVIDADES_PREDEFINIDAS)
combo_actividades.pack(side=tk.LEFT, padx=5)
combo_actividades.current(0)
combo_actividades.bind("<<ComboboxSelected>>", verificar_actividad)

# Reloj
label_reloj = ttk.Label(root, text="", font=("Arial", 16))
label_reloj.pack(pady=10)
actualizar_reloj()

# Contadores de tiempo activo e inactivo
frame_tiempos = tk.Frame(root, padx=10, pady=10)
frame_tiempos.pack(pady=10)

label_tiempo_activo = ttk.Label(frame_tiempos, text="Tiempo Activo: 0:00", font=("Arial", 12))
label_tiempo_activo.pack(side=tk.LEFT, padx=5)

label_tiempo_inactivo = ttk.Label(frame_tiempos, text="Tiempo Inactivo: 0:00", font=("Arial", 12))
label_tiempo_inactivo.pack(side=tk.LEFT, padx=5)

# Estado actual
label_estado = ttk.Label(root, text="Sin actividad", font=("Arial", 12))
label_estado.pack(pady=5)

# Botones de control
frame_botones = tk.Frame(root, padx=10, pady=10)
frame_botones.pack(pady=10)

btn_iniciar = ttk.Button(frame_botones, text="Iniciar", command=iniciar)
btn_iniciar.pack(pady=5)
btn_pausar = ttk.Button(frame_botones, text="Pausar", command=pausar, state=tk.DISABLED)
btn_pausar.pack(pady=5)
btn_parar = ttk.Button(frame_botones, text="Parar", command=parar, state=tk.DISABLED)
btn_parar.pack(pady=5)
btn_defecto = tk.Button(frame_botones, text="Defecto encontrado", command=defecto_encontrado, bg="orange", fg="white", state=tk.DISABLED)
btn_defecto.pack(pady=5)

# Frame para los botones de mostrar tablas
frame_tablas = tk.Frame(frame_botones)
frame_tablas.pack(pady=5)

btn_tabla = ttk.Button(frame_tablas, text="Mostrar Tabla de Actividades", command=mostrar_tabla)
btn_tabla.pack(side=tk.LEFT, padx=5)
btn_tabla_defectos = ttk.Button(frame_tablas, text="Mostrar Tabla de Defectos", command=mostrar_tabla_defectos)
btn_tabla_defectos.pack(side=tk.LEFT, padx=5)

btn_grafica = ttk.Button(frame_botones, text="Mostrar Gráfica", command=ver_grafica)
btn_grafica.pack(pady=10)
btn_cambiar_modo = ttk.Button(frame_botones, text="Modo Rápido", command=cambiar_modo)
btn_cambiar_modo.pack(pady=10)

# Frame para los botones de generar PDF
frame_pdf = tk.Frame(frame_botones)
frame_pdf.pack(pady=10)

btn_pdf = ttk.Button(frame_pdf, text="Generar PDF Actividades", command=generar_reporte_pdf)
btn_pdf.pack(side=tk.LEFT, padx=5)
btn_pdf_defectos = ttk.Button(frame_pdf, text="Generar PDF Defectos", command=generar_reporte_pdf_defectos)
btn_pdf_defectos.pack(side=tk.LEFT, padx=5)

# Cargar proyectos al iniciar
actualizar_proyectos()

root.mainloop()