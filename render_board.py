import time

import pygame
import zmq
import sys

# Constants
TILE_SIZE = 40
GRID_SIZE = 10
MARGIN = 40
BOARD_SPACING = 160

WIDTH = GRID_SIZE * TILE_SIZE * 2 + BOARD_SPACING
HEIGHT = GRID_SIZE * TILE_SIZE + MARGIN * 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BLUE = (100, 100, 255)

placing_ships = True
current_ship_size = 3
ships_to_place = [3, 3, 2, 2]
placed_ships = []
ship_orientation = "horizontal"
hover_tile = None

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
pygame.display.set_caption("Battleship - Player vs AI")
font = pygame.font.SysFont(None, 28)

# ZMQ setup
context = zmq.Context()
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5555")

receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5556")
receiver.RCVTIMEO = 100  # Non-blocking receive, timeouts after 100ms

time.sleep(.2)

# State
player_board = [["empty"] * GRID_SIZE for _ in range(GRID_SIZE)]
enemy_board = [["unknown"] * GRID_SIZE for _ in range(GRID_SIZE)]
game_over = False
winner = None


def draw_grid(board, offset_x, offset_y, show_ships):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            cell = board[r][c]
            color = BLUE  # default

            if cell == "ship" and show_ships:
                color = GRAY
            elif cell == "hit":
                color = RED
            elif cell == "miss":
                color = WHITE
            elif cell == "sunk":
                color = BLACK

            pygame.draw.rect(screen, color,
                             (offset_x + c * TILE_SIZE, offset_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, (0, 0, 0),
                             (offset_x + c * TILE_SIZE, offset_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    if placing_ships and offset_x == MARGIN and hover_tile:
        row, col = hover_tile
        valid = True
        ship_len = current_ship_size
        for i in range(ship_len):
            rr = row + i if ship_orientation == "vertical" else row
            cc = col + i if ship_orientation == "horizontal" else col
            if rr >= GRID_SIZE or cc >= GRID_SIZE or board[rr][cc] != "empty":
                valid = False
        color = (0, 255, 0) if valid else (255, 100, 100)
        for i in range(ship_len):
            rr = row + i if ship_orientation == "vertical" else row
            cc = col + i if ship_orientation == "horizontal" else col
            if rr < GRID_SIZE and cc < GRID_SIZE:
                pygame.draw.rect(screen, color,
                                 (offset_x + cc * TILE_SIZE, offset_y + rr * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

    player_text = "PLAYER" if show_ships else "ENEMY"
    text = font.render(f"{player_text}", True, (255, 255, 255))
    screen.blit(text, (offset_x + GRID_SIZE * TILE_SIZE // 2 - text.get_width() // 2, offset_y - 20))


def draw_game_over():
    if game_over:
        msg = f"Game Over! Winner: {winner}"
        txt = font.render(msg, True, (255, 255, 0))
        screen.blit(txt, (10, HEIGHT + 10))


def get_enemy_clicked_cell(mx, my):
    board_x = GRID_SIZE * TILE_SIZE + BOARD_SPACING
    if my < MARGIN or my >= HEIGHT - MARGIN:
        return None
    if board_x <= mx < board_x + GRID_SIZE * TILE_SIZE:
        row = (my - MARGIN) // TILE_SIZE
        col = (mx - board_x) // TILE_SIZE
        return row, col
    return None


def get_player_clicked_cell(mx, my):
    board_x = MARGIN
    if my < MARGIN or my >= HEIGHT - MARGIN:
        return None
    if board_x <= mx < board_x + GRID_SIZE * TILE_SIZE:
        row = (my - MARGIN) // TILE_SIZE
        col = (mx - board_x) // TILE_SIZE
        return row, col
    return None


# Game loop
running = True
while running:
    screen.fill((30, 30, 30))

    # Draw two boards
    draw_grid(player_board, MARGIN, MARGIN, show_ships=True)
    draw_grid(enemy_board, GRID_SIZE * TILE_SIZE + BOARD_SPACING, MARGIN, show_ships=False)
    draw_game_over()

    if placing_ships:
        txt = font.render(
            f"Placing ship size {current_ship_size} ({ship_orientation}) - Press R to rotate",
            True, (255, 255, 255)
        )
        screen.blit(txt, (10, HEIGHT + 10))

        mouse_pos = pygame.mouse.get_pos()
        hover_tile = get_player_clicked_cell(*mouse_pos)
    else:
        hover_tile = None

    pygame.display.flip()

    # Handle game logic messages
    try:
        msg = receiver.recv_json()
        print(f"Received message: {msg}")
        if msg["type"] == "update":
            r, c = msg["row"], msg["col"]
            result = msg["result"]
            target = msg["player"]

            if target == "AI":
                player_board[r][c] = result if result in ["hit", "miss", "sunk"] else player_board[r][c]
            else:
                enemy_board[r][c] = result if result in ["hit", "miss", "sunk"] else enemy_board[r][c]

        elif msg["type"] == "game_over":
            game_over = True
            winner = msg["winner"]
    except zmq.error.Again:
        pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if placing_ships and event.key == pygame.K_r:
                ship_orientation = "vertical" if ship_orientation == "horizontal" else "horizontal"

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            pos = pygame.mouse.get_pos()

            if placing_ships:
                click = get_player_clicked_cell(*pos)
                if click:
                    row, col = click

                    if ((ship_orientation == "horizontal" and col + current_ship_size <= GRID_SIZE) or
                            (ship_orientation == "vertical" and row + current_ship_size <= GRID_SIZE)):
                        valid = True

                        for i in range(current_ship_size):
                            rr = row + i if ship_orientation == "vertical" else row
                            cc = col + i if ship_orientation == "horizontal" else col
                            if player_board[rr][cc] == "ship":
                                valid = False

                        if valid:
                            ship = []
                            for i in range(current_ship_size):
                                rr = row + i if ship_orientation == "vertical" else row
                                cc = col + i if ship_orientation == "horizontal" else col
                                player_board[rr][cc] = "ship"
                                ship.append({"row": rr, "col": cc})

                            placed_ships.append({
                                "row": row,
                                "col": col,
                                "size": current_ship_size,
                                "orientation": ship_orientation
                            })
                            ships_to_place.pop(0)
                            if ships_to_place:
                                current_ship_size = ships_to_place[0]
                            else:
                                placing_ships = False
                                # Send to main controller
                                sender.send_json({
                                    "type": "placement",
                                    "ships": placed_ships,
                                    "player": "player"
                                })

            else:
                click = get_enemy_clicked_cell(*pos)
                if click:
                    row, col = click
                    if enemy_board[row][col] == "unknown":
                        sender.send_json({
                            "type": "fire",
                            "row": row,
                            "col": col,
                            "player": "player"
                        })

pygame.quit()
sys.exit()
