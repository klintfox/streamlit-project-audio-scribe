# constants.py

# Título y menú
APP_TITLE = "AudioScribe"
MENU_ONE_CONVERT_AUDIO = "Convertir archivo MP4 a WAV"
MENU_TWO_AUDIO_MANAGER = "Gestionar Audio"
MENU_THREEE_TEXT_MANAGER = "Generar Texto"

# DataFrame
#DF_TIMES = "data"
DATA_EDITOR = "data_editor"
DATA_ROWS = "edited_rows"
HORA_INICIO_TEXT_INPUT= "Ingrese la hora de inicio (0h 0m 0s)"
HORA_FIN_TEXT_INPUT = "Ingrese la hora de fin (0h 1m 0s)"

# Sección "Convertir archivo MP4 a WAV"
CONVERT_MP4_TO_WAV_OPTION = "Convertir archivo MP4 a WAV"
SELECT_VIDEO = "Seleccionar Video"
PROCESS_BUTTON = "Procesar"
FILE_TOO_LARGE = "El archivo es demasiado grande. El tamaño máximo permitido es de 1000 MB."
FILE_DETAILS = "Detalles del archivo"
FILE_NAME = "nombre_archivo"
FILE_TYPE = "tipo_archivo"
FILE_SIZE = "tamaño_archivo"

# Sección "Gestionar Audio"
SELECT_AUDIO = "Seleccionar Audio"
SEGMENT_AUDIO_BUTTON = "Segmentar Audio"
SPLIT_AUDIO_BUTTON = "Dividir Audios"
GENERATE_TEXT_BUTTON = "Generar Textos"
GENERATE_DOCUMENT_BUTTON = "Generar Documento"

# Sección "Generar Texto"
#GENERATE_TEXT_OPTION = "Generar Texto"

# Form
HORARIO_INICIO = "horaInicio"
HORARIO_FIN ="horaFin"
KEY_HORA_INICIO ="khinicio"
KEY_HORA_FIN = "khfin"

# Buttons
PRIMARY = "primary"
SECONDARY = "secondary"

# Message Errors:
VALID_TIME_ERROR = "El formato de tiempo debe ser 'HH:MM:SS'."

# Confirm Messages
INTERVALO_AGREGADO = "Intervalo Agreado"

# Spinner 
SPINNER_TEXT = "Procesando el archivo... Esto puede tardar algunos segundos"

SPINNER_SEGMENT_AUDIO = "Segmentando audio(s)... Esto puede tardar algunos segundos." 
SPINNER_SEGMENT_AUDIO_SUCCESS = "Éxito!, Audios Segmentados" 

SPINNER_DIVIDE_AUDIO = "Dividiendo los audios en segmentos de 1 minuto... Esto puede tardar algunos segundos."
SPINNER_DIVIDE_AUDIO_SUCCESS = "¡Éxito! Todos los audios han sido divididos."

SPINNER_GENERATE_TEXT = "Generando textos por audio... Esto puede tardar algunos segundos."
SPINNER_GENERATE_TEXT_SUCCESS = "Éxito, Textos generados!"

SPINNER_GENERATE_DOCUMENT = "Generando textos por audio... Esto puede tardar algunos segundos."
SPINNER_GENERATE_DOCUMENT_SUCCESS = "Éxito, Documento Generado"


# File Upload Messages
FILE_UPLOAD_NOT_SELECT = "Atención, seleccione un archivo primero!"

# Tipo de Archivos
WAV = "wav"
MP3 = "mp3"
SUFFIX_MP4 = ".mp4"



# Tiempop
HH = "h"
MM = "m"
SS = "s"
