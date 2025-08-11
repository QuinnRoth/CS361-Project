import zmq
import random
import time
import signal
import sys

GRID_SIZE = 10
context = zmq.Context()

# REP socket to receive turn notification and send move back
move_socket = context.socket(zmq.REP)
move_socket.bind("tcp://*:5557")  # changed from connect to bind

# PUSH socket to send initial setup
setup_sender = context.socket(zmq.PUSH)
setup_sender.connect("tcp://localhost:5555")

time.sleep(1)

# Place ships automatically
ships = []
used = set()
lengths = [4, 3, 3, 2, 2]

def signal_handler(sig, frame):
    print("Game logic service shutting down...")
    if 'setup_sender' in globals():
        setup_sender.close()
    if 'move_socket' in globals():
        move_socket.close()
    if 'context' in globals():
        context.term()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

for length in lengths:
    placed = False
    while not placed:
        orientation = random.choice(["horizontal", "vertical"])
        if orientation == "horizontal":
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - length)
            ship = [(row, col + i) for i in range(length)]
        else:
            row = random.randint(0, GRID_SIZE - length)
            col = random.randint(0, GRID_SIZE - 1)
            ship = [(row + i, col) for i in range(length)]

        if all((r, c) not in used for r, c in ship):
            ships.append(ship)
            used.update(ship)
            placed = True

# Send ship placement
setup_sender.send_json({
    "type": "placement",
    "ships": ships,
    "player": "AI"
})

setup_sender.send_json({"type": "ready", "player": "AI"})

shots = set()
hits = set()

def get_adjacent_cells(row, col):
    adjacent = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and (r, c) not in shots:
            adjacent.append((r, c))

    return adjacent


while True:
    msg = move_socket.recv_json()
    print(f"Received message (opp): {msg}", flush=True)
    if msg.get("type") == "your_turn":
        # Make a random move
        print("AI is thinking...", flush=True)

        if msg.get("result") is not None:  # get info from previous turn
            print("result is not none")
            result_info = msg["result"]
            if result_info.get("result") == "hit":  # if hit add it to list of hit cells
                row, col = result_info.get("row"), result_info.get("col")
                hits.add((row, col))
            elif result_info.get("result") == "sunk":  # if sunk, remove the ship from hits
                sunk_ship = result_info.get("sunk_ship", [])
                for r, c in sunk_ship:
                    hits.discard((r, c))
        # Always try to target adjacent cells to any current hit
        target_candidates = []
        print(f"Current hits: {hits}", flush=True)
        for hit_row, hit_col in hits:
            print("in hit for loop")
            adjacent_cells = get_adjacent_cells(hit_row, hit_col)
            target_candidates.extend(adjacent_cells)
        if target_candidates:
            print(f"Target candidates: {target_candidates}", flush=True)
            row, col = random.choice(target_candidates)
            shots.add((row, col))
            print(f"AI fires at ({row}, {col}) (adjacent to hit)", flush=True)
        else:
            # Otherwise, pick a random cell that hasn't been targeted yet
            available_cell = False
            while not available_cell:
                row = random.randint(0, GRID_SIZE - 1)
                col = random.randint(0, GRID_SIZE - 1)
                if (row + col) % 2 == 0 and (row, col) not in shots:
                    available_cell = True
            shots.add((row, col))
            print(f"AI fires at ({row}, {col}) (random)", flush=True)
        move_socket.send_json({
            "type": "fire",
            "row": row,
            "col": col,
            "player": "AI"
        })
