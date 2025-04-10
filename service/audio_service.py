# Imports estándar de Python
import os
import tempfile
import subprocess

# Imports de bibliotecas de terceros
import logging
from pydub import AudioSegment
import streamlit as st

# Own Imports
from config import *

def process_video(video_file):

    # Ruta absoluta a la carpeta temp en la raíz del proyecto
    ruta_temp = os.path.join(BASE_PATH, "temp")

    # Crear la carpeta 'temp' si no existe
    if not os.path.exists(ruta_temp):
        os.makedirs(ruta_temp)

    # Guardamos el archivo temporalmente en el disco
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_file.getbuffer())  # Guardamos el archivo cargado
        temp_video_path = temp_file.name  # Ruta del archivo temporal
        
    nombre = video_file.name.rsplit('.', 1)[0]
    archivo_video_output = os.path.join(ruta_temp, nombre + ".wav")  # Guardamos en la carpeta 'temp'

    try:
        # Ejecutar el comando ffmpeg
        #-y: Sobrescribe los archivos de salida sin pedir confirmación.
        command = ["ffmpeg", "-y", "-i", temp_video_path, archivo_video_output]
        #subprocess.run(command, check=True)
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        st.success(f"Archivo procesado exitosamente! guardado en: {archivo_video_output}")
        st.write(result.stdout)
    except subprocess.CalledProcessError as e:
        # Captura los errores de ffmpeg y muestra un mensaje detallado
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
        st.error(f"Detalles del error: {e.stderr}")  # Muestra el error específico de ffmpeg
    except Exception as e:
        st.error(f"Un error inesperado ocurrió: {e}")
    finally:
        # Limpiar el archivo temporal (si ya no lo necesitas)
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

def segmentar_audio(audio_file):
    if not audio_file:
        st.error("Error, por favor carga un archivo de audio primero.")
        return
    
    # Asegurarnos de que la carpeta de salida exista
    if not os.path.exists(os.path.join(BASE_PATH,"audios_seg")):
        os.makedirs(os.path.join(BASE_PATH,"audios_seg"))
    
    try:            
        # Guardar el archivo cargado como un archivo temporal para poder procesarlo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_file.getbuffer())  # Guardamos el archivo cargado en el archivo temporal
            temp_audio_path = temp_file.name  # Ruta del archivo temporal
        
        # Usamos pydub para cargar el archivo de audio
        audio = AudioSegment.from_wav(temp_audio_path)

        # Procesar cada segmento de la colección de tiempos
        for idx, (start_time_ms, end_time_ms) in enumerate(st.session_state.times):
            if start_time_ms >= end_time_ms:
                return st.error(f"El tiempo de inicio debe ser menor que el de fin para el segmento {idx + 1}.")
            
            # Cortar el segmento del audio según los tiempos proporcionados
            segment = audio[start_time_ms:end_time_ms]  # Cortamos el segmento de audio en milisegundos

            # Definir el nombre del archivo de salida
            archivo_audio_output = f"audios_seg/segmento{idx + 1}.wav"
            
            # Construir la ruta completa usando BASE_PATH
            output_path = os.path.join(BASE_PATH, archivo_audio_output)

            # Guardar el segmento como un nuevo archivo
            segment.export(output_path, format="wav")

            st.info(f"Segmento {idx + 1} guardado en: {archivo_audio_output}")                    

    except subprocess.CalledProcessError as e:
        # En caso de error, aseguramos la eliminación del archivo temporal:
        if 'temp_audio_path' in locals():
            os.remove(temp_audio_path)
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
    finally:
        # Eliminar el archivo temporal después de procesarlo
        if 'temp_audio_path' in locals():
            os.remove(temp_audio_path)


def dividir_audios():
    ruta_audios_seg = os.path.join(BASE_PATH,"audios_seg")  # Carpeta de entrada donde están los archivos segmentados
    
    # Asegurarnos de que la carpeta de salida exista
    output_dir = os.path.join(BASE_PATH, "audios_minuto")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ruta_audios_minuto = os.path.join(BASE_PATH,"audios_minuto")  # Carpeta donde se guardarán los segmentos de 1 minuto
    
    try:                       
        # Iterar sobre los archivos en la carpeta 'audios_seg'
        for filename in os.listdir(ruta_audios_seg):
            if filename.startswith("segmento") and filename.endswith(".wav"):
                # Cargar el archivo de audio
                audio_path = os.path.join(ruta_audios_seg, filename)
                audio = AudioSegment.from_wav(audio_path)

                total_duration = len(audio)  # Duración total del archivo en milisegundos
                
                # Calcular el número de segmentos de 1 minuto
                num_segments = total_duration // SEGMENT_DURATION + (total_duration % SEGMENT_DURATION > 0)

                # Dividir el archivo de audio en segmentos de 1 minuto
                for i in range(num_segments):
                    start_time = i * SEGMENT_DURATION
                    end_time = min((i + 1) * SEGMENT_DURATION, total_duration)
                    
                    # Extraer el segmento
                    segment = audio[start_time:end_time]
                    
                    # Definir el nombre del archivo de salida
                    audio_seg_file = f"{filename[:-4]}_audio{i + 1}.wav"

                    # Guardar el segmento en la carpeta 'audios_minuto'
                    output_path = os.path.join(ruta_audios_minuto, audio_seg_file)
                    segment.export(output_path, format="wav")

                    # Mostrar mensaje de éxito para cada segmento
                    st.info(f"Segmento {i + 1} guardado como: {audio_seg_file}")
    
    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        st.error(f"Error: {e}")
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado: {e}")
        st.error(f"Ocurrió un error inesperado: {e}")        

