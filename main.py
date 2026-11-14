import json
import sys
import threading

import pygame

from core.game import CaroGame
from agents.random_agent import RandomAgent
from agents.heuristic_agent import HeuristicAgent
from agents.minimax_agent import MinimaxAgent
from agents.mcts_agent import MCTSAgent
from agents.supervised_agent import SupervisedAgent
from evaluation.tournament import RESULTS_PATH, run_tournament
from evaluation.statistics import rank_standings


# ==============================
# 1. KHỞI TẠO
# ==============================

pygame.init()

WIDTH = 840
HEIGHT = 920

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CARO AI 9x9")

# Màu sắc
BACKGROUND = (242, 245, 239)
BOARD_COLOR = (229, 220, 193)
INK = (38, 51, 44)
MUTED = (111, 124, 114)
BLACK = INK
RED = (198, 72, 61)
BLUE = (47, 119, 142)
WHITE = (255, 255, 255)
GREEN = (48, 125, 88)
SHADOW = (218, 226, 217)
GRID = (120, 119, 96)

FONT = pygame.font.SysFont("segoeui", 21, bold=True)
SMALL_FONT = pygame.font.SysFont("segoeui", 15)
TITLE_FONT = pygame.font.SysFont("georgia", 36, bold=True)

# Kích thước bàn cờ
BOARD_SIZE = 9
CELL_SIZE = 70

START_X = 140
START_Y = 245

# Khởi tạo game
game = CaroGame(BOARD_SIZE)
random_agent = RandomAgent(seed=7)
heuristic_agent = HeuristicAgent(seed=7)
minimax_agent = MinimaxAgent(depth=2, candidate_limit=6)
mcts_agent = MCTSAgent(iterations=80, rollout_depth=10, candidate_limit=7, seed=7)
supervised_agent = SupervisedAgent(seed=7)

MODE_PVP = "pvp"
MODE_RANDOM = "random"
MODE_HEURISTIC = "heuristic"
MODE_MINIMAX = "minimax"
MODE_MCTS = "mcts"
MODE_SUPERVISED = "supervised"
mode = MODE_PVP
MODE_LABELS = {
    MODE_PVP: "Hai nguoi choi",
    MODE_RANDOM: "Nguoi choi vs AI Random",
    MODE_HEURISTIC: "Nguoi choi vs AI Heuristic",
    MODE_MINIMAX: "Nguoi choi vs AI Minimax",
    MODE_MCTS: "Nguoi choi vs AI MCTS",
    MODE_SUPERVISED: "Nguoi choi vs AI hoc",
}
stats_view = False
tournament_running = False
tournament_error = None


def load_latest_tournament():
    try:
        return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


tournament_result = load_latest_tournament()

clock = pygame.time.Clock()


# ==============================
# 2. VẼ CHỮ
# ==============================

def draw_text(text, font, color, x, y):
    image = font.render(text, True, color)
    SCREEN.blit(image, (x, y))


def draw_centered_text(text, font, color, center):
    image = font.render(text, True, color)
    SCREEN.blit(image, image.get_rect(center=center))


# ==============================
# 3. VẼ BÀN CỜ
# ==============================

def draw_board():
    SCREEN.fill(BACKGROUND)

    draw_text("CARO", TITLE_FONT, INK, 34, 20)
    draw_text("9x9  |  CHON CHE DO", SMALL_FONT, MUTED, 38, 68)
    pygame.draw.line(SCREEN, SHADOW, (32, 96), (808, 96), 2)

    reset_button = pygame.Rect(642, 28, 112, 46)
    close_button = pygame.Rect(772, 28, 46, 46)
    pygame.draw.rect(SCREEN, GREEN, reset_button, border_radius=8)
    draw_centered_text("Choi lai", FONT, WHITE, reset_button.center)

    close_color = (171, 57, 53) if close_button.collidepoint(pygame.mouse.get_pos()) else RED
    pygame.draw.rect(SCREEN, close_color, close_button, border_radius=8)
    center_x, center_y = close_button.center
    pygame.draw.line(SCREEN, WHITE, (center_x - 7, center_y - 7), (center_x + 7, center_y + 7), 3)
    pygame.draw.line(SCREEN, WHITE, (center_x + 7, center_y - 7), (center_x - 7, center_y + 7), 3)

    supervised_label = "6  AI hoc"
    if not supervised_agent.is_available:
        supervised_label += " (thieu PyTorch)"
    elif not supervised_agent.is_trained:
        supervised_label += " (chua train)"
    mode_options = (
        (MODE_PVP, "1.  Hai nguoi choi"),
        (MODE_RANDOM, "2.  AI Random"),
        (MODE_HEURISTIC, "3.  AI Heuristic"),
        (MODE_MINIMAX, "4. Minimax + Alpha-Beta"),
        (MODE_MCTS, "5.s  Monte Carlo (MCTS)"),
        (MODE_SUPERVISED, supervised_label),
    )
    mode_buttons = {}
    for index, (mode_value, label) in enumerate(mode_options):
        column = index % 3
        row = index // 3
        button = pygame.Rect(34 + column * 260, 108 + row * 56, 248, 50)
        selected = mode == mode_value
        pygame.draw.rect(
            SCREEN,
            GREEN if selected else WHITE,
            button,
            border_radius=8,
        )
        if not selected:
            pygame.draw.rect(SCREEN, SHADOW, button, width=1, border_radius=8)
        draw_centered_text(label, SMALL_FONT, WHITE if selected else INK, button.center)
        mode_buttons[mode_value] = button

    if game.game_over:
        status = "VAN CO" if game.winner == 0 else f"{game.result()} THANG!"
        status_color = GREEN
    else:
        player_name = "X" if game.current_player == 1 else "O"
        status = f"LUOT CUA {player_name}"
        status_color = RED if game.current_player == 1 else BLUE

    board_rect = pygame.Rect(
        START_X - 18,
        START_Y - 18,
        CELL_SIZE * 8 + 36,
        CELL_SIZE * 8 + 36,
    )
    pygame.draw.rect(SCREEN, SHADOW, board_rect.move(0, 7), border_radius=12)
    pygame.draw.rect(SCREEN, BOARD_COLOR, board_rect, border_radius=12)

    # Vẽ các đường ngang và dọc
    for i in range(BOARD_SIZE):
        x = START_X + i * CELL_SIZE
        y = START_Y + i * CELL_SIZE

        pygame.draw.line(
            SCREEN,
            GRID,
            (START_X, y),
            (START_X + CELL_SIZE * 8, y),
            2
        )

        pygame.draw.line(
            SCREEN,
            GRID,
            (x, START_Y),
            (x, START_Y + CELL_SIZE * 8),
            2
        )

    # Vẽ các quân cờ
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):

            player = game.board[row][col]

            if player == 0:
                continue

            x = START_X + col * CELL_SIZE
            y = START_Y + row * CELL_SIZE

            if player == 1:
                # Quân X
                pygame.draw.line(
                    SCREEN,
                    RED,
                    (x - 20, y - 20),
                    (x + 20, y + 20),
                    5
                )

                pygame.draw.line(
                    SCREEN,
                    RED,
                    (x + 20, y - 20),
                    (x - 20, y + 20),
                    5
                )

            else:
                # Quân O
                pygame.draw.circle(
                    SCREEN,
                    BLUE,
                    (x, y),
                    23,
                    5
                )

    # Đánh dấu 5 quân chiến thắng
    if game.winning_cells:
        for row, col in game.winning_cells:

            x = START_X + col * CELL_SIZE
            y = START_Y + row * CELL_SIZE

            pygame.draw.circle(
                SCREEN,
                GREEN,
                (x, y),
                29,
                3
            )

    draw_centered_text(
        status,
        FONT,
        status_color,
        (WIDTH // 2, 802),
    )
    draw_centered_text(
        "T: Dau giai  |  S: Thong ke  |  R: Choi lai  |  Esc: Thoat",
        SMALL_FONT,
        MUTED,
        (WIDTH // 2, 884),
    )

    if stats_view:
        draw_stats_overlay()

    return reset_button, close_button, mode_buttons


# ==============================
# 4. XỬ LÝ CLICK
# ==============================

def handle_click(pos, reset_button, mode_buttons):

    mouse_x, mouse_y = pos

    # Click nút chơi lại
    if reset_button.collidepoint(pos):
        game.reset()
        return

    for mode_value, button in mode_buttons.items():
        if button.collidepoint(pos):
            switch_mode(mode_value)
            return

    if mode != MODE_PVP and game.current_player == 2:
        return

    # Chuyển tọa độ chuột thành tọa độ ô
    col = round((mouse_x - START_X) / CELL_SIZE)
    row = round((mouse_y - START_Y) / CELL_SIZE)

    # Kiểm tra khoảng cách đến giao điểm
    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        return

    x = START_X + col * CELL_SIZE
    y = START_Y + row * CELL_SIZE

    distance = ((mouse_x - x) ** 2 + (mouse_y - y) ** 2) ** 0.5

    if distance <= 30:
        game.make_move(row, col)


def switch_mode(new_mode):
    global mode
    mode = new_mode
    game.reset()


def play_ai_turn():
    if game.game_over or game.current_player != 2 or mode == MODE_PVP:
        return

    agent = {
        MODE_RANDOM: random_agent,
        MODE_HEURISTIC: heuristic_agent,
        MODE_MINIMAX: minimax_agent,
        MODE_MCTS: mcts_agent,
        MODE_SUPERVISED: supervised_agent,
    }[mode]
    move = agent.choose_move(game)
    if move is not None:
        game.make_move(*move)


def start_tournament():
    global tournament_running, tournament_error, stats_view
    if tournament_running:
        return

    tournament_running = True
    tournament_error = None
    stats_view = True

    def run_in_background():
        global tournament_result, tournament_running, tournament_error
        try:
            tournament_result = run_tournament(games_per_pair=2)
        except Exception as error:
            tournament_error = str(error)
        finally:
            tournament_running = False

    threading.Thread(target=run_in_background, daemon=True).start()


def draw_stats_overlay():
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((25, 34, 29, 185))
    SCREEN.blit(veil, (0, 0))

    panel = pygame.Rect(90, 150, 660, 600)
    pygame.draw.rect(SCREEN, BACKGROUND, panel, border_radius=10)
    draw_text("KET QUA DAU GIA", TITLE_FONT, INK, 126, 176)
    draw_text("Bang xep hang AI", FONT, MUTED, 128, 232)

    if tournament_running:
        draw_text("Giai dang dien ra... ket qua se tu cap nhat", FONT, GREEN, 128, 290)
    elif tournament_error:
        draw_text("Khong the chay giai:", FONT, RED, 128, 290)
        draw_text(tournament_error[:68], SMALL_FONT, INK, 128, 324)
    elif tournament_result:
        draw_text("AI", SMALL_FONT, MUTED, 132, 284)
        draw_text("DIEM", SMALL_FONT, MUTED, 410, 284)
        draw_text("THANG / HOA / THUA", SMALL_FONT, MUTED, 510, 284)
        for index, (name, stats) in enumerate(
            rank_standings(tournament_result.get("standings", {}))
        ):
            y = 322 + index * 54
            pygame.draw.line(SCREEN, SHADOW, (128, y + 34), (712, y + 34), 1)
            draw_text(f"{index + 1}. {name}"[:28], FONT, INK, 132, y)
            draw_text(f"{stats['points']:g}", FONT, GREEN, 420, y)
            draw_text(
                f"{stats['wins']} / {stats['draws']} / {stats['losses']}",
                SMALL_FONT,
                MUTED,
                530,
                y + 4,
            )
        match_count = len(tournament_result.get("matches", []))
        draw_text(f"So tran: {match_count}  |  Luu tai: {RESULTS_PATH.name}", SMALL_FONT, MUTED, 128, 632)
    else:
        draw_text("Chua co ket qua. Nhan T de bat dau giai AI.", FONT, MUTED, 128, 290)

    draw_text("Nhan S de dong bang thong ke", SMALL_FONT, MUTED, 128, 700)


# ==============================
# 5. VÒNG LẶP GAME
# ==============================

running = True

while running:

    play_ai_turn()

    reset_button, close_button, mode_buttons = draw_board()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Click chuột
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if stats_view:
                    continue
                if close_button.collidepoint(event.pos):
                    running = False
                else:
                    handle_click(event.pos, reset_button, mode_buttons)

        # Nhấn phím R để chơi lại
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game.reset()
            elif event.key == pygame.K_1:
                switch_mode(MODE_PVP)
            elif event.key == pygame.K_2:
                switch_mode(MODE_RANDOM)
            elif event.key == pygame.K_3:
                switch_mode(MODE_HEURISTIC)
            elif event.key == pygame.K_4:
                switch_mode(MODE_MINIMAX)
            elif event.key == pygame.K_5:
                switch_mode(MODE_MCTS)
            elif event.key == pygame.K_6:
                switch_mode(MODE_SUPERVISED)
            elif event.key == pygame.K_t:
                start_tournament()
            elif event.key == pygame.K_s:
                stats_view = not stats_view
            elif event.key == pygame.K_ESCAPE:
                running = False

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()