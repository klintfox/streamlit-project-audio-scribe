# Imports estándar de Python
import os

# Imports de bibliotecas de terceros
import streamlit as st
import speech_recognition as sr
from docx import Document
import shutil

# Own Imports
from config import *

def generar_textos():
    ruta_audios_minuto = os.path.join(BASE_PATH, "audios_minuto")

    # Asegurarnos de que la carpeta de salida exista
    carpeta_textos_minuto = os.path.join(BASE_PATH, "textos_minuto")
    os.makedirs(carpeta_textos_minuto, exist_ok=True)

    notification_messages = []
    error_messages = []
    info_messages = []

    try:
        recognizer = sr.Recognizer()
        audio_files = [f for f in os.listdir(ruta_audios_minuto) if f.endswith('.wav')]
        total_audios = len(audio_files)

        with st.status(SPINNER_GENERATE_TEXT, expanded=True) as status:
            # Placeholder dinámico para mostrar el número de audios pendientes
            contador_placeholder = st.empty()
            contador_placeholder.write(f"🎧 Textos pendientes: {total_audios}")

            for index, audio_file in enumerate(audio_files, start=1):
                audio_minuto_file_path = os.path.join(ruta_audios_minuto, audio_file)

                try:
                    with sr.AudioFile(audio_minuto_file_path) as source:
                        audio_data = recognizer.record(source)

                    text = recognizer.recognize_google(audio_data, language=RECOGNITION_LANGUAGE)

                    # Guardar texto
                    text_file_name = os.path.splitext(audio_file)[0] + ".txt"
                    text_file_path = os.path.join(carpeta_textos_minuto, text_file_name)

                    with open(text_file_path, "w", encoding="utf-8") as text_file:
                        text_file.write(text)

                except sr.UnknownValueError:
                    notification_messages.append(f"No se pudo entender el audio '{audio_file}'.")
                except sr.RequestError as e:
                    error_messages.append(f"No se pudo solicitar resultados de Google Speech Recognition para '{audio_file}'; {e}")
                except FileNotFoundError as e:
                    error_messages.append(f"Error al procesar el archivo '{audio_file}': {e}")

                # Actualizar contador de audios pendientes
                audios_restantes = total_audios - index
                contador_placeholder.write(f"🎧 Textos pendientes: {audios_restantes}")

            # Mostrar resultados
            if info_messages:
                st.success("✅ Audios procesados exitosamente:")
                st.markdown("\n".join(info_messages))

            if notification_messages:
                st.warning("⚠️ Algunos audios no pudieron ser entendidos:")
                st.markdown("\n".join(notification_messages))

            if error_messages:
                st.error("❌ Errores encontrados durante el procesamiento:")
                st.markdown("\n".join(error_messages))

            status.update(label="✅ Generacion de Textos completado", state="complete")

    except FileNotFoundError:
        st.error("❌ Carpeta de audios no encontrada.")
    except Exception as e:
        st.error(f"🚨 Error inesperado: {e}")
    

def generar_documento():
    # Obtener la ruta de la carpeta desde el label

    carpeta_textos_minuto = os.path.join(BASE_PATH,"textos_minuto")

    if not os.path.exists(os.path.join(BASE_PATH,"temp")):
        os.makedirs(os.path.join(BASE_PATH,"temp"))
    
    ruta_temp = os.path.join(BASE_PATH,"temp")    

    # Ruta del archivo final donde se guardarán todas las transcripciones
    document_file_path = os.path.join(ruta_temp, "documentoGenerado.txt")
    
    try:
        # Obtener todos los archivos de texto en la carpeta de transcripciones
        text_files = [f for f in os.listdir(carpeta_textos_minuto) if f.endswith('.txt')]

        if not text_files:
            st.warning("No se encontraron archivos de transcripción para generar el documento.")
            return  # Salir si no hay archivos para procesar

        # Abrir el archivo final en modo de escritura
        with open(document_file_path, "w", encoding="utf-8") as final_file:
            for text_file in text_files:
                text_file_path = os.path.join(carpeta_textos_minuto, text_file)
                try:
                    with open(text_file_path, "r", encoding="utf-8") as file:
                        # Escribir el contenido de cada archivo de texto en el archivo final
                        contenido = file.read()
                        final_file.write(contenido + "\n\n")                        

                except Exception as e:
                    st.error(f"No se pudo leer el archivo '{text_file}': {e}")
                    continue  # Si hay un error al leer el archivo, seguir con el siguiente archivo            
        
        # Después de generar el documento, eliminar los archivos en las carpetas
        carpetas_a_limpiar = [
            os.path.join(BASE_PATH, "audios_minuto"),
            os.path.join(BASE_PATH, "audios_seg"),
            os.path.join(BASE_PATH, "textos_minuto")
        ]
        
        for carpeta in carpetas_a_limpiar:
            if os.path.exists(carpeta):
                for filename in os.listdir(carpeta):
                    file_path = os.path.join(carpeta, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)  # Elimina el archivo
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)  # Elimina directorios (si hay alguno)
                    except Exception as e:
                        st.error(f"No se pudo eliminar el archivo o directorio '{file_path}': {e}")
        
        st.success(SPINNER_GENERATE_DOCUMENT_SUCCESS)

    except Exception as e:
        # Manejo general de excepciones
        st.error(f"Ocurrió un error inesperado al generar el documento: {e}")

def mostrar_descargar_documento():
    # Ruta del archivo generado
    archivo_path = os.path.join(BASE_PATH, "temp", "documentoGenerado.txt")
    
    # Verificar si el archivo existe
    if os.path.exists(archivo_path):
        # Leer el contenido del archivo
        with open(archivo_path, 'r', encoding='utf-8') as file:
            contenido = file.read()

        # Dividir el contenido en páginas (por ejemplo, 1000 caracteres por página)
        paginas = [contenido[i:i+5000] for i in range(0, len(contenido), 5000)]

        # Inicializar la página actual en session_state si no está presente
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 0
            
        # Asegurarse de que el índice de la página esté dentro del rango de la lista
        st.session_state.pagina_actual = max(0, min(st.session_state.pagina_actual, len(paginas) - 1))
        
        # Crear el documento Word (.docx) a partir del contenido completo
        docx_path = os.path.join(BASE_PATH, "temp", "documentoGenerado.docx")
        doc = Document()
        doc.add_paragraph(contenido)
        doc.save(docx_path)
        
        # Botones Descarga
        col1, col2,col3,col4 = st.columns([1,1,3,3])
        with col1:
            with open(archivo_path, "rb") as file:
                st.download_button(
                    label="Descargar documento",
                    data=file,
                    file_name="documentoGenerado.txt",
                    mime="text/plain"
                )
        with col2:
            with open(docx_path, "rb") as file:
                st.download_button(
                    label="Descargar documento en Word",
                    data=file,
                    file_name="documentoGenerado.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
        # Mostrar la página actual usando st.text_area        
        st.text_area("Contenido del documento generado", paginas[st.session_state.pagina_actual], height=400)

        # Navegación entre páginas
        col1, col2, col3, col4 = st.columns([4,1,4,1])  # Crear las columnas para los botones de navegación
        with col2:
            if st.button("Anterior", disabled=st.session_state.pagina_actual == 0):
                st.session_state.pagina_actual -= 1

        with col3:
            if st.button("Siguiente", disabled=st.session_state.pagina_actual == len(paginas) - 1):
                st.session_state.pagina_actual += 1

        # Sección separada para los botones de descarga
        st.markdown("<hr>", unsafe_allow_html=True)  # Línea horizontal para separar visualmente
        st.subheader("Próximamente...")        
        
        # Aquí podrías tener un botón de análisis o alguna otra funcionalidad        
        st.button("Analizar Texto")

    else:
        st.error("El archivo 'documentoGenerado.txt' no existe en la ruta especificada.")