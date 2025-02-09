import os

# Configuración básica de Flask
DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_super_segura")

# Configuración del servidor
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True


# Configuración de OCR (Ruta de Tesseract en Windows)
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Otras configuraciones
UPLOAD_FOLDER = os.path.abspath("data/uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Configuración de la base de datos (Si en el futuro se usa SQL)
SQLALCHEMY_DATABASE_URI = "sqlite:///data/database.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
