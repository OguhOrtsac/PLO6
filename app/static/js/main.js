let players = [];
let activePlayer = 1;
let blockedCards = new Set(); // Cartas bloqueadas
let activeBoard = null; // Board activo
const boards = {
    board1: [],
    board2: [],
};
//cambios
let foldedPlayers = new Set(); // Jugadores que han hecho fold


// Conectar al servidor de WebSocket
var socket = io.connect('http://' + document.domain + ':' + location.port);



// seccion para scraping, panel izquierdo

document.getElementById('toggleLock').addEventListener('click', function() {
    let selectBox = document.getElementById('pdiSelect');
    let textBox = document.getElementById('mesaInput');
    let button = document.getElementById('toggleLock');

    if (selectBox.disabled) {
        selectBox.disabled = false;
        textBox.disabled = false;
        button.classList.remove('btn-danger');
        button.classList.add('btn-success');
        button.textContent = 'Bloquear';
    } else {
        selectBox.disabled = true;
        textBox.disabled = true;
        button.classList.remove('btn-success');
        button.classList.add('btn-danger');
        button.textContent = 'Desbloquear';
    }
});

document.getElementById("actualizarPdis").addEventListener("click", function() {
    fetch("/actualizar_pdis")
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let pdiSelect = document.getElementById("pdiSelect");
                pdiSelect.innerHTML = "<option value=''>Seleccione un PDI</option>";
                data.pdis.forEach(pdi => {
                    let option = document.createElement("option");
                    option.value = pdi;
                    option.textContent = pdi;
                    pdiSelect.appendChild(option);
                });
            } else {
                alert("Error al actualizar PDIs");
            }
        })
        .catch(error => console.error("Error en la actualización de PDIs:", error));
});

document.getElementById("num-simulations").addEventListener("input", function (event) {
    let input = event.target;

    // 🔹 Si el valor no es un número entero, corregirlo
    let valor = parseInt(input.value, 10);

    if (isNaN(valor) || valor < 1) {
        input.value = 1000;  // 🔹 Restaurar a 1000 si el valor es inválido
    } else {
        input.value = valor;  // 🔹 Asegurar que sea un número entero
    }
});

// 🔹 Evento para activar el botón con Ctrl + Enter
document.addEventListener("keydown", function (event) {
    if (event.ctrlKey && event.key === "Enter") {  
        event.preventDefault(); // Evita comportamientos no deseados en algunas páginas
        processSimulationWithBoards(); // Llamar la misma función del botón
    }
});





function initializeGameWithBoards(cartas, numCartasBoard) {
    if (!Array.isArray(cartas) || typeof numCartasBoard !== "number") {
        console.error("❌ Parámetros inválidos. Se esperaba un array y un número.");
        return;
    }

    if (numCartasBoard > cartas.length) {
        console.error("❌ numCartasBoard excede la cantidad de cartas en el arreglo.");
        return;
    }

    const board1 = cartas.slice(0, numCartasBoard);
    const board2 = cartas.slice(numCartasBoard);

    console.log("📌 Board 1:", board1);
    console.log("📌 Board 2:", board2);

    function addCardToBoard(board, boardName, card) {
        if (card !== "No se detectó carta válida.png" && !blockedCards.has(card)) {
            if (boards[boardName].length < 5) {
                boards[boardName].push(card);
                blockedCards.add(card);

                // Marcar visualmente la carta como bloqueada
                const cardElement = document.querySelector(`#deck img[alt="${card}"]`)?.parentElement;
                if (cardElement) {
                    cardElement.classList.add("blocked");
                    cardElement.querySelector(".card-blocked-x").style.display = "block";
                }

                console.log(`✅ Carta ${card} asignada a ${boardName}`);
            } else {
                console.warn(`⚠️ ${boardName} ya tiene suficientes cartas.`);
            }
        } else {
            console.warn(`⚠️ Carta duplicada detectada y omitida en ${boardName}: ${card}`);
        }
    }

    // Asignar cartas a los boards evitando duplicaciones
    board1.forEach(card => addCardToBoard(board1, "board1", card));
    board2.forEach(card => addCardToBoard(board2, "board2", card));

    updateBoardCards("board1");
    updateBoardCards("board2");
}

function assignPlayerCards(cartasJugador) {
    if (!Array.isArray(cartasJugador) || cartasJugador.length === 0) {
        console.warn("⚠️ No hay cartas de jugador para asignar.");
        return;
    }

    const cartasValidas = cartasJugador.filter(card => card !== "No se detectó carta válida.png");

    if (cartasValidas.length === 0) {
        console.warn("⚠️ Todas las cartas del jugador fueron inválidas y se omitieron.");
        return;
    }

    let playerId = 1;
    let player = players.find(p => p.id === playerId);

    if (!player) {
        console.error("❌ No se encontró el jugador activo.");
        return;
    }

    function addCardToPlayer(card) {
        if (!blockedCards.has(card)) {  
            if (player.selectedCards.length < 6) {
                player.selectedCards.push(card);
                blockedCards.add(card);

                // Marcar la carta en la baraja como bloqueada
                const cardElement = document.querySelector(`#deck img[alt="${card}"]`)?.parentElement;
                if (cardElement) {
                    cardElement.classList.add("blocked");
                    cardElement.querySelector(".card-blocked-x").style.display = "block";
                }

                console.log(`✅ Carta ${card} asignada al Jugador ${playerId}`);
            } else {
                console.warn(`⚠️ El jugador ${playerId} ya tiene 6 cartas.`);
            }
        } else {
            console.warn(`⚠️ Carta duplicada detectada y omitida en el jugador: ${card}`);
        }
    }

    cartasValidas.forEach(card => addCardToPlayer(card));

    console.log(`📌 Cartas finales del jugador ${playerId}:`, player.selectedCards);
    updatePlayerCards(playerId);
}

document.querySelectorAll("input[name='boardOption']").forEach(radio => {
    radio.addEventListener("change", function() {
        document.querySelectorAll("label.form-check-label").forEach(label => {
            label.classList.remove("text-success");
        });
        this.parentElement.classList.add("text-success");
    });
});

// Inicializa jugadores según el Combo Box
function updatePlayers() {
    const numPlayers = parseInt(document.getElementById("num-active-players").value);
    const playerButtonsContainer = document.getElementById("player-buttons");
    playerButtonsContainer.innerHTML = "";

    if (isNaN(numPlayers) || numPlayers < 1) {
        console.error("Error: Número de jugadores inválido");
        return;
    }

    players = Array.from({ length: numPlayers }, (_, i) => ({
        id: i + 1,
        selectedCards: [],
    }));

    players.forEach((player) => {
        const playerContainer = document.createElement("div");
        playerContainer.className = "player-container mt-3"; // Margen superior para separar de otros botones
        playerContainer.style.border = "2px solid green"; // Borde verde alrededor de cada contenedor de jugador
        playerContainer.style.padding = "10px"; // Agregar algo de padding para que no se vea tan pegado
        playerContainer.style.borderRadius = "5px"; // Bordes redondeados para el contenedor
        playerContainer.innerHTML = `
            <div class="d-flex align-items-center">
                <!-- Botón Player a la izquierda -->
                <button class="btn btn-primary me-2" onclick="setActivePlayer(${player.id})" id="player-button-${player.id}">
                    Player ${player.id}
                </button>
    
                <!-- Indicador al lado del botón Player -->
                <span id="indicator-${player.id}" class="indicator me-3"></span>
    
                <!-- Botón Fold al lado del indicador -->
                <button class="btn btn-warning btn-sm" onclick="toggleFold(${player.id})" id="fold-button-${player.id}">
                    Fold
                </button>
            </div>
    
            <!-- Cartas seleccionadas debajo de los botones -->
            <div id="selected-cards-${player.id}" class="selected-cards mt-2"></div>
        `;
        playerButtonsContainer.appendChild(playerContainer);
    });
    


    // Verificar si hay al menos un jugador
    if (players.length > 0) {
        setActivePlayer(players[0].id);
    } else {
        activePlayer = null;
    }
}

function toggleFold(playerId) {
    const foldButton = document.getElementById(`fold-button-${playerId}`);
    const playerButton = document.getElementById(`player-button-${playerId}`);

    if (foldedPlayers.has(playerId)) {
        // Si ya estaba en Fold, lo quitamos y lo activamos nuevamente
        foldedPlayers.delete(playerId);
        foldButton.classList.remove("btn-danger");
        foldButton.classList.add("btn-warning");
        foldButton.textContent = "Fold";
        playerButton.disabled = false;
    } else {
        // Si no estaba en Fold, lo agregamos y deshabilitamos su botón de selección
        foldedPlayers.add(playerId);
        foldButton.classList.remove("btn-warning");
        foldButton.classList.add("btn-danger");
        foldButton.textContent = "Unfold";
        playerButton.disabled = true; // Deshabilitar selección de jugador
    }
}


// Cambia el jugador activo
function setActivePlayer(playerId) {
    console.log("Jugador activo cambiado a:", playerId); // Depuración del jugador activo
    activePlayer = playerId;
    activeBoard = null; // Desactiva cualquier board activo

    // 🔹 Quitar la selección de todos los indicadores
    document.querySelectorAll(".indicator").forEach((el) => el.classList.remove("active"));
    document.getElementById(`indicator-${playerId}`).classList.add("active");

    // 🔹 Quitar la selección de los boards
    document.querySelectorAll(".board-area").forEach((el) => el.classList.remove("board-active"));

    // 🔹 Restaurar el color original de los botones de boards
    document.querySelectorAll(".board-btn").forEach((el) => el.classList.remove("btn-success"));
}

// Cambia el board activo
function setActiveBoard(boardId) {
    activeBoard = boardId;
    activePlayer = null; // Desactiva cualquier jugador activo

    // 🔹 Remover la clase 'board-active' de todos los boards
    document.querySelectorAll(".board-area").forEach((el) => el.classList.remove("board-active"));
    document.getElementById(boardId)?.classList.add("board-active");

    // 🔹 Remover la clase 'active' de todos los indicadores
    document.querySelectorAll(".indicator").forEach((el) => el.classList.remove("active"));

    // 🔹 Remover la clase 'btn-success' de todos los botones de boards
    document.querySelectorAll(".board-btn").forEach((el) => el.classList.remove("btn-success"));

    // 🔹 Buscar el botón del board por ID
    const boardButton = document.getElementById(`${boardId}-button`);
    if (boardButton) {
        boardButton.classList.add("btn-success");
    } else {
        console.warn(`⚠️ No se encontró el botón para el board '${boardId}'.`);
    }
}



function resetGame() {
    // Desbloquear todas las cartas
    blockedCards.clear();
    document.querySelectorAll(".card-container").forEach((card) => {
        card.classList.remove("blocked");
        card.querySelector(".card-blocked-x").style.display = "none";
    });

    // Reiniciar jugadores
    players.forEach((player) => {
        player.selectedCards = [];
        updatePlayerCards(player.id);
    });

    // Reiniciar boards
    Object.keys(boards).forEach((boardId) => {
        boards[boardId] = [];
        updateBoardCards(boardId);
    });
    // Generar nuevos jugadores según el número seleccionado
    updatePlayers();
}

function getFormattedPlayersHands() {
    return players.map(player => player.selectedCards.map(card => card.replace('.png', '').replace('_', '')));
}

function generateBoard() {
    // Ejemplo: Retorna un board aleatorio para pruebas
    return ["2h", "3h", "4h", "5h", "6h"];
}


// Actualiza las cartas seleccionadas de un jugador
function updatePlayerCards(playerId) {
    const playerCardsContainer = document.getElementById(`selected-cards-${playerId}`);
    const player = players.find((p) => p.id === playerId);
    playerCardsContainer.innerHTML = player.selectedCards
        .map(
            (cardId) => `
        <div class="selected-card me-2 position-relative">
            <img src="/static/images/baraja/${cardId}" alt="${cardId}" class="small-card">
            <button class="btn-close selected-card-x" onclick="removeCard('${cardId}')"></button>
        </div>
        `
        )
        .join("");
}

// Actualiza las cartas seleccionadas de un board
function updateBoardCards(boardId) {
    const boardCardsContainer = document.getElementById(boardId);
    if (!boardCardsContainer) {
        console.error(`Error: El board '${boardId}' no está configurado en el DOM.`);
        return;
    }

    boardCardsContainer.innerHTML = boards[boardId]
        .map(
            (cardId) => `
        <div class="selected-card me-2 position-relative">
            <img src="/static/images/baraja/${cardId}" alt="${cardId}" class="small-card">
            <button class="btn-close selected-card-x" onclick="removeCard('${cardId}', 'board', '${boardId}')"></button>
        </div>
        `
        )
        .join("");
}

// Bloquea una carta en la baraja
function blockCardInDeck(cardId) {
    const cardElement = document.querySelector(`#deck img[alt="${cardId}"]`);
    if (cardElement) {
        cardElement.classList.add("blocked");
        cardElement.style.cursor = "not-allowed";
    }
}

// Desbloquea una carta en la baraja
function unblockCardInDeck(cardId) {
    const cardElement = document.querySelector(`#deck img[alt="${cardId}"]`);
    if (cardElement) {
        cardElement.classList.remove("blocked");
        cardElement.style.cursor = "pointer";
    }
}

// Inicializa
updatePlayers();


function displaySimulationResults(results, cadena) {
    
    const resultsContainer = document.getElementById(cadena);
    const numSimulations = parseInt(document.getElementById("num-simulations").value);
    if (!resultsContainer) {
        console.error("Error: No se encontró el contenedor con id:", cadena);
        return;
    }

    if (!results.board1Wins || !results.board2Wins || !results.board1Ties || !results.board2Ties) {
        resultsContainer.innerHTML = "<p>Error: No se recibieron resultados válidos.</p>";
        return;
    }

    resultsContainer.innerHTML = ""; // Limpiar contenido antes de actualizar

    // Crear la estructura de la tabla con encabezados
    resultsContainer.innerHTML = `
        <h4 class="text-center">Resultados:</h4>
        <table class="table table-bordered">
            <thead class="thead-dark">
                <tr>
                    <th class="text-left">Nombre</th>
                    <th class="text-center" colspan="2">Board 1</th>
                    <th class="text-center" colspan="2">Board 2</th>
                </tr>
                <tr>
                    <th class="text-left"></th>
                    <th class="text-center">Victorias</th>
                    <th class="text-center">Empates</th>
                    <th class="text-center">Victorias</th>
                    <th class="text-center">Empates</th>
                </tr>
            </thead>
            <tbody>
            ${results.board1Wins.map((_, index) => {
                    // Calcular porcentajes
                    const board1WinPercentage = ((results.board1Wins[index] / numSimulations) * 100).toFixed(1);
                    const board1TiePercentage = ((results.board1Ties[index] / numSimulations) * 100).toFixed(1);
                    const board2WinPercentage = ((results.board2Wins[index] / numSimulations) * 100).toFixed(1);
                    const board2TiePercentage = ((results.board2Ties[index] / numSimulations) * 100).toFixed(1);

                    return `
                    <tr>
                        <td>Jugador ${index + 1}</td>
                        <td>${results.board1Wins[index]} (${board1WinPercentage}%)</td>
                        <td>${results.board1Ties[index]} (${board1TiePercentage}%)</td>
                        <td>${results.board2Wins[index]} (${board2WinPercentage}%)</td>
                        <td>${results.board2Ties[index]} (${board2TiePercentage}%)</td>
                    </tr>`;
            }).join("")}
            </tbody>
        </table>
    `;

}


//cosas de las simulaciones con boards

function validateSimulationsInput() {
    const input = document.getElementById("num-simulations").value;
    return /^\d+$/.test(input); // Solo números
}

// 🔹 Mantener la funcionalidad del botón solo en JavaScript
document.getElementById("process-with-boards").addEventListener("click", function() {
    processSimulationWithBoards();
});


function processSimulationWithBoards() {
    if (!validateSimulationsInput()) {
        alert("Por favor, ingresa un número válido para las simulaciones.");
        return;
    }

    const numSimulations = parseInt(document.getElementById("num-simulations").value);
    const numRivals = parseInt(document.getElementById("num-rivals").value);

    // Validar que ambos boards tengan el mismo número de cartas
    if (boards.board1.length !== boards.board2.length) {
        alert("Los boards deben tener el mismo número de cartas antes de procesar.");
        return;
    }

    // Obtener cartas no bloqueadas
    const unblockedCards = getUnblockedCards();
    shuffleArray(unblockedCards); // Barajar cartas

    // Completar los boards si falta
    while (boards.board1.length < 2) boards.board1.push(unblockedCards.pop());
    while (boards.board2.length < 2) boards.board2.push(unblockedCards.pop());

    // Asignar cartas a los rivales
    const rivalsHands = [];
    for (let i = 0; i < numRivals; i++) {
        rivalsHands.push(unblockedCards.splice(0, 6));
    }

    // Llamar a la simulación incluyendo los foldeados
    simulateRoundsWithBoards(numSimulations, rivalsHands);
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function getUnblockedCards() {
    const allCards = [...Array(52)].map((_, i) => `${"23456789TJQKA"[Math.floor(i / 4)]}${"hdcs"[i % 4]}`);
    const usedCards = [...blockedCards, ...boards.board1, ...boards.board2].flat();
    return allCards.filter(card => !usedCards.includes(card));
}




document.getElementById("procesarPdi").addEventListener("click", function () {
    resetGame();
    let pdiSeleccionado = document.getElementById("pdiSelect").value;
    let boardSeleccionado = document.querySelector("input[name='boardOption']:checked");

    if (pdiSeleccionado && boardSeleccionado) {
        console.log("PDI seleccionado:", pdiSeleccionado);

        // Emitir el evento de WebSocket
        socket.emit('capturar', {
            pdi: pdiSeleccionado,
            board: boardSeleccionado.value
        });
    } else {
        alert("Seleccione un PDI y un Board antes de procesar.");
    }
});

socket.on('connect', function() {
    console.log('Conectado a la mesa 25');
    // Emitir el mensaje 'listo' después de unirse a la sala
});




// Escuchar el evento de actualización de captura desde el servidor
socket.on('actualizacion_captura', function(data) {
    console.log('Actualización de captura:', data);

    if (data.success) {
        let cartasBoard = data.cartas_board || [];
        let cartasJugador = data.cartas_jugador || [];
        let numCartasBoard = data.num_CartasBoard || 0;
        console.log('Datooos', data.num_CartasBoard)
        // 🔹 Llamar funciones con las cartas extraídas
        initializeGameWithBoards(cartasBoard, numCartasBoard);
        assignPlayerCards(cartasJugador);
    } else {
        alert("Error en la captura: " + (data.error || "Desconocido"));
    }
});


// Esta es la función para simular las rondas utilizando sockets
function simulateRoundsWithBoards(numSimulations, rivalsHands) {
    const playersHands = getFormattedPlayersHands(); // Obtener las manos de los jugadores
    const board1 = boards.board1;
    const board2 = boards.board2;

    // 🔹 Asegurar que foldedPlayers está definido y tiene un formato válido
    const foldedPlayersArray = Array.from(foldedPlayers || []);

    // Emitir el evento 'simulate_with_boards' al servidor con los datos necesarios
    socket.emit('simulate_with_boards', {
        numSimulations,
        playersHands,
        rivalsHands,
        board1,
        board2,
        foldedPlayers: foldedPlayersArray, // Enviar siempre una lista
    });

}

    
// Escuchar la respuesta del servidor para obtener los resultados de la simulación
socket.on('resultados_simulacion', function(data) {
    console.log('Procesando resultadoooooos:', data);

    if (data.success) {
        const cadena = "simulation-results2";
        displaySimulationResults(data.resultados, cadena);
    } else {
        alert("Ocurrió un error durante la simulación: " + (data.error || "Desconocido"));
    }
});


socket.on('error', function(error) {
    console.error('Error en el WebSocket:', error);
});



function selectCard(cardId) {
    if (blockedCards.has(cardId)) return; // No permitir seleccionar cartas bloqueadas

    if (activePlayer) {
        const player = players.find((p) => p.id === activePlayer);
        if (player.selectedCards.length < 6) {
            player.selectedCards.push(cardId);
            blockedCards.add(cardId); // Bloquear la carta al seleccionarla

            // Mostrar la X en la carta bloqueada visualmente
            const cardElement = document.querySelector(`#deck img[alt="${cardId}"]`).parentElement;
            cardElement.classList.add("blocked");
            cardElement.querySelector(".card-blocked-x").style.display = "block";

            // Actualizar las cartas del jugador
            updatePlayerCards(activePlayer);

            // Emitir evento al servidor para que otros jugadores reciban la carta seleccionada
            socket.emit('card_selected', {
                playerId: activePlayer,
                cardId: cardId,
                selectedCards: player.selectedCards // Mandamos la lista de cartas seleccionadas del jugador
            });
        } else {
            alert("Un jugador no puede tener más de 6 cartas seleccionadas.");
        }
    } else if (activeBoard) {
        if (boards[activeBoard].length < 5) {
            boards[activeBoard].push(cardId);
            blockedCards.add(cardId); // Bloquear la carta al seleccionarla

            // Mostrar la X en la carta bloqueada visualmente
            const cardElement = document.querySelector(`#deck img[alt="${cardId}"]`).parentElement;
            cardElement.classList.add("blocked");
            cardElement.querySelector(".card-blocked-x").style.display = "block";

            // Actualizar las cartas del board
            updateBoardCards(activeBoard);

            // Emitir evento al servidor para que otros jugadores reciban la carta seleccionada en el board
            socket.emit('card_selected', {
                board: activeBoard,
                cardId: cardId,
                boardCards: boards[activeBoard] // Mandamos las cartas del board actual
            });
        } else {
            alert("Un board no puede tener más de 5 cartas seleccionadas.");
        }
    } else {
        alert("Selecciona un jugador o un board primero.");
    }
}

// Escuchar el evento de actualización de cartas desde el servidor
socket.on('update_cards', function(data) {
    console.log("Actualizando cartas:", data);

    // Si se trata de un jugador, actualizamos sus cartas seleccionadas
    if (data.playerId) {
        const player = players.find(p => p.id === data.playerId);
        if (player) {
            player.selectedCards = data.selectedCards;
            updatePlayerCards(data.playerId);
        }
    }

    // Si se trata de un board, actualizamos las cartas del board
    if (data.board) {
        boards[data.board] = data.boardCards;
        updateBoardCards(data.board);
    }

    // Aquí añadimos la parte de bloquear las cartas visualmente en todos los clientes
    const cardElement = document.querySelector(`#deck img[alt="${data.cardId}"]`);
    if (cardElement) {
        // Bloquear la carta visualmente
        cardElement.parentElement.classList.add("blocked");
        cardElement.parentElement.querySelector(".card-blocked-x").style.display = "block";

        // Asegurarnos de agregar la carta a blockedCards globalmente
        blockedCards.add(data.cardId);  // Agregar la carta a la lista global de cartas bloqueadas

        // Asegurarnos de que la carta esté en la lista de cartas seleccionadas del jugador y del board
        if (data.playerId) {
            const player = players.find(p => p.id === data.playerId);
            if (player && !player.selectedCards.includes(data.cardId)) {
                player.selectedCards.push(data.cardId); // Agregar la carta a la lista de cartas seleccionadas del jugador
            }
        }

        if (data.board) {
            if (!boards[data.board].includes(data.cardId)) {
                boards[data.board].push(data.cardId); // Agregar la carta a la lista de cartas seleccionadas del board
            }
        }
    }
});



// Deselecciona una carta
function removeCard(cardId, type = 'player', boardId = null) {
    if (!blockedCards.has(cardId)) return; // No permitir deselectar cartas no bloqueadas

    // Emisión global de la eliminación de la carta
    if (type === 'player' && activePlayer) {
        const player = players.find((p) => p.id === activePlayer);
        const cardIndex = player.selectedCards.indexOf(cardId);
        if (cardIndex > -1) {
            player.selectedCards.splice(cardIndex, 1);
            blockedCards.delete(cardId);  // Desbloquear la carta

            // Quitar la X en la carta bloqueada visualmente
            const cardElement = document.querySelector(`#deck img[alt="${cardId}"]`).parentElement;
            cardElement.classList.remove("blocked");
            cardElement.querySelector(".card-blocked-x").style.display = "none";

            // Actualizar las cartas del jugador
            updatePlayerCards(activePlayer);

            // Emitir evento al servidor para que todos los jugadores reciban la carta eliminada
            socket.emit('card_removed_event', {
                cardId: cardId,  // Mandamos la carta eliminada
                playerId: activePlayer,
                selectedCards: player.selectedCards // Mandamos la lista de cartas seleccionadas actualizadas
            });
        }
    } else if (type === 'board' && boardId) {
        const boardIndex = boards[boardId].indexOf(cardId);
        if (boardIndex > -1) {
            boards[boardId].splice(boardIndex, 1);
            blockedCards.delete(cardId); // Desbloquear la carta

            // Quitar la X en la carta bloqueada visualmente
            const cardElement = document.querySelector(`#deck img[alt="${cardId}"]`).parentElement;
            cardElement.classList.remove("blocked");
            cardElement.querySelector(".card-blocked-x").style.display = "none";

            // Actualizar las cartas del board
            updateBoardCards(boardId);

            // Emitir evento al servidor para que todos los jugadores reciban la carta eliminada en el board
            socket.emit('card_removed_event', {
                cardId: cardId,
                board: boardId,
                boardCards: boards[boardId] // Mandamos las cartas del board actual
            });
        }
    } else {
        alert("Selecciona un jugador o un board primero.");
    }
}

// Escuchar el evento de actualización de cartas eliminadas desde el servidor
socket.on('update_removed_cards', function(data) {
    console.log("Actualizando cartas eliminadas:", data);

    // Si se trata de un jugador
    if (data.playerId) {
        const player = players.find(p => p.id === data.playerId);
        if (player) {
            player.selectedCards = data.selectedCards;
            updatePlayerCards(data.playerId);
        }
    }

    // Si se trata de un board
    if (data.board) {
        boards[data.board] = data.boardCards;
        updateBoardCards(data.board);
    }

    // Rehabilitar la carta para ser seleccionada de nuevo en el deck
    if (data.cardId) {
        const cardElement = document.querySelector(`#deck img[alt="${data.cardId}"]`).parentElement;
        cardElement.classList.remove("blocked");
        cardElement.querySelector(".card-blocked-x").style.display = "none";
        blockedCards.delete(data.cardId);
    }
});
