from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room

from app.modules.captura import obtener_pdis_pppoker, capturar_pppoker
import cv2  # Para procesamiento de imágenes
import os  # Para manejo de rutas
from app.modules.visualiza import visualizar_areas
from app.modules.area_cartas import  obtener_area_boards, obtener_area_jugador
from app.modules.cartas import procesar_cartas, normalizar_cartas, limpiar_cartas
from app.modules.deck import Deck
from app.modules.game_logic import simulate_rounds
from app.modules.documento import generar_excel, generar_pdf
import sys 

# Rutas del proyecto
#ruta_captura_pantalla = os.path.abspath(os.path.join("app", "static", "images", "capturas_pantalla", "capt7.png"))
ruta_board = os.path.abspath(os.path.join("app", "static", "images", "preprocesadas", "board"))
ruta_jugador = os.path.abspath(os.path.join("app", "static", "images", "preprocesadas", "jugador"))
RUTA_SALIDA = os.path.abspath(os.path.join("app", "static", "images", "preprocesadas"))

# Crear la carpeta de salida si no existe
os.makedirs(RUTA_SALIDA, exist_ok=True)

def cargar_imagen(ruta_imagen):
    """Carga la imagen principal desde la ruta especificada."""
    imagen = cv2.imread(ruta_imagen)
    if imagen is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen en {ruta_imagen}. Verifica la ruta.")
    return imagen


# Crear la aplicación Flask y configurar la carpeta de plantillas
app = Flask(__name__, template_folder="../app/templates")
socketio = SocketIO(app)

# Cuando un cliente se conecta, unirse a la sala "mesa_25"    
    
@socketio.on('connect')
def handle_connect():
    # Unir al cliente a la sala "mesa_25"
    join_room("mesa_25")
    print(f"SID del cliente: {request.sid}")
    
    # Verificar si el cliente está en la sala
    participants = list(socketio.server.manager.get_participants(namespace='/', room="mesa_25"))
    print(f"Participantes en la sala 'mesa_25': {participants}")
    
    # Confirmar que el cliente está listo
    print("Unido a la mesa 25")



# Detectar si el programa está empaquetado como .exe
if getattr(sys, 'frozen', False):
    base_path = os.path.join(sys._MEIPASS, "config")  # Carpeta temporal donde PyInstaller extrae archivos
else:
    base_path = os.path.abspath("./config")  # Ruta normal en desarrollo

# Ruta completa del archivo de configuración
config_path = os.path.join(base_path, "settings.py")

# Verificar si el archivo existe antes de cargarlo
if os.path.exists(config_path):
    app.config.from_pyfile(config_path)
else:
    raise FileNotFoundError(f"No se encontró settings.py en {config_path}")

def obtener_lista_pdis():
    """
    Obtiene la lista de PDI de las ventanas activas.
    Returns:
        list: Lista de números de PDI.
    """
    ventanas = obtener_pdis_pppoker()
    pdis = [ventana for ventana in ventanas]  # Solo los PDI (PID)
    print("Lista de PDI detectados:", pdis)  # Imprimir en consola para depuración
    return pdis

@app.route('/')
def home():
    pdis = obtener_lista_pdis()
    # Generar la baraja
    deck = Deck()  

    return render_template(
        "index.html",
        pdis=pdis,
        cards=deck.cards  # Pasar la lista de cartas al HTML
    )

@app.route('/actualizar_pdis', methods=['GET'])
def actualizar_pdis():
    pdis = obtener_lista_pdis()
    return jsonify({"success": True, "pdis": pdis})


# Ruta para capturar imagen (modificada para usar WebSockets)
@socketio.on('capturar')
def capturar_socket(data):
    """
    Captura las cartas y actualiza a todos los usuarios en la mesa.
    """
    pdi_seleccionado = data.get("pdi")
    num_CartasBoard = int(data.get("board", 0))  # Convertir a número, por defecto 0 si no existe
    
    if not pdi_seleccionado:
        return jsonify({"success": False, "error": "No se proporcionó un PDI válido"})
    
    # Lógica de captura
    ancho, alto, ruta_captura_pantalla = capturar_pppoker(pdi_seleccionado)
    try:
        imagen_principal = cargar_imagen(ruta_captura_pantalla)
        area_jugador = obtener_area_jugador(ancho, alto)
        ruta_visualizacion = os.path.join("app", "static", "images", "visualizacion_areas.png")
        resultados_cartas = []
        resultados_cartas_jug = []

        if num_CartasBoard != 0:
            area_boards = obtener_area_boards(ancho, alto, num_CartasBoard)
            resultados_cartas = procesar_cartas(imagen_principal, area_boards, ruta_board, tipo="board")
            visualizar_areas(ruta_captura_pantalla, area_jugador, area_boards, ruta_salida=ruta_visualizacion)
        
        resultados_cartas_jug = procesar_cartas(imagen_principal, area_jugador, ruta_jugador, tipo="jugador")

        # Emitir los resultados a todos los usuarios en la mesa 25
        print("Emitiendo actualización de captura...")
        # Emitir los resultados a todos los usuarios en la mesa 25
        socketio.emit('actualizacion_captura', {
            "success": True,
            "pdi": pdi_seleccionado,
            "cartas_board": resultados_cartas,
            "cartas_jugador": resultados_cartas_jug,
            "num_CartasBoard": num_CartasBoard
        }, room="mesa_25")  # Usar el nombre de la sala "mesa_25"


        
        return jsonify({
            "success": True,
            "mensaje": f"Captura realizada para PDI {pdi_seleccionado}",
            "cartas_board": resultados_cartas,
            "cartas_jugador": resultados_cartas_jug,
            "num_CartasBoard": num_CartasBoard
        })

    except Exception as e:
        print(f"Error en el procesamiento: {e}")
        return jsonify({"success": False, "error": f"No se pudo procesar la captura. Detalles: {str(e)}"})



# AQUI VA LO NUEVO DE SIMULACIONES Y CARTAS

# Ruta para la simulación de manos (modificada para usar WebSockets)
@socketio.on('simulate_with_boards')
def simulate_with_boards_socket(data):
    """
    Procesa la simulación de rondas utilizando los boards y manos de jugadores/rivales.
    Emitimos los resultados a todos los usuarios en la mesa.
    """
    try:
        if not os.path.exists("app/outputs"):
            os.makedirs("app/outputs")
        
        num_simulations = data.get('numSimulations')
        players_hands = data.get('playersHands', [])
        rivals_hands = data.get('rivalsHands', [])
        board1 = data.get('board1', [])
        board2 = data.get('board2', [])
        num_rivals = data.get('num_rivals', 0)

        # Validaciones básicas
        if not all([num_simulations, players_hands, board1, board2]):
            return jsonify({"success": False, "error": "Faltan parámetros necesarios para la simulación."}), 400

        # Normalizar las cartas
        players_hands = [normalizar_cartas(hand) for hand in players_hands]
        rivals_hands = [normalizar_cartas(hand) for hand in rivals_hands]
        board1 = normalizar_cartas(limpiar_cartas(data.get('board1', [])))
        board2 = normalizar_cartas(limpiar_cartas(data.get('board2', [])))
  
        board = board1 + board2
        folded_players = set(data.get('foldedPlayers', []))  # Extraer jugadores foldeados
        resultados, detailed_logs = simulate_rounds(players_hands, len(rivals_hands), board, num_simulations, folded_players, log_details=True)

        # Generar PDF y Excel
        ruta_pdf = os.path.join("app", "outputs", "simulaciones.pdf")
        ruta_excel = os.path.join("app", "outputs", "simulaciones.xlsx")
        generar_pdf(detailed_logs, ruta_pdf)
        generar_excel(detailed_logs, ruta_excel)
        print("GENEROOOOO")
        
        # Emitir los resultados de la simulación a todos los usuarios en la mesa 25
        socketio.emit('resultados_simulacion', {
            "success": True,
            "resultados": resultados,
            "detailed_logs": detailed_logs
        }, room="mesa_25")  # Emitir en la misma sala "mesa_25"
        print("Emitiendo resultados a la sala mesa_25")  # Verificar que se emite

        return jsonify({"success": True, "resultados": resultados})  # Asegúrate de devolver el 'success' también en el JSON

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


    
@socketio.on('card_selected')
def handle_card_selected(data):
    try:
        # Verifica que los datos necesarios están presentes
        if 'playerId' in data:
            playerId = data['playerId']
            selectedCards = data['selectedCards']
            print(f"Jugador {playerId} seleccionó las cartas: {selectedCards}")
        elif 'board' in data:
            board = data['board']
            boardCards = data['boardCards']
            print(f"Se seleccionaron las cartas para el board {board}: {boardCards}")
        else:
            return {"error": "Datos incompletos"}, 400

        # Emitir los cambios a todos los jugadores conectados en la mesa
        socketio.emit('update_cards', data, room="mesa_25")

    except Exception as e:
        print(f"Error al procesar la carta seleccionada: {e}")
        return {"error": "Error al procesar la selección"}, 500


@socketio.on('card_removed_event')
def handle_card_removed(data):
    try:
        # Verifica que los datos necesarios están presentes
        if 'playerId' in data:
            playerId = data['playerId']
            selectedCards = data['selectedCards']
            print(f"Jugador {playerId} eliminó la carta: {data['cardId']}")
        elif 'board' in data:
            board = data['board']
            print(f"Se eliminó la carta {data['cardId']} del board {board}")
        else:
            return {"error": "Datos incompletos"}, 400

        # Emitir los cambios a todos los jugadores conectados en la mesa
        socketio.emit('update_removed_cards', data, room="mesa_25")

    except Exception as e:
        print(f"Error al procesar la eliminación de carta: {e}")
        return {"error": "Error al procesar la eliminación"}, 500


# Iniciar la aplicación con WebSocket
if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
