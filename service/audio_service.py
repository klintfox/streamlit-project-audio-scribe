# Imports estándar de Python
import os
import tempfile
import subprocess

# Imports de bibliotecas de terceros
import logging
import streamlit as st
##from pydub import AudioSegment
import librosa
import soundfile as sf


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
        st.error("❌ Error, por favor carga un archivo de audio primero.")
        return

    ruta_audios_seg = os.path.join(BASE_PATH, "audios_seg")
    os.makedirs(ruta_audios_seg, exist_ok=True)

    # Determinar la extensión según el tipo de archivo cargado
    if audio_file.type == "audio/wav":
        extension = ".wav"
    elif audio_file.type == "audio/mpeg":
        extension = ".mp3"
    else:
        st.error("❌ Formato de audio no compatible. Por favor, sube un archivo .wav o .mp3.")
        return

    try:
        # Guardar el archivo cargado como temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_file.write(audio_file.getbuffer())
            temp_audio_path = temp_file.name

        # Cargar el audio como array NumPy
        audio, sample_rate = librosa.load(temp_audio_path, sr=None)

        # Verificar que existan tiempos definidos
        if "times" not in st.session_state or not st.session_state.times:
            st.error("❌ No se han definido los tiempos de segmentación.")
            return

        total_segmentos = len(st.session_state.times)
        segmentos_restantes = total_segmentos
        info_messages = []

        with st.status("✂️ Segmentando audio...", expanded=True) as status:
            contador_placeholder = st.empty()
            contador_placeholder.write(f"🧩 Segmentos restantes: {segmentos_restantes}")

            for idx, (start_time_ms, end_time_ms) in enumerate(st.session_state.times):
                if start_time_ms >= end_time_ms:
                    st.error(f"❌ El tiempo de inicio debe ser menor que el de fin para el segmento {idx + 1}.")
                    return

                # Convertir tiempos de milisegundos a muestras
                start_sample = int((start_time_ms / 1000.0) * sample_rate)
                end_sample = int((end_time_ms / 1000.0) * sample_rate)

                segment = audio[start_sample:end_sample]

                archivo_audio_output = f"segmento{idx + 1}.wav"
                output_path = os.path.join(ruta_audios_seg, archivo_audio_output)

                # Guardar el segmento como archivo .wav
                sf.write(output_path, segment, sample_rate)

                # Actualiza contador regresivo
                segmentos_restantes -= 1
                contador_placeholder.write(f"🧩 Segmentos restantes: {segmentos_restantes}")

            if info_messages:
                st.success("✅ Segmentación completada exitosamente:")
                st.markdown("\n".join(info_messages))

            status.update(label="✅ Segmentación finalizada", state="complete")        

    except Exception as e:
        if 'temp_audio_path' in locals():
            os.remove(temp_audio_path)
        st.error(f"❌ Error al procesar el archivo: {e}")
    finally:
        if 'temp_audio_path' in locals():
            os.remove(temp_audio_path)


def dividir_audios():
    ruta_audios_seg = os.path.join(BASE_PATH, "audios_seg")  # Carpeta de entrada
    ruta_audios_minuto = os.path.join(BASE_PATH, "audios_minuto")  # Carpeta de salida

    # Asegurarnos de que la carpeta de salida exista
    os.makedirs(ruta_audios_minuto, exist_ok=True)

    total_segmentos = 0
    total_files = 0  # Contador de archivos
    audio_files = [
        f for f in os.listdir(ruta_audios_seg)
        if f.startswith("segmento") and f.endswith(".wav")
    ]

    # Contamos cuántos segmentos se generarán en total
    for filename in audio_files:
        audio_path = os.path.join(ruta_audios_seg, filename)
        audio, sample_rate = librosa.load(audio_path, sr=None)
        total_duration = len(audio)
        
        # Aquí calculamos el SEGMENT_DURATION en muestras (1 minuto)
        SEGMENT_DURATION = 60 * sample_rate  # 1 minuto en muestras
        
        # Ahora calculamos cuántos segmentos se generarán
        num_segments = total_duration // SEGMENT_DURATION + (total_duration % SEGMENT_DURATION > 0)
        total_segmentos += num_segments
        total_files += 1  # Aumentamos el contador de archivos

    # Iniciamos la división de los audios
    with st.status("🔄 Dividiendo audios en segmentos de 1 minuto...", expanded=True) as status:
        contador_placeholder = st.empty()  # Este será el espacio donde mostraremos la actualización del contador

        segmentos_restantes = total_segmentos  # Iniciamos el contador de segmentos restantes

        for filename in audio_files:
            audio_path = os.path.join(ruta_audios_seg, filename)
            audio, sample_rate = librosa.load(audio_path, sr=None)
            total_duration = len(audio)
            
            # Calculamos el SEGMENT_DURATION en muestras (1 minuto)
            SEGMENT_DURATION = 60 * sample_rate  # 1 minuto en muestras
            
            num_segments = total_duration // SEGMENT_DURATION + (total_duration % SEGMENT_DURATION > 0)

            # Dividimos el archivo en segmentos
            for i in range(num_segments):
                start_sample = i * SEGMENT_DURATION
                end_sample = min((i + 1) * SEGMENT_DURATION, total_duration)
                segment = audio[start_sample:end_sample]

                audio_seg_file = f"{filename[:-4]}_audio{i + 1}.wav"
                output_path = os.path.join(ruta_audios_minuto, audio_seg_file)
                sf.write(output_path, segment, sample_rate)

                # Actualizamos el contador de segmentos restantes
                segmentos_restantes -= 1
                contador_placeholder.write(f"🧩 Audios Divididos restantes: {segmentos_restantes}")

        # Finalizamos la operación
        status.update(label="✅ División de audios completada", state="complete")