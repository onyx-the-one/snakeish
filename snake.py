import pygame
import random
import sys
import os

"""
This is just a project of boredom, dont overthink it.
My latest high score is 45 which i got in spanish class high asf watching the simpsons in french.
Brought to you by onyx. Follow my ig @ubtii16. ^^
Snake-ish v2 - now with modes and shit
"""

# === GAME CONFIGURATION ===
# Basic display
WIDTH, HEIGHT = 1200, 800
TILE_SIZE = 20
COLS = WIDTH // TILE_SIZE
ROWS = HEIGHT // TILE_SIZE

# Modes (pick one)
MODES = {
    "CHILL": {"initial_fps": 6, "speed_inc": False, "wrap": True, "obstacles": 0},
    "STANDARD": {"initial_fps": 8, "speed_inc": True, "wrap": True, "obstacles": 5},
    "AGGRO": {"initial_fps": 12, "speed_inc": True, "wrap": False, "obstacles": 10}
}
CURRENT_MODE = "STANDARD"

# Load mode settings
mode_config = MODES[CURRENT_MODE]
INITIAL_FPS = mode_config["initial_fps"]
SPEED_INCREMENT_ON_FOOD = mode_config["speed_inc"]
WRAP_AROUND_WALLS = mode_config["wrap"]
OBSTACLE_COUNT = mode_config["obstacles"]

INITIAL_SNAKE_LENGTH = 3
START_DIRECTION = (1, 0)  # tuple now
FOOD_SCORE = 1
FOOD_WALL_BUFFER = 1
FPS_STEP = 0.1

# Themes
THEMES = {
    "DEFAULT": {
        "bg": (0, 0, 0),
        "snake_head": (0, 220, 0),
        "snake_body": (0, 170, 0),
        "food": (220, 40, 40),
        "obstacle": (80, 80, 80),
        "hud": (230, 230, 230)
    },
    "BETTER": {
        "bg": (5, 5, 10),
        "snake_head": (255, 0, 150),
        "snake_body": (180, 0, 120),
        "food": (0, 255, 200),
        "obstacle": (100, 100, 100),
        "hud": (240, 240, 240)
    }
}
CURRENT_THEME = "DEFAULT"
theme = THEMES[CURRENT_THEME]

# Keys (both WASD and arrows)
KEY_TO_DIR = {
    pygame.K_w: (0, -1), pygame.K_UP: (0, -1),
    pygame.K_s: (0, 1), pygame.K_DOWN: (0, 1),
    pygame.K_a: (-1, 0), pygame.K_LEFT: (-1, 0),
    pygame.K_d: (1, 0), pygame.K_RIGHT: (1, 0)
}
KEY_PAUSE = pygame.K_p
KEY_RESTART = pygame.K_r
KEY_QUIT = pygame.K_ESCAPE

HIGH_SCORE_FILE = "snake_highscore.txt"

# === END OF CONFIGURATION ===

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("consolas", size, True)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surf, text_rect)

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        f.write(str(score))

def random_grid_position(exclude=None, min_x=0, max_x=None, min_y=0, max_y=None):
    max_x = max_x or COLS
    max_y = max_y or ROWS
    while True:
        pos = (random.randint(min_x, max_x - 1), random.randint(min_y, max_y - 1))
        if not exclude or pos not in exclude:
            return pos

def create_initial_snake():
    start_x = COLS // 2
    start_y = ROWS // 2
    snake = []
    dx, dy = START_DIRECTION
    for i in range(INITIAL_SNAKE_LENGTH):
        snake.append((start_x - i * dx, start_y - i * dy))
    return snake

def create_obstacles(snake, food):
    #bark bark
    occupied = set(snake)
    occupied.add(food)
    obstacles = set()
    for _ in range(OBSTACLE_COUNT):
        pos = random_grid_position(exclude=occupied | obstacles)
        obstacles.add(pos)
    return obstacles

def move_snake(snake, direction):
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])
    if WRAP_AROUND_WALLS:
        new_head = (new_head[0] % COLS, new_head[1] % ROWS)
    return new_head

def check_collisions(new_head, snake, obstacles):
    if not WRAP_AROUND_WALLS:
        if new_head[0] < 0 or new_head[0] >= COLS or new_head[1] < 0 or new_head[1] >= ROWS:
            return True
    if new_head in snake:
        return True
    if new_head in obstacles:
        return True
    return False

def spawn_food(snake, obstacles):
    buffer = FOOD_WALL_BUFFER
    excluded = set(snake) | obstacles
    return random_grid_position(
        exclude=excluded,
        min_x=buffer, max_x=COLS - buffer,
        min_y=buffer, max_y=ROWS - buffer
    )

def handle_input(events, direction, game_over, paused):
    needs_reset = False

    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == KEY_QUIT):
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == KEY_PAUSE:
                paused = not paused
            elif event.key == KEY_RESTART:
                needs_reset = True
            elif not game_over and not paused and event.key in KEY_TO_DIR:
                new_dir = KEY_TO_DIR[event.key]
                # no instant reverse
                if new_dir != (-direction[0], -direction[1]):
                    direction = new_dir

    return direction, needs_reset, paused

def update_game_state(snake, direction, food, score, fps, obstacles, high_score):
    new_head = move_snake(snake, direction)

    if check_collisions(new_head, snake, obstacles):
        if score > high_score:
            save_high_score(score)
        return None, None, score, fps, True  # game over

    snake.insert(0, new_head)

    ate_food = new_head == food
    if ate_food:
        score += FOOD_SCORE
        food = spawn_food(snake, obstacles)
        if SPEED_INCREMENT_ON_FOOD:
            fps += FPS_STEP
    else:
        snake.pop()

    return snake, food, score, fps, False

def draw_scene(screen, snake, food, obstacles, score, fps, game_over, paused, high_score):
    screen.fill(theme["bg"])

    # obstacles
    for pos in obstacles:
        x, y = pos[0] * TILE_SIZE, pos[1] * TILE_SIZE
        pygame.draw.rect(screen, theme["obstacle"], (x, y, TILE_SIZE, TILE_SIZE))

    # snake - FIXED: check if snake exists before drawing
    if snake is not None:
        head_glow = score >= 15
        #fuck ice
        for idx, segment in enumerate(snake):
            x, y = segment[0] * TILE_SIZE, segment[1] * TILE_SIZE
            color = theme["snake_head"] if idx == 0 else theme["snake_body"]
            if head_glow and idx == 0:
                pygame.draw.rect(screen, (255, 255, 255), (x-2, y-2, TILE_SIZE+4, TILE_SIZE+4))
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    # food - FIXED: check if food exists before drawing
    if food is not None:
        fx, fy = food[0] * TILE_SIZE, food[1] * TILE_SIZE
        pygame.draw.rect(screen, theme["food"], (fx, fy, TILE_SIZE, TILE_SIZE))

    # HUD
    draw_text(screen, f"Mode: {CURRENT_MODE}", 16, theme["hud"], 5, 5)
    draw_text(screen, f"Score: {score}  Best: {high_score}", 20, theme["hud"], 5, 25)
    draw_text(screen, f"FPS: {fps:.1f}  Wrap: {'ON' if WRAP_AROUND_WALLS else 'OFF'}", 16, theme["hud"], 5, 50)
    draw_text(screen, "WASD/Arrows: Move  P:Pause  R:Restart  ESC:Quit", 14, theme["hud"], 5, HEIGHT-25)

    # states
    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 100, 255, 128))
        screen.blit(overlay, (0, 0))
        draw_text(screen, "PAUSED (P to resume)", 28, (255,255,255), WIDTH//2-120, HEIGHT//2)

    if game_over:
        if score == 0:
            draw_text(screen, "Skill issue. Press R.", 24, (255,100,100), WIDTH//2-100, HEIGHT//2)
        else:
            draw_text(screen, "GAME OVER - R to restart", 24, (255,100,100), WIDTH//2-140, HEIGHT//2)

    pygame.display.flip()

# MAIN
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake-ish v2")
    clock = pygame.time.Clock()

    high_score = load_high_score()

    def reset_game():
        nonlocal snake, direction, food, score, fps, game_over, paused, obstacles
        snake = create_initial_snake()
        direction = START_DIRECTION
        food = random_grid_position(exclude=set(snake))
        score = 0
        fps = INITIAL_FPS
        game_over = False
        paused = False
        obstacles = create_obstacles(snake, food) if OBSTACLE_COUNT > 0 else set()

    snake = None
    direction = None
    food = None
    score = 0
    # Im a tranny femboy ;w;
    fps = INITIAL_FPS
    game_over = False
    paused = False
    obstacles = set()

    reset_game()

    while True:
        events = pygame.event.get()
        direction, needs_reset, paused = handle_input(events, direction, game_over, paused)

        if needs_reset:
            reset_game()
            continue

        if game_over or paused:
            draw_scene(screen, snake, food, obstacles, score, fps, game_over, paused, high_score)
        else:
            result_snake, result_food, score, fps, game_over = update_game_state(
                snake, direction, food, score, fps, obstacles, high_score
            )
            # Only update snake/food if game not over
            if not game_over:
                snake = result_snake
                food = result_food
            draw_scene(screen, snake, food, obstacles, score, fps, game_over, paused, high_score)

        clock.tick(fps)

if __name__ == "__main__":
    main()
