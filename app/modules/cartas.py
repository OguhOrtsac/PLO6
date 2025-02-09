from skimage.metrics import structural_similarity as ssim
import cv2
import os
import numpy as np
import uuid
from app.modules.ocr import extraer_carta



def recortar_carta(imagen, x, y, ancho, alto, escala=1):
    """
    Recorta una región específica de la imagen según las coordenadas dadas,
    aumenta la resolución y mejora la calidad.
    """
    carta = imagen[y:y + alto, x:x + ancho]

    # Aumentar resolución
    nueva_ancho = int(carta.shape[1] * escala)
    nueva_alto = int(carta.shape[0] * escala)
    carta = cv2.resize(carta, (nueva_ancho, nueva_alto), interpolation=cv2.INTER_CUBIC)
    carta = resaltar_bordes(carta)

    # Mejorar calidad
    carta = mejorar_calidad(carta)
    carta = resaltar_bordes(carta)
    # Ajustar brillo y contraste
    carta = ajustar_brillo_contraste(carta, alpha=1.5, beta=20)
   
    return carta

def mejorar_calidad(imagen):
    """
    Aplica técnicas de mejora de calidad a la imagen.
    """
    # Aplicar filtro bilateral para suavizar sin perder bordes
    imagen_suavizada = cv2.bilateralFilter(imagen, d=9, sigmaColor=75, sigmaSpace=75)

    # Incrementar nitidez con una máscara de bordes
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    imagen_nitida = cv2.filter2D(imagen_suavizada, -1, kernel)

    return imagen_nitida

def ajustar_brillo_contraste(imagen, alpha=1.5, beta=20):
    """
    Ajusta el brillo y contraste de la imagen.
    Args:
        alpha (float): Factor de contraste (>1 para aumentar).
        beta (int): Factor de brillo (+ para iluminar, - para oscurecer).
    """
    return cv2.convertScaleAbs(imagen, alpha=alpha, beta=beta)

def convertir_a_grises(imagen):
    """
    Convierte la imagen a escala de grises.
    """
    return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)


def resaltar_bordes(imagen):
    """
    Resalta los bordes de la imagen de forma fina, definiendo mejor los márgenes
    y rellenándolos suavemente con el color predominante de la imagen.

    Args:
        imagen: Imagen original en formato BGR.

    Returns:
        Imagen con bordes finos resaltados y definidos.
    """
    # Convertir a escala de grises para detectar bordes
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Aplicar detección de bordes (Canny) con umbrales ajustados para bordes finos
    bordes = cv2.Canny(gris, threshold1=75, threshold2=150)

    # Dilatar los bordes mínimamente para hacerlos visibles
    kernel = np.ones((2, 2), np.uint8)  # Kernel más pequeño para bordes finos
    bordes_dilatados = cv2.dilate(bordes, kernel, iterations=1)

    # Crear una máscara de bordes para combinar con la imagen original
    bordes_color = cv2.cvtColor(bordes_dilatados, cv2.COLOR_GRAY2BGR)

    # Obtener el color predominante de la imagen
    color_predominante = detectar_color_predominante(imagen)

    # Aplicar un color más sutil en los bordes
    bordes_color[:, :, 0] = bordes_color[:, :, 0] * (color_predominante[0] / 255)
    bordes_color[:, :, 1] = bordes_color[:, :, 1] * (color_predominante[1] / 255)
    bordes_color[:, :, 2] = bordes_color[:, :, 2] * (color_predominante[2] / 255)

    # Combinar bordes suavemente con la imagen original
    imagen_resaltada = cv2.addWeighted(imagen, 0.95, bordes_color, 0.05, 0)

    return imagen_resaltada

def detectar_color_predominante(imagen):
    """
    Detecta el color predominante en la imagen y devuelve uno de los 4 posibles:
    rojo, verde, azul o negro.

    Args:
        imagen: Imagen en formato BGR.

    Returns:
        Tuple[int, int, int]: Color en formato BGR.
    """
    # Convertir la imagen a formato HSV para analizar los colores
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Definir rangos de colores en HSV
    colores = {
        "rojo": ((0, 50, 50), (10, 255, 255)),
        "verde": ((40, 50, 50), (80, 255, 255)),
        "azul": ((100, 50, 50), (140, 255, 255)),
        "negro": ((0, 0, 0), (180, 255, 50))
    }

    # Contadores de píxeles para cada color
    contador_colores = {"rojo": 0, "verde": 0, "azul": 0, "negro": 0}

    # Analizar la cantidad de píxeles en cada rango
    for color, (lower, upper) in colores.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        contador_colores[color] = cv2.countNonZero(mask)

    # Determinar el color predominante
    color_predominante = max(contador_colores, key=contador_colores.get)

    # Mapeo de colores a formato BGR
    mapeo_colores = {
        "rojo": (0, 0, 255),
        "verde": (0, 255, 0),
        "azul": (255, 0, 0),
        "negro": (0, 0, 0)
    }

    return mapeo_colores[color_predominante]

def procesar_cartas(imagen_principal, areas, carpeta_salida, tipo):
    """
    Procesa las cartas en las áreas especificadas y realiza el OCR para convertir imágenes en texto.

    Args:
        imagen_principal (numpy.ndarray): Imagen principal donde están las cartas.
        areas (list): Lista de coordenadas [(x, y, ancho, alto), ...].
        carpeta_salida (str): Ruta de la carpeta donde se guardarán las cartas recortadas.
        tipo (str): Identificador del tipo de área ("board" o "jugador").

    Returns:
        list: Lista de cartas identificadas.
    """
    cartas_detectadas = []  # ✅ Lista para acumular todas las cartas

    for i, (x, y, ancho, alto) in enumerate(areas):
        carta_recortada = recortar_carta(imagen_principal, x, y, ancho, alto)
        ruta_carta = os.path.join(carpeta_salida, f"{tipo}_carta_{i+1}.png")       
        cv2.imwrite(ruta_carta, carta_recortada)
        
        # Llama a la función OCR y obtiene el resultado para esta carta
        resultado = extraer_carta(ruta_carta)
        print(f"🔍 Carta detectada en {tipo}: {resultado}")

        if resultado:
            cartas_detectadas.append(resultado+".png")  # ✅ Acumulamos la carta detectada

    return cartas_detectadas  # ✅ Devolvemos TODAS las cartas encontradas



#FUNCIONES PARA PROCESAR CARTAS SELECCIONADAS CON LAS IMAGENES


def normalizar_cartas(cartas):
    """
    Convierte las cartas al formato requerido por la biblioteca 'treys'.
    Ejemplo: 'AS' -> 'As', '6H' -> '6h', '10H' -> 'Th'
    """
    palos = {'S': 's', 'H': 'h', 'C': 'c', 'D': 'd'}
    normalizadas = []

    for carta in cartas:
        if carta.startswith('10'):  # Convertir '10' a 'T'
            carta = 'T' + carta[2:]
        if carta[-1] in palos:  # Si el último carácter es un palo en mayúsculas
            normalizadas.append(carta[:-1] + palos[carta[-1]])
        elif carta[-1] in ['s', 'h', 'c', 'd']:  # Si ya está en minúscula
            normalizadas.append(carta)
        else:
            raise ValueError(f"Error al procesar la carta: {carta}. Palo no reconocido.")

    return normalizadas

def limpiar_cartas(cartas):
    """
    Limpia el formato de las cartas eliminando extensiones y caracteres innecesarios.
    """
    return [carta.replace('.png', '').replace('_', '') for carta in cartas]
