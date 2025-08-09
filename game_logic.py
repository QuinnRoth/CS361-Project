import zmq
import time

GRID_SIZE = 10

context = zmq.Context()
to_game = context.socket(zmq.REP)
to_game.bind("tcp://*:5560")  # changed port from 5558 to 5560

time.sleep(0.2)

players = {
    "player": {
        "board": [["empty"] * GRID_SIZE for _ in range(GRID_SIZE)],
        "ships": [],
        "hits": set(),
        "sunk": 0
    },
    "AI": {
        "board": [["empty"] * GRID_SIZE for _ in range(GRID_SIZE)],
        "ships": [],
        "hits": set(),
        "sunk": 0
    }
}

def place_ship(player, ship_data):
    board = players[player]["board"]
    ships = []
    for ship in ship_data:
        if isinstance(ship, dict):  # from UI
            row, col = ship["row"], ship["col"]
            size = ship["size"]
            orientation = ship["orientation"]
            cells = []
            for i in range(size):
                r = row + i if orientation == "vertical" else row
                c = col + i if orientation == "horizontal" else col
                board[r][c] = "ship"
                cells.append((r, c))
            ships.append(cells)
        elif isinstance(ship, list):  # from AI
            cells = []
            for r, c in ship:
                board[r][c] = "ship"
                cells.append((r, c))
            ships.append(cells)
    players[player]["ships"] = ships
    players[player]["sunk"] = 0
    players[player]["hits"] = set()

def is_ship_sunk(ship, hits):
    return all(cell in hits for cell in ship)

def fire_at(player, row, col):
    target = "AI" if player == "player" else "player"
    board = players[target]["board"]
    hits = players[target]["hits"]
    ships = players[target]["ships"]

    fire_result = ""
    sunk = False
    game_over = False

    if board[row][col] == "ship":
        board[row][col] = "hit"
        hits.add((row, col))
        fire_result = "hit"

        for ship in ships:
            if (row, col) in ship:
                if is_ship_sunk(ship, hits):
                    sunk = True
                    players[target]["sunk"] += 1
                    fire_result = "sunk"
                    break

        if players[target]["sunk"] == len(ships):
            game_over = True

    elif board[row][col] == "empty":
        board[row][col] = "miss"
        fire_result = "miss"
    else:
        fire_result = board[row][col]  # already hit or miss

    return {
        "type": "result",
        "player": player,
        "row": row,
        "col": col,
        "result": fire_result,
        "sunk": sunk,
        "game_over": game_over,
        "winner": player if game_over else None
    }


print("Game logic service running...")

while True:
    msg = to_game.recv_json()
    msg_type = msg.get("type")
    print("Received message (logic):", msg)

    if msg_type == "placement":
        player = msg.get("player", "player")
        print(f"Placing ships for {player}")
        place_ship(player, msg["ships"])
        to_game.send_json({"status": "ok"})
    elif msg_type == "fire":
        player = msg.get("player", "player")
        row, col = msg["row"], msg["col"]
        print(f"{player} fires at ({row}, {col})")
        result = fire_at(player, row, col)
        to_game.send_json(result)
        if result.get("game_over"):
            exit(0)
    else:
        to_game.send_json({"status": "unknown"})
