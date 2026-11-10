import pygame
import sys

from game import CaroGame


# ==============================
# 1. KHỞI TẠO
# ==============================

pygame.init()

WIDTH = 800
HEIGHT = 850

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CARO AI 9x9")

# Màu sắc
BACKGROUND = (245, 222, 179)
BOARD_COLOR = (190, 140, 80)
BLACK = (30, 30, 30)
RED = (220, 50, 50)
BLUE = (40, 100, 220)
WHITE = (255, 255, 255)
GREEN = (40, 160, 80)

FONT = pygame.font.SysFont("Arial", 25)
TITLE_FONT = pygame.font.SysFont("Arial", 36, bold=True)

# Kích thước bàn cờ
BOARD_SIZE = 9
CELL_SIZE = 75

START_X = 70
START_Y = 150

# Khởi tạo game
game = CaroGame(BOARD_SIZE)

clock = pygame.time.Clock()


# ==============================
# 2. VẼ CHỮ
# ==============================

def draw_text(text, font, color, x, y):
    image = font.render(text, True, color)
    SCREEN.blit(image, (x, y))


# ==============================
# 3. VẼ BÀN CỜ
# ==============================

def draw_board():
    SCREEN.fill(BACKGROUND)

    draw_text(
        "CARO AI 9x9",
        TITLE_FONT,
        BLACK,
        300,
        25
    )

    # Nền bàn cờ
    pygame.draw.rect(
        SCREEN,
        BOARD_COLOR,
        (
            START_X - 15,
            START_Y - 15,
            CELL_SIZE * 8 + 30,
            CELL_SIZE * 8 + 30
        )
    )

    # Vẽ các đường ngang và dọc
    for i in range(BOARD_SIZE):
        x = START_X + i * CELL_SIZE
        y = START_Y + i * CELL_SIZE

        pygame.draw.line(
            SCREEN,
            BLACK,
            (START_X, y),
            (START_X + CELL_SIZE * 8, y),
            2
        )

        pygame.draw.line(
            SCREEN,
            BLACK,
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

    # Hiển thị lượt chơi
    if game.game_over:

        if game.winner == 0:
            status = "KET QUA: HOA!"
        else:
            status = f"CHUC MUNG! {game.result()} THANG!"

        draw_text(
            status,
            FONT,
            GREEN,
            230,
            90
        )

    else:
        player_name = "X" if game.current_player == 1 else "O"

        color = RED if game.current_player == 1 else BLUE

        draw_text(
            f"Luot hien tai: {player_name}",
            FONT,
            color,
            320,
            90
        )

    # Nút chơi lại
    button = pygame.Rect(630, 30, 130, 45)

    pygame.draw.rect(
        SCREEN,
        GREEN,
        button,
        border_radius=8
    )

    draw_text(
        "Choi lai",
        FONT,
        WHITE,
        650,
        38
    )

    return button


# ==============================
# 4. XỬ LÝ CLICK
# ==============================

def handle_click(pos, reset_button):

    mouse_x, mouse_y = pos

    # Click nút chơi lại
    if reset_button.collidepoint(pos):
        game.reset()
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


# ==============================
# 5. VÒNG LẶP GAME
# ==============================

running = True

while running:

    reset_button = draw_board()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Click chuột
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                handle_click(
                    event.pos,
                    reset_button
                )

        # Nhấn phím R để chơi lại
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game.reset()

            if event.key == pygame.K_ESCAPE:
                running = False

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()