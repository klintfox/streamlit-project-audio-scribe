# Imports estándar de Python
import os

# Imports de bibliotecas de terceros
import streamlit as st
import speech_recognition as sr
from docx import Document

# Own Imports
from config import *

def generar_textos():

    ruta_audios_minuto = os.path.join(BASE_PATH,"audios_minuto")

    # Asegurarnos de que la carpeta de salida exista
    if not os.path.exists(os.path.join(BASE_PATH,"textos_minuto")):
        os.makedirs(os.path.join(BASE_PATH,"textos_minuto"))
    
    carpeta_textos_minuto = os.path.join(BASE_PATH,"textos_minuto")
    
    notification_messages = []
    error_messages = []
    try:
        # Crea un objeto Recognizer
        recognizer = sr.Recognizer()   

        # Obtener todos los archivos de audio en la carpeta audios_seg
        audio_files = [f for f in os.listdir(ruta_audios_minuto) if f.endswith('.wav')]            
        st.info(f"Número de Audios: {len(audio_files)}")

        # Asi ocurra un error el bucle seguirá con el siguiente audio
        for audio_file in audio_files:
            audio_minuto_file_path = os.path.join(ruta_audios_minuto, audio_file)                
            with sr.AudioFile(audio_minuto_file_path) as source:
                audio_data = recognizer.record(source)                    

            try:
                # Reconocimiento de voz con idioma español
                text = recognizer.recognize_google(audio_data, language=RECOGNITION_LANGUAGE)                

                # Guardar el texto en un archivo en la carpeta de transcripciones
                text_file_name = os.path.splitext(audio_file)[0] + ".txt"
                text_file_path = os.path.join(carpeta_textos_minuto, text_file_name)
                with open(text_file_path, "w", encoding="utf-8") as text_file:
                    text_file.write(text)

                st.info(f"El audio: {audio_file} ha sido procesado y se generó el texto en: {text_file_path}")
            except sr.UnknownValueError:
                notification_messages.append(f"No se pudo entender el audio '{audio_file}'.")                
            except sr.RequestError as e:                    
                error_messages.append(f"No se pudo solicitar resultados de Google Speech Recognition para '{audio_file}'; {e}")
            except FileNotFoundError as e:
                error_messages.append(f"Error al procesar el archivo '{audio_file}': {e}")                    

        # Mostrar los mensajes de notificación o error
        if notification_messages:
            for message in notification_messages:
                st.warning(message)
        
        if error_messages:
            for message in error_messages:
                st.error(message)

    except FileNotFoundError:                
        st.error("Errores: ",error_messages)
    except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")
    

def generar_documento():
    # Obtener la ruta de la carpeta desde el label

    carpeta_textos_minuto = os.path.join(BASE_PATH,"textos_minuto")    

    # Asegurarse de que la carpeta temp exista
    # if not os.path.exists(os.path.join(BASE_PATH,ruta_temp)):
    #    os.makedirs(os.path.join(BASE_PATH,ruta_temp))

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
                        #final_file.write(file.read() + "\n")  # Agregar un salto de línea entre transcripciones
                except Exception as e:
                    st.error(f"No se pudo leer el archivo '{text_file}': {e}")
                    continue  # Si hay un error al leer el archivo, seguir con el siguiente archivo

        # Confirmar que el documento se generó correctamente
        #st.success(f"Documento generado con éxito: {document_file_path}")
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
        st.subheader("Opciones de descarga")
        # Crear columnas para los botones de descarga        
        
        # Aquí podrías tener un botón de análisis o alguna otra funcionalidad        
        st.button("Analizar Texto")

    else:
        st.error("El archivo 'documentoGenerado.txt' no existe en la ruta especificada.")