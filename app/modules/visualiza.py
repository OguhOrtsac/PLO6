import cv2  # Para procesamiento de imágenes
import os  # Para manejo de rutas

def visualizar_areas(ruta_imagen, *listas_areas, ruta_salida):
    """
    Dibuja rectángulos en las áreas especificadas de la imagen y guarda una nueva imagen con las áreas resaltadas.

    Args:
        ruta_imagen (str): Ruta de la imagen a procesar.
        *listas_areas (list): Varias listas de áreas en formato [(x, y, ancho, alto), ...].
        ruta_salida (str): Ruta donde se guardará la imagen resultante.
    """
    try:
        # Cargar la imagen desde la ruta proporcionada
        imagen = cv2.imread(ruta_imagen)
        if imagen is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen en {ruta_imagen}. Verifica la ruta.")

        # Contador para identificar cada área
        contador = 1

        # Recorrer todas las listas de áreas
        for lista_areas in listas_areas:
            for (x, y, ancho, alto) in lista_areas:
                inicio = (x, y)  # Esquina superior izquierda del rectángulo
                fin = (x + ancho, y + alto)  # Esquina inferior derecha del rectángulo
                color = (0, 255, 0)  # Color verde en formato BGR
                grosor = 1  # Grosor de la línea del rectángulo

                # Dibujar rectángulo en la imagen
                cv2.rectangle(imagen, inicio, fin, color, grosor)
                # Añadir un texto identificador encima del área
              #  cv2.putText(imagen, f"Area {contador}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
               # contador += 1

        # Guardar la imagen con los rectángulos resaltados
        cv2.imwrite(ruta_salida, imagen)
       # print(f"Imagen con áreas resaltadas guardada en {ruta_salida}")

    except Exception as e:
        print(f"Error al visualizar áreas: {e}")
        raise
