import pandas as pd
import os  # Para manejo de rutas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ruta_pdf = os.path.join("app", "outputs", "simulaciones.pdf")
ruta_excel = os.path.join("app", "outputs", "simulaciones.xlsx")

def generar_pdf(detailed_logs, output_path=ruta_pdf):
    """
    Genera un archivo PDF con los detalles de las simulaciones, incluyendo jugadores, rivales y ganadores.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 50  # Espaciado inicial desde la parte superior

    for log in detailed_logs:
        # Título de la simulación
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Simulación {log['simulation']}")
        y -= 20

        # Manos de los jugadores
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Manos de los jugadores principales:")
        for i, hand in enumerate(log["players_hands"]):
            y -= 15
            c.drawString(70, y, f"Jugador {i + 1}: {', '.join(hand)}")
        
        y -= 20

        # Manos de los rivales
        c.drawString(50, y, "Manos de los rivales:")
        for i, hand in enumerate(log["rivals_hands"]):
            y -= 15
            c.drawString(70, y, f"Rival {i + 1}: {', '.join(hand)}")
        
        y -= 20

        # Boards
        c.drawString(50, y, f"Board 1: {', '.join(log['board1'])}")
        y -= 15
        c.drawString(50, y, f"Board 2: {', '.join(log['board2'])}")
        
        y -= 20
        
        # Board 1: Imprimir solo ganadores o empates, nunca ambos
        if "board1_tied_players" in log and log["board1_tied_players"]:
            c.drawString(50, y, "Empates en el Board 1:")
            for tied in log["board1_tied_players"]:
                y -= 15
                jugador_tipo = "Jugador" if tied["type"] == "player" else "Rival"
                c.drawString(
                    70, y,
                    f"{jugador_tipo} {tied['player_number']} - Mano completa: {', '.join(tied['hand'])}, Mejor mano: {', '.join(tied['best_hand'])}"
                )
        else:
            c.drawString(50, y, "Ganadores del Board 1:")
            for winner in log["board1_winner"]:
                y -= 15
                jugador_tipo = "Jugador" if winner["type"] == "player" else "Rival"
                c.drawString(
                    70, y,
                    f"{jugador_tipo} {winner['player_number']} - Mano completa: {', '.join(winner['hand'])}, Mejor mano: {', '.join(winner['best_hand'])}"
                )

        y -= 30

        # Board 2: Imprimir solo ganadores o empates, nunca ambos
        if "board2_tied_players" in log and log["board2_tied_players"]:
            c.drawString(50, y, "Empates en el Board 2:")
            for tied in log["board2_tied_players"]:
                y -= 15
                jugador_tipo = "Jugador" if tied["type"] == "player" else "Rival"
                c.drawString(
                    70, y,
                    f"{jugador_tipo} {tied['player_number']} - Mano completa: {', '.join(tied['hand'])}, Mejor mano: {', '.join(tied['best_hand'])}"
                )
        else:
            c.drawString(50, y, "Ganadores del Board 2:")
            for winner in log["board2_winner"]:
                y -= 15
                jugador_tipo = "Jugador" if winner["type"] == "player" else "Rival"
                c.drawString(
                    70, y,
                    f"{jugador_tipo} {winner['player_number']} - Mano completa: {', '.join(winner['hand'])}, Mejor mano: {', '.join(winner['best_hand'])}"
                )

        y -= 30




        # Espacio entre simulaciones
        y -= 80
        if y < 200:  # Si estamos cerca del borde inferior, crea una nueva página
            c.showPage()
            y = height - 50

    c.save()

def generar_excel(detailed_logs, output_path=ruta_excel):
    """
    Genera un archivo Excel con los detalles de las simulaciones, incluyendo jugadores, rivales y ganadores.
    """
    rows = []

    for log in detailed_logs:
        # Detalles de los jugadores principales
        for i, hand in enumerate(log["players_hands"]):
            rows.append({
                "Simulación": log["simulation"],
                "Tipo": "Jugador",
                "ID": i + 1,
                "Mano completa": ", ".join(hand),
                "Board": "N/A",
                "Mejor mano": "N/A",
                "Ganador": "No"
            })
        
        # Detalles de los rivales
        for i, hand in enumerate(log["rivals_hands"]):
            rows.append({
                "Simulación": log["simulation"],
                "Tipo": "Rival",
                "ID": i + 1,
                "Mano completa": ", ".join(hand),
                "Board": "N/A",
                "Mejor mano": "N/A",
                "Ganador": "No"
            })
        
        # Ganadores del Board 1
        for winner in log["board1_winner"]:
            rows.append({
                "Simulación": log["simulation"],
                "Tipo": winner["type"].capitalize(),
                "ID": "N/A",
                "Mano completa": ", ".join(winner["hand"]),
                "Board": "1",
                "Mejor mano": ", ".join(winner["best_hand"]),
                "Ganador": "Sí"
            })

        # Ganadores del Board 2
        for winner in log["board2_winner"]:
            rows.append({
                "Simulación": log["simulation"],
                "Tipo": winner["type"].capitalize(),
                "ID": "N/A",
                "Mano completa": ", ".join(winner["hand"]),
                "Board": "2",
                "Mejor mano": ", ".join(winner["best_hand"]),
                "Ganador": "Sí"
            })

    # Crear DataFrame y exportar a Excel
    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)
