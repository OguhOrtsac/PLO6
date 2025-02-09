class Deck:
    def __init__(self):
        # Orden de los palos: Picas, Corazones, Tréboles, Diamantes
        self.suits = ['S', 'H', 'C', 'D']  
        # Orden de los valores: A, 2, 3, ..., K
        self.values = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']  
        self.cards = self.generate_deck()  # Generar las cartas en orden correcto

    def generate_deck(self):
        """
        Genera las 52 cartas en el orden correcto: A, 2, 3, ..., K, por cada palo.
        """
        deck = []
        for suit in self.suits:
            for value in self.values:
                card = f"{value}_{suit}.png"
                deck.append(card)
        return deck

    def shuffle_deck(self):
        """
        Baraja las cartas.
        """
        from random import shuffle
        shuffle(self.cards)

    def render_cards(self):
        """
        Genera el HTML para renderizar las cartas en una cuadrícula con eventos onclick.
        """
        html = '<div class="container">'
        for i in range(0, len(self.cards), 13):  # 13 cartas por fila
            html += '<div class="row my-1 gx-1">'  # Reducimos espacio entre columnas con gx-1
            for card in self.cards[i:i + 13]:
                html += f'''
                    <div class="col-auto" style="padding: 2px; margin: 1px;">
                        <img 
                            src="../static/images/baraja/{card}" 
                            alt="{card}" 
                            class="card-img" 
                            onclick="selectCard('{card}')"
                            style="width: 60px; height: auto;"
                        >
                    </div>
                '''
            html += '</div>'
        html += '</div>'
        return html





