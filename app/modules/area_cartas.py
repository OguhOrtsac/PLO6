def obtener_area_boards(width, height, num_CartasBoard):
    """
    Retorna las coordenadas dinámicas basadas en el tamaño de la captura .
    """
    # Factores relativos al tamaño de la imagen
    separacion_x = width * 0.122  # Espacio horizontal entre cartas
    separacion_boards = height * 0.023  # Espacio vertical entre los dos boards
    
    # Dimensiones relativas de las cartas del board
    ancho_carta = width * 0.054
    alto_carta = height * 0.031
    alto_carta_ant = height * 0.084

    # Posiciones iniciales de las cartas en el board
    x_inicial_board1 = width * 0.202
    y_board1 = height * 0.404
    x_inicial_board2 = x_inicial_board1
    y_board2 = y_board1 + alto_carta_ant + separacion_boards

    # Generar dinámicamente las áreas para ambos boards
    areas = []

    # Calcular áreas del board 1
    for i in range(num_CartasBoard):
        x = x_inicial_board1 + i * separacion_x
         
        if i == 4: x += 2  
         # Si es la carta número 2 (índice 1 en la lista), restar 1 píxel
        if i == 1:  x -= 2 
        areas.append((int(x), int(y_board1), int(ancho_carta), int(alto_carta)))

    # Calcular áreas del board 2
    for i in range(num_CartasBoard):
        x = x_inicial_board2 + i * separacion_x
        if i == 4: x += 2 
         # Si es la carta número 2 (índice 1 en la lista), restar 1 píxel
        if i == 1: x -= 2 
        areas.append((int(x), int(y_board2), int(ancho_carta), int(alto_carta)))

    return areas


def obtener_area_jugador(width, height):
    """
    Retorna las coordenadas dinámicas para las cartas del jugador.
    """
    # Dimensiones relativas de las cartas del jugador
    ancho_carta_jugador = width * 0.042
    alto_carta_jugador = height * 0.025

    # Posiciones iniciales como porcentaje
    x_inicial_jugador = width * 0.535
    y_jugador = height * 0.806

    # Generar dinámicamente las áreas para las cartas del jugador
    areas = []
    for i in range(6):
        x = x_inicial_jugador + i * (ancho_carta_jugador + (width * 0.002))  # Separación dinámica entre cartas
        areas.append((int(x), int(y_jugador), int(ancho_carta_jugador), int(alto_carta_jugador)))

    return areas
