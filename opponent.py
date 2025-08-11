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

while True:
    msg = move_socket.recv_json()
    print(f"Received message (opp): {msg}", flush=True)
    if msg.get("type") == "your_turn":
        # Make a random move
        print("AI is thinking...", flush=True)
        available_cell = False

        while available_cell is False:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            if (row, col) not in shots:
                available_cell = True
        shots.add((row, col))
        print(f"AI fires at ({row}, {col})", flush=True)
        move_socket.send_json({
            "type": "fire",
            "row": row,
            "col": col,
            "player": "AI"
        })
