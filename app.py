# Imports estándar de Python
import os
import re
#import gettext

# Imports de bibliotecas de terceros
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# Own Imports
#from resources.messages import _ 
from config import *
from service.audio_service import process_video, segmentar_audio, dividir_audios
from service.text_service import generar_textos, generar_documento, mostrar_descargar_documento

def configure_page():
    logo = Image.open(os.path.join("static","logo.ico"))    
    st.set_page_config(page_title=APP_TITLE, page_icon=logo, layout="wide")

# Inicializar sesión y datos
def initialize_session_data():
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({HORARIO_INICIO: [], HORARIO_FIN: []})
    
    if 'times' not in st.session_state:
        st.session_state.times = []

# Limpiar formulario
def clear_form():
    st.session_state[KEY_HORA_INICIO] = ""
    st.session_state[KEY_HORA_FIN] = ""

# Verifica si el formato del tiempo es correcto (0h 0m 0s).
def is_valid_time_format(time_str):    
    pattern = r'^\d+h \d+m \d+s$'
    return re.match(pattern, time_str) is not None

# Convierte una cadena en formato '1h 5m 33s' a milisegundos.
def time_to_milliseconds(time_str):    
    hours = minutes = seconds = 0
    matches = re.findall(r'(\d+)([hms])', time_str)
    
    for value, unit in matches:
        if unit == HH:
            hours = int(value)
        elif unit == MM:
            minutes = int(value)
        elif unit == SS:
            seconds = int(value)
    
    return (hours * 3600 + minutes * 60 + seconds) * 1000

# Añadir nueva fila al DataFrame
def add_dfForm():
    horaInicio = st.session_state[KEY_HORA_INICIO]
    horaFin = st.session_state[KEY_HORA_FIN]
    
    if not is_valid_time_format(horaInicio) or not is_valid_time_format(horaFin):
                 st.error(VALID_TIME_ERROR)
    elif horaInicio and horaFin:
         new_row = pd.DataFrame({HORARIO_INICIO: [horaInicio], HORARIO_FIN: [horaFin]})
         st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
         st.info(INTERVALO_AGREGADO)
         clear_form()

# Crear una colección con los valores de horaInicio y horaFin
def add_interval_time():
    #hour_pairs = []  # Lista para almacenar los pares de horas
    for index, row in st.session_state.data.iterrows():  # Iteramos sobre las filas
        hora_inicio = row[HORARIO_INICIO]
        hora_fin = row[HORARIO_FIN]

        # Convertir los tiempos a milisegundos (opcional)
        start_time_ms = time_to_milliseconds(hora_inicio)
        end_time_ms = time_to_milliseconds(hora_fin)
        st.session_state.times.append((start_time_ms, end_time_ms))

# Lógica de edición de filas
def handle_row_deletion():
    edited_rows = st.session_state[DATA_EDITOR][DATA_ROWS]
    rows_to_delete = []

    for idx, value in edited_rows.items():
        if value["x"] is True:
            rows_to_delete.append(idx)

    # Eliminar filas seleccionadas
    if rows_to_delete:
        st.session_state['data'] = st.session_state['data'].drop(rows_to_delete, axis=0).reset_index(drop=True)

# Mostrar el editor de datos
def display_data_editor():
    columns = st.session_state['data'].columns
    column_config = {column: st.column_config.Column(disabled=True) for column in columns}

    # Crear una copia del DataFrame con la columna 'x' para marcar filas a eliminar
    modified_df = st.session_state['data'].copy()
    modified_df["x"] = False  # Columna para eliminar
    modified_df = modified_df[["x"] + modified_df.columns[:-1].tolist()]

    st.data_editor(
        modified_df,
        key="data_editor",
        on_change=handle_row_deletion,
        hide_index=True,
        column_config=column_config,
        use_container_width=True,
    )

# Crear formulario para ingresar horas
def create_time_form():
    # Crear columnas para las entradas de hora
    placeholder_for_horaInicio, placeholder_for_horaFin = st.columns(2)

    with placeholder_for_horaInicio:
        horaInicio = st.text_input(HORA_INICIO_TEXT_INPUT, key=KEY_HORA_INICIO)

    with placeholder_for_horaFin:
        horaFin = st.text_input(HORA_FIN_TEXT_INPUT, key=KEY_HORA_FIN)

    return horaInicio, horaFin

    
def main():
    configure_page()    

    # Usar las constantes definidas en constants.py
    st.title(APP_TITLE)  # Usamos la constante APP_TITLE en lugar de _("AudioScribe")

    # Menú
    menu = [
        ##MENU_ONE_CONVERT_AUDIO,
        MENU_TWO_AUDIO_MANAGER,
        MENU_THREEE_TEXT_MANAGER
    ]
    opcion = st.sidebar.selectbox(MENU_ONE_CONVERT_AUDIO, menu)
    
    if opcion == MENU_ONE_CONVERT_AUDIO:
        st.subheader(CONVERT_MP4_TO_WAV_OPTION)
        archivo_video = st.file_uploader(SELECT_VIDEO, type=["mp4"]) 

        if st.button(PROCESS_BUTTON):
            if archivo_video is not None:
                if archivo_video.size > MAX_SIZE_FILE:
                    st.error(FILE_TOO_LARGE)
                else:
                    # Mostrar el spinner antes de procesar el video
                    with st.spinner(SPINNER_TEXT):
                        process_video(archivo_video)  # Llamada a la función para procesar el video

            else:
                st.warning(FILE_UPLOAD_NOT_SELECT)

    elif opcion == MENU_TWO_AUDIO_MANAGER:
        st.subheader(MENU_TWO_AUDIO_MANAGER)
        initialize_session_data()
        archivo_audio = st.file_uploader(SELECT_AUDIO, type=[WAV, MP3])
        horaInicio, horaFin = create_time_form()        
        
        # Formulario para agregar los datos
        dfForm = st.form(key='dfForm')

        st.markdown("<h3 style='text-align: center;'>Datos de Intervalos de Tiempo</h3>", unsafe_allow_html=True)        
        with dfForm:
            st.empty()  # Placeholder para las columnas de hora
            add_button = st.form_submit_button("Add", on_click=add_dfForm, disabled=not (horaInicio and horaFin))
        
        # Mostrar el editor de datos
        display_data_editor()

        # Agregar el botón de "Process" después de mostrar el DataFrame
        process_button = st.button("Procesar", on_click=add_interval_time, type=PRIMARY)
        if process_button:
            st.success('Procesado')
            
        st.markdown("<h3 style='text-align: center;'>Operaciones</h3>", unsafe_allow_html=True)  
        #st.markdown("<hr>", unsafe_allow_html=True)  # Línea horizontal para separar visualmente
        #st.subheader("Operaciones")
        
        if len(st.session_state.times) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                btn_segmentar_audio = st.button(SEGMENT_AUDIO_BUTTON, type=PRIMARY)
            with col2:
                btn_dividir_audio = st.button(SPLIT_AUDIO_BUTTON, type=PRIMARY)
            with col3:
                btn_generar_texto = st.button(GENERATE_TEXT_BUTTON, type=PRIMARY)
            with col4:
                btn_generar_documento = st.button(GENERATE_DOCUMENT_BUTTON, type=PRIMARY)
            
            if btn_segmentar_audio:
                with st.spinner(SPINNER_SEGMENT_AUDIO):
                    segmentar_audio(archivo_audio)                
                st.success(SPINNER_SEGMENT_AUDIO_SUCCESS)
            if btn_dividir_audio:
                 with st.spinner(SPINNER_DIVIDE_AUDIO):
                    dividir_audios()                    
                    st.success(SPINNER_DIVIDE_AUDIO_SUCCESS)
            if btn_generar_texto:
                with st.spinner(SPINNER_GENERATE_TEXT):
                    generar_textos()
                    st.success(SPINNER_GENERATE_TEXT_SUCCESS)
            if btn_generar_documento:
                with st.spinner(SPINNER_GENERATE_DOCUMENT):
                    generar_documento()
                    st.success(SPINNER_GENERATE_DOCUMENT_SUCCESS)

    elif opcion == MENU_THREEE_TEXT_MANAGER:
        st.subheader(MENU_THREEE_TEXT_MANAGER)
        mostrar_descargar_documento()

        
if __name__ == '__main__':
    main()