import os
import time  # Importar módulo para pausas
import win32gui
import win32process
import win32con
import ctypes
from PIL import ImageGrab

# Configuración de dimensiones esperadas
ANCHO_VENTANA = 440
ALTO_VENTANA = 823

# Constante para calcular márgenes
DWMWA_EXTENDED_FRAME_BOUNDS = 9


def validar_hwnd(hwnd):
    return hwnd and win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)

def obtener_bordes(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    extended_frame_bounds = ctypes.wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        ctypes.wintypes.HWND(hwnd),
        ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(extended_frame_bounds),
        ctypes.sizeof(extended_frame_bounds)
    )
    x = rect[0] + (extended_frame_bounds.left - rect[0])
    y = rect[1] + (extended_frame_bounds.top - rect[1])
    x1 = rect[2] - (rect[2] - extended_frame_bounds.right)
    y1 = rect[3] - (rect[3] - extended_frame_bounds.bottom)
    return x, y, x1, y1

def traer_ventana_al_frente(hwnd):
    if not validar_hwnd(hwnd):
        raise ValueError("El HWND no es válido o la ventana no está visible.")
    try:
        tid_foreground = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
        tid_target = win32process.GetWindowThreadProcessId(hwnd)[0]
        ctypes.windll.user32.AttachThreadInput(tid_foreground, tid_target, True)
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        ctypes.windll.user32.AttachThreadInput(tid_foreground, tid_target, False)
        time.sleep(0.5)
    except Exception as e:
        raise RuntimeError(f"No se pudo traer la ventana al frente: {e}")
    
    

def obtener_pdis_pppoker():
    """
    Obtiene los PDI de las ventanas activas con el título que contiene "- PPPoker".

    Returns:
        list: Lista de PDI detectados en las ventanas.
    """
    pdis = []
    
    def enum_ventanas(hwnd, _):
        titulo = win32gui.GetWindowText(hwnd)
        if "- PPPoker" in titulo:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pdis.append(str(pid))  # Solo guardar el número del PDI (PID)
    
    win32gui.EnumWindows(enum_ventanas, None)
    
    return sorted(pdis)

def listar_ventanas_pppoker():
    ventanas = []
    def enum_ventanas(hwnd, _):
        titulo = win32gui.GetWindowText(hwnd)
        if "- PPPoker" in titulo:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            ventanas.append({"pid": pid, "title": titulo, "hwnd": hwnd})
    win32gui.EnumWindows(enum_ventanas, None)
    return sorted(ventanas, key=lambda x: x['pid'])



def capturar_ventana(hwnd, ruta_salida):
    if not validar_hwnd(hwnd):
        raise ValueError("El HWND no es válido o la ventana no está visible.")
    x, y, x1, y1 = obtener_bordes(hwnd)
    ancho = x1 - x
    alto = y1 - y
    print(f"Coordenadas ajustadas: (x: {x}, y: {y}, ancho: {ancho}, alto: {alto})")
    if ancho != ANCHO_VENTANA or alto != ALTO_VENTANA:
        print(f"Advertencia: Dimensiones inesperadas ({ancho}x{alto}). Se capturará con estas dimensiones.")
    captura = ImageGrab.grab(bbox=(x, y, x1, y1))
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    captura.save(ruta_salida)
    print(f"Captura guardada en: {ruta_salida}")
    return ancho, alto, ruta_salida

def capturar_pppoker(pdi_seleccionado):
    """
    Captura la ventana de PPPoker seleccionada por su PDI.

    Args:
        pdi_seleccionado (str): Nombre del PDI seleccionado.

    Returns:
        tuple: Dimensiones de la captura (ancho, alto)
    """
    ventanas = listar_ventanas_pppoker()
    
    hwnd_seleccionado = None
    for ventana in ventanas:
        if str(ventana['pid']) == pdi_seleccionado:
            hwnd_seleccionado = ventana['hwnd']
            break
    
    if hwnd_seleccionado is None:
        print(f"No se encontró la ventana con PDI: {pdi_seleccionado}")
        return None, None
    
    ruta_salida = os.path.abspath(os.path.join("app", "static", "images", "capturas_pantalla", "Captura.png"))
    
    try:
        traer_ventana_al_frente(hwnd_seleccionado)
        return capturar_ventana(hwnd_seleccionado, ruta_salida)
    except ValueError as ve:
        print(f"Error: {ve}")
    except RuntimeError as re:
        print(f"Error: {re}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    return None, None


