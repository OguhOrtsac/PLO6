import cv2
import pytesseract
import re

def procesar_imagen_para_ocr(imagen_path):
    """
    Procesa una imagen para mejorar la precisión del OCR.
    """
    # Lee la imagen en color
    imagen = cv2.imread(imagen_path)

    # Convierte a escala de grises
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Aplica un filtro de color para manejar relleno
    _, imagen_binaria = cv2.threshold(imagen_gris, 150, 255, cv2.THRESH_BINARY_INV)

    # Aumenta el contraste utilizando ecualización del histograma
    imagen_binaria = cv2.equalizeHist(imagen_binaria)

    # Aplica un desenfoque para reducir ruido
    imagen_binaria = cv2.GaussianBlur(imagen_binaria, (3, 3), 0)

    # Escala la imagen para mejorar la detección
    #imagen_escalada = cv2.resize(imagen_binaria, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    return imagen_binaria

def procesar_sin_quitar_contornos(imagen_path):
    """
    Procesa la imagen sin eliminar los contornos ni aplicar umbral adaptativo.
    """
    imagen = cv2.imread(imagen_path, cv2.IMREAD_GRAYSCALE)
    _, imagen_binaria = cv2.threshold(imagen, 127, 255, cv2.THRESH_BINARY)
    return imagen_binaria

def detectar_color(imagen_path):
    """
    Detecta el color predominante de la carta para determinar su palo.
    """
    imagen = cv2.imread(imagen_path)
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Define rangos de colores para identificar colores predominantes
    colores = {
        "R": ((0, 50, 50), (10, 255, 255), (170, 50, 50), (180, 255, 255)),  # Rojo
        "B": ((100, 50, 50), (140, 255, 255)),  # Azul
        "G": ((40, 50, 50), (80, 255, 255)),  # Verde
        "N": ((0, 0, 0), (180, 255, 50)),  # Negro
    }

    max_color = ""
    max_count = 0

    for color, ranges in colores.items():
        if len(ranges) == 2:
            mask = cv2.inRange(hsv, ranges[0], ranges[1])
        else:
            mask1 = cv2.inRange(hsv, ranges[0], ranges[1])
            mask2 = cv2.inRange(hsv, ranges[2], ranges[3])
            mask = mask1 + mask2

        count = cv2.countNonZero(mask)
        if count > max_count:
            max_count = count
            max_color = color

    return max_color

def determinar_palo(color):
    """
    Determina el palo basado en el color detectado.
    """
    if color == "R":
        return "H"  # Corazones
    elif color == "B":
        return "D"  # Diamantes
    elif color == "G":
        return "C"  # Tréboles
    elif color == "N":
        return "S"  # Picas
    else:
        return "?"  # Indeterminado

def extraer_carta(imagen_path):
    """
    Extrae el nombre de la carta de una imagen específica.

    Args:
        imagen_path (str): Ruta de la imagen de la carta.

    Returns:
        str: Nombre de la carta detectada o 'No se detectó carta válida'.
    """
    # Procesa la imagen
    imagen_procesada = procesar_imagen_para_ocr(imagen_path)
    temp_path = "temp_processed_image.png"
    cv2.imwrite(temp_path, imagen_procesada)

    # Configuración de Tesseract
    config_tesseract = (
        "--psm 8 --oem 3 -c tessedit_char_whitelist=AJKQ2345678910 -c tessedit_char_blacklist=il"
    )

    # Realiza el OCR en la imagen procesada
    texto_extraido = pytesseract.image_to_string(temp_path, config=config_tesseract).strip()
    match = re.search(r'^(A|J|K|Q|10|[2-9])$', texto_extraido)

    if match:
        carta_detectada = match.group(0)
        color = detectar_color(imagen_path)
        palo = determinar_palo(color)
        return f"{carta_detectada}_{palo}"
    else:
        # Si no se detectó texto, utiliza el método alternativo
        imagen_procesada = procesar_sin_quitar_contornos(imagen_path)
        temp_path_alternativo = "temp_processed_image_alternative.png"
        cv2.imwrite(temp_path_alternativo, imagen_procesada)

        texto_extraido = pytesseract.image_to_string(temp_path_alternativo, config=config_tesseract).strip()
        match = re.search(r'^(A|J|K|Q|10|[2-9])$', texto_extraido, re.IGNORECASE)

        if match:
            carta_detectada = match.group(0).upper()
            color = detectar_color(imagen_path)
            palo = determinar_palo(color)
            return f"{carta_detectada}_{palo}"
        else:
            return "No se detectó carta válida"
