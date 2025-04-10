import gettext
import os

# Configurar el directorio de locales
locales_path = os.path.join(os.path.dirname(__file__), "../locales")

# Función para cargar el idioma deseado
def set_language(language_code='es_ES'):
    try:
        # Intentar cargar la traducción
        translation = gettext.translation('messages', locales_path, languages=[language_code])
        # Forzar que la codificación sea utf-8 en la instalación
        translation.install(unicode=True)  # Asegura que las traducciones se manejen en unicode
        print(f"Traducción cargada para el idioma: {language_code}")
        return translation.gettext
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de traducción para el idioma '{language_code}' en la ruta {locales_path}")
        return None  # O manejar el error de alguna manera
    except UnicodeDecodeError as e:
        print(f"Error de codificación: {str(e)}")
        return None  # Manejar el error de codificación de manera adecuada

# Llamada para cargar las traducciones (por defecto español)
_ = set_language()  # Carga los mensajes en español por defecto

# Si deseas cambiar el idioma, por ejemplo, a inglés
# _ = set_language('en_US')
