class PlayerManager:
    def __init__(self, num_players=6):
        self.num_players = num_players
        self.players = {i: {"selected_cards": []} for i in range(1, num_players + 1)}

    def update_num_players(self, num_players):
        """
        Actualiza el número de jugadores y reinicia las selecciones.
        """
        self.num_players = num_players
        self.players = {i: {"selected_cards": []} for i in range(1, num_players + 1)}

    def select_card(self, player_id, card):
        """
        Añade una carta a las seleccionadas por el jugador.
        """
        if len(self.players[player_id]["selected_cards"]) < 6:
            self.players[player_id]["selected_cards"].append(card)
            return True
        return False

    def deselect_card(self, player_id, card):
        """
        Elimina una carta seleccionada por el jugador.
        """
        if card in self.players[player_id]["selected_cards"]:
            self.players[player_id]["selected_cards"].remove(card)
            return True
        return False
