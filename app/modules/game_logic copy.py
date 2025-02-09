
from itertools import combinations
import random


from treys import Evaluator, Card

evaluator = Evaluator()


def generar_combinaciones_validas(mano_jugador, board):
    """
    Genera todas las combinaciones válidas de 2 cartas de la mano y 3 cartas del board.
    """
    
    

    combinaciones_mano = combinations(mano_jugador, 2)
   # print(f"mano JUGADOR P R I N C I P A L{mano_jugador}")
    combinaciones_board = combinations(board, 3)
   # combinaciones_lista = list(combinaciones_mano)  # Convierte el iterador en una lista

   # print(f"combinaciones de LA MANO     00000000: {combinaciones_lista}")
    # Convertir a lista para calcular la longitud
    # Imprimir el número de combinaciones
    #print(f"Cantidad de combinaciones en combinaciones_mano: {cantidad_combinaciones}")
    # Asegúrate de que combinaciones_mano sea una lista
    combinaciones_mano = list(combinaciones_mano)  # Si ya era un iterador, ahora será una lista
    combinaciones_board = list(combinaciones_board)  # También aplica si combinaciones_board es un iterador

    # Generar todas las combinaciones válidas
   # resultado = [list(mano) + list(board_part) for mano in combinaciones_mano for board_part in combinaciones_board]
   # print(resultado)
   # return resultado

    return [list(mano) + list(board_part) for mano in combinaciones_mano for board_part in combinaciones_board]

def simulate_rounds(players_hands, num_rivals, board_cards, num_simulations, log_details=False):
    """
    Simula rondas de Omaha PLO6 para determinar ganadores en cada board considerando jugadores y rivales.
    """
    results = {
        "board1Wins": [0] * len(players_hands),  # Conteo de victorias para los jugadores principales
        "board2Wins": [0] * len(players_hands),
        "board1Ties": [0] * len(players_hands),  # Conteo de empates
        "board2Ties": [0] * len(players_hands),
    }
    rival_wins = {
        "board1": 0,  # Conteo de victorias para los rivales en el board 1
        "board2": 0   # Conteo de victorias para los rivales en el board 2
    }
    rival_ties = {
        "board1": 0,  # Conteo de empates con rivales en el board 1
        "board2": 0   # Conteo de empates con rivales en el board 2
    }
    detailed_logs = []  # Para registrar las primeras simulaciones

    for sim in range(num_simulations):
        # Barajar y repartir cartas a los rivales
        remaining_deck = shuffle_deck(players_hands, board_cards)
        rivals_hands = [remaining_deck[i * 6:(i + 1) * 6] for i in range(num_rivals)]
        
        if len(board_cards) <= 5:
        # Si board_cards tiene 5 o menos cartas, usar el comportamiento original
            board1 = remaining_deck[num_rivals * 6:num_rivals * 6 + 5]
            board2 = remaining_deck[num_rivals * 6 + 5:num_rivals * 6 + 10]
        elif len(board_cards) == 6:
            # Si board_cards tiene 6 cartas, dividir en 3 para cada board y completar con remaining_deck
            board1 = board_cards[:3] + remaining_deck[num_rivals * 6:num_rivals * 6 + 2]
            board2 = board_cards[3:] + remaining_deck[num_rivals * 6 + 2:num_rivals * 6 + 4]
        elif len(board_cards) == 8:
            # Si board_cards tiene 8 cartas, dividir en 4 para cada board y completar con remaining_deck
            board1 = board_cards[:4] + remaining_deck[num_rivals * 6:num_rivals * 6 + 1]
            board2 = board_cards[4:] + remaining_deck[num_rivals * 6 + 1:num_rivals * 6 + 2]
        elif len(board_cards) == 10:
            # Si board_cards tiene 10 cartas, dividir en 5 para cada board
            board1 = board_cards[:5]
            board2 = board_cards[5:]
        else:
            raise ValueError(f"Cantidad inválida de cartas en board_cards: {len(board_cards)}")

       # board1 = remaining_deck[num_rivals * 6:num_rivals * 6 + 5]
       # board2 = remaining_deck[num_rivals * 6 + 5:num_rivals * 6 + 10]

        # Evaluar manos en ambos boards
        all_scores_board1 = []  # Puntuaciones de todos (jugadores principales y rivales) en el board 1
        all_scores_board2 = []  # Puntuaciones de todos (jugadores principales y rivales) en el board 2

        # Evaluar jugadores principales
        for player_hand in players_hands:
            score1, best_hand1 = encontrar_mejor_mano(player_hand, board1)
            score2, best_hand2 = encontrar_mejor_mano(player_hand, board2)
            all_scores_board1.append((score1, "player", player_hand, best_hand1))
            all_scores_board2.append((score2, "player", player_hand, best_hand2))

        # Evaluar rivales
        for rival_hand in rivals_hands:
            score1, best_hand1 = encontrar_mejor_mano(rival_hand, board1)
            score2, best_hand2 = encontrar_mejor_mano(rival_hand, board2)
            all_scores_board1.append((score1, "rival", rival_hand, best_hand1))
            all_scores_board2.append((score2, "rival", rival_hand, best_hand2))


        # Determinar ganadores en el board 1
        min_score1 = min(score for score, _, _, _ in all_scores_board1)
        winners_board1 = [hand for score, _, hand, _ in all_scores_board1 if score == min_score1]

        # Si hay más de un ganador, es un empate
        if len(winners_board1) > 1:
            for score, entity, hand, best_hand in all_scores_board1:
                if score == min_score1:
                    if entity == "player":
                        results["board1Ties"][players_hands.index(hand)] += 1  # Sumar empate en board 1
                    elif entity == "rival":
                        rival_ties["board1"] += 1  # Sumar empate para rivales en board 1
        else:
            for score, entity, hand, best_hand in all_scores_board1:
                if score == min_score1:
                    if entity == "player":
                        results["board1Wins"][players_hands.index(hand)] += 1  # Sumar victoria
                    elif entity == "rival":
                        rival_wins["board1"] += 1  # Sumar victoria para rivales en board 1

        # Determinar ganadores en el board 2
        min_score2 = min(score for score, _, _, _ in all_scores_board2)
        winners_board2 = [hand for score, _, hand, _ in all_scores_board2 if score == min_score2]

        # Si hay más de un ganador, es un empate
        if len(winners_board2) > 1:
            for score, entity, hand, best_hand in all_scores_board2:
                if score == min_score2:
                    if entity == "player":
                        results["board2Ties"][players_hands.index(hand)] += 1  # Sumar empate en board 2
                    elif entity == "rival":
                        rival_ties["board2"] += 1  # Sumar empate para rivales en board 2
        else:
            for score, entity, hand, best_hand in all_scores_board2:
                if score == min_score2:
                    if entity == "player":
                        results["board2Wins"][players_hands.index(hand)] += 1  # Sumar victoria
                    elif entity == "rival":
                        rival_wins["board2"] += 1  # Sumar victoria para rivales en board 2


        # Registrar detalles de las primeras simulaciones
        if log_details and sim < 100:
            def get_player_number(hand, entity):
                """ Retorna el número del jugador o rival basado en su posición en la lista correspondiente. """
                if entity == "player":
                    return players_hands.index(hand) + 1  # Jugadores empiezan en 1
                else:  # Es un rival
                    return rivals_hands.index(hand) + 1  # Rivales también empiezan en 1

            detailed_log = {
                "simulation": sim + 1,
                "players_hands": players_hands,
                "rivals_hands": rivals_hands,
                "board1": board1,
                "board2": board2,
                "board1_winner": [
                    {
                        "player_number": get_player_number(hand, entity),  # Obtiene el número del jugador o rival
                        "type": entity,
                        "hand": hand,
                        "best_hand": best_hand
                    }
                    for score, entity, hand, best_hand in all_scores_board1 if score == min_score1
                ],
                "board2_winner": [
                    {
                        "player_number": get_player_number(hand, entity),  # Obtiene el número del jugador o rival
                        "type": entity,
                        "hand": hand,
                        "best_hand": best_hand
                    }
                    for score, entity, hand, best_hand in all_scores_board2 if score == min_score2
                ]
            }

            # Verificar si hubo empate en el Board 1 y agregar solo si hay más de un ganador
            tied_players_board1 = [
                {
                    "player_number": get_player_number(hand, entity),  # Obtiene el número del jugador o rival
                    "type": entity,
                    "hand": hand,
                    "best_hand": best_hand
                }
                for score, entity, hand, best_hand in all_scores_board1 if score == min_score1
            ]
            if len(tied_players_board1) > 1:  # Solo guardar si hubo más de un jugador con la mejor mano
                detailed_log["board1_tied_players"] = tied_players_board1

            # Verificar si hubo empate en el Board 2 y agregar solo si hay más de un ganador
            tied_players_board2 = [
                {
                    "player_number": get_player_number(hand, entity),  # Obtiene el número del jugador o rival
                    "type": entity,
                    "hand": hand,
                    "best_hand": best_hand
                }
                for score, entity, hand, best_hand in all_scores_board2 if score == min_score2
            ]
            if len(tied_players_board2) > 1:  # Solo guardar si hubo más de un jugador con la mejor mano
                detailed_log["board2_tied_players"] = tied_players_board2

            # Agregar a detailed_logs solo después de haber verificado los empates
            detailed_logs.append(detailed_log)

    return results, detailed_logs

def evaluar_mano(cartas):
    """
    Evalúa una mano de póker y devuelve su ranking y la mejor combinación.
    """
    # Separar valores y palos
    valores = [carta[:-1] for carta in cartas]
    palos = [carta[-1] for carta in cartas]

    # Mapeo de valores a números
    valor_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                 '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    valores = [valor_map[v] for v in valores]
    valores.sort(reverse=True)

    # Contar repeticiones de valores
    conteo_valores = {v: valores.count(v) for v in set(valores)}
    repetidos = sorted(conteo_valores.items(), key=lambda x: (-x[1], -x[0]))

    # Clasificación
    es_flush = len(set(palos)) == 1
    es_escalera = len(set(valores)) == 5 and max(valores) - min(valores) == 4

    if es_flush and es_escalera:
        return (1, valores)  # Escalera de color
    if repetidos[0][1] == 4:
        return (2, [repetidos[0][0]] * 4 + valores)  # Póker
    if repetidos[0][1] == 3 and repetidos[1][1] == 2:
        return (3, [repetidos[0][0]] * 3 + [repetidos[1][0]] * 2)  # Full house
    if es_flush:
        return (4, valores)  # Flush
    if es_escalera:
        return (5, valores)  # Escalera
    if repetidos[0][1] == 3:
        return (6, [repetidos[0][0]] * 3 + valores)  # Trío
    if repetidos[0][1] == 2 and repetidos[1][1] == 2:
        return (7, [repetidos[0][0]] * 2 + [repetidos[1][0]] * 2 + valores)  # Dos pares
    if repetidos[0][1] == 2:
        return (8, [repetidos[0][0]] * 2 + valores)  # Par
    return (9, valores)  # Carta alta

def encontrar_mejor_mano(mano_jugador, board):
    """
    Encuentra la mejor mano posible para un jugador en Omaha PLO6.
    Evalúa todas las combinaciones válidas de 2 cartas de la mano y 3 del board.
    """
    combinaciones = generar_combinaciones_validas(mano_jugador, board)
    mejor_puntuacion = float('inf')
    mejor_mano = None
    evaluaciones = []  # Para registrar combinaciones evaluadas

    for combinacion in combinaciones:
        # Validar longitud de la combinación
        if len(combinacion) != 5:
            continue

        try:
            # Convertir las cartas al formato Treys
            treys_cartas = [Card.new(carta) for carta in combinacion]
            puntuacion = evaluator.evaluate([], treys_cartas)

            # Registrar la evaluación
            evaluaciones.append({"combinacion": combinacion, "puntuacion": puntuacion})

            # Actualizar la mejor mano
            if puntuacion < mejor_puntuacion:
               # print(f"tronoo IF PUNTUACION")
                mejor_puntuacion = puntuacion
                mejor_mano = combinacion
        except Exception as e:
            import traceback
            print("Ocurrió un error:")
            print(f"Tipo: {type(e).__name__}")
            print(f"Mensaje: {e}")
            traceback.print_exc()  # Imprime el stack trace completo
    # Registrar todas las evaluaciones para depuración
    return mejor_puntuacion, mejor_mano

def shuffle_deck(players_hands, board_cards):
    """
    Baraja las cartas restantes del mazo, excluyendo las ya usadas.
    
    Args:
        players_hands (list): Listas de las cartas de todos los jugadores.
        board_cards (list): Cartas asignadas a los boards.

    Returns:
        list: Mazo barajado con las cartas restantes.
    """
    # Todas las cartas de la baraja
    full_deck = [
        f"{rank}{suit}" for rank in "23456789TJQKA" for suit in "hdcs"
    ]

    # Cartas ya usadas por los jugadores y en el board
    used_cards = set(card for hand in players_hands for card in hand)
    used_cards.update(board_cards)

    # Cartas restantes
    remaining_deck = [card for card in full_deck if card not in used_cards]

    # Barajar las cartas restantes
    random.shuffle(remaining_deck)

    return remaining_deck


