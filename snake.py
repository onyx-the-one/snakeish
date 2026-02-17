import pygame
import random
import sys

"""
This is just a project of boredom, dont overthink it.
My latest high score is 45 which i got in spanish class high asf watching the simpsons in french.
Brought to you by onyx. Follow my ig @ubtii16. ^^
"""

# === GAME CONFIGURATION ===
# Basic display
WIDTH, HEIGHT = 1200, 800          # Window size in pixels
TILE_SIZE = 20                    # Size of each grid tile in pixels

# Gameplay tuning
INITIAL_FPS = 8                  # Base speed of the game
SPEED_INCREMENT_ON_FOOD = True    # Increase speed slightly each time you eat
FPS_STEP = 0.1                    # How much FPS increases per food

WRAP_AROUND_WALLS = True         # If True, snake appears on opposite side instead of dying

# Snake setup
INITIAL_SNAKE_LENGTH = 3         # Starting length of the snake
START_DIRECTION = [1, 0]          # Initial direction (x, y) 1,0=right; -1,0=left; 0,1=down; 0,-1=up

# Food / scoring
FOOD_SCORE = 1                    # Score per food eaten
FOOD_WALL_BUFFER = 1              # Tiles from wall edge where food CANNOT spawn (prevents wall spawn)

# Obstacles
ENABLE_OBSTACLES = True           # Turn obstacles on/off
OBSTACLE_COUNT = 5               # Number of randomly placed obstacles

# pygame key constants
KEY_UP = pygame.K_w
KEY_DOWN = pygame.K_s
KEY_LEFT = pygame.K_a
KEY_RIGHT = pygame.K_d
KEY_PAUSE = pygame.K_p #pause
KEY_RESTART = pygame.K_r #reset

#uncomment for arrow keys instead
#KEY_UP = pygame.K_UP
#KEY_DOWN = pygame.K_DOWN
#KEY_LEFT = pygame.K_LEFT
#KEY_RIGHT = pygame.K_RIGHT

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)
GREY = (80, 80, 80)
PAUSE_BLUE = (0, 100, 255, 128)   # Semi-transparent for pause overlay

# === END OF CONFIGURATION ===

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("consolas", size, True)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surf, text_rect)

def random_grid_position(exclude=None, min_x=0, max_x=None, min_y=0, max_y=None):
    cols = WIDTH // TILE_SIZE
    rows = HEIGHT // TILE_SIZE
    max_x = max_x or cols
    max_y = max_y or rows
    
    while True:
        pos = [random.randint(min_x, max_x - 1), random.randint(min_y, max_y - 1)]
        if not exclude or tuple(pos) not in exclude:
            return pos

def create_initial_snake():
    cols = WIDTH // TILE_SIZE
    rows = HEIGHT // TILE_SIZE
    start_x = cols // 2
    start_y = rows // 2
    snake = []
    dx, dy = START_DIRECTION
    for i in range(INITIAL_SNAKE_LENGTH):
        snake.append([start_x - i * dx, start_y - i * dy])
    return snake

def create_obstacles(snake, food, count):
    cols = WIDTH // TILE_SIZE
    rows = HEIGHT // TILE_SIZE
    occupied = {tuple(seg) for seg in snake}
    occupied.add(tuple(food))
    
    obstacles = set()
    for _ in range(count):
        pos = random_grid_position(exclude=occupied | obstacles)
        obstacles.add(tuple(pos))
    return obstacles

# MAIN

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake-ish")
    clock = pygame.time.Clock()

    snake = None
    direction = None
    food = None
    score = 0
    fps = INITIAL_FPS
    game_over = False
    obstacles = set()
    paused = False

    def reset_game():
        nonlocal snake, direction, food, score, fps, game_over, obstacles, paused
        snake = create_initial_snake()
        direction = START_DIRECTION[:]
        food = random_grid_position(exclude={tuple(seg) for seg in snake})
        score = 0
        fps = INITIAL_FPS
        game_over = False
        paused = False
        if ENABLE_OBSTACLES:
            obstacles = create_obstacles(snake, food, OBSTACLE_COUNT)
        else:
            obstacles = set()

    # Init
    reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if event.key == KEY_PAUSE:
                    paused = not paused
                elif event.key == KEY_RESTART:
                    reset_game()
                elif not game_over and not paused:
                    if event.key == KEY_UP and direction != [0, 1]:
                        direction = [0, -1]
                    elif event.key == KEY_DOWN and direction != [0, -1]:
                        direction = [0, 1]
                    elif event.key == KEY_LEFT and direction != [1, 0]:
                        direction = [-1, 0]
                    elif event.key == KEY_RIGHT and direction != [-1, 0]:
                        direction = [1, 0]

        if game_over or paused:
            pass
        else:
            head_x, head_y = snake[0]
            new_head = [head_x + direction[0], head_y + direction[1]]

            cols = WIDTH // TILE_SIZE
            rows = HEIGHT // TILE_SIZE

            if WRAP_AROUND_WALLS:
                new_head[0] %= cols
                new_head[1] %= rows
            else:
                if (new_head[0] < 0 or
                    new_head[0] >= cols or
                    new_head[1] < 0 or
                    new_head[1] >= rows):
                    game_over = True

            if not game_over and new_head in snake:
                game_over = True

            if not game_over and tuple(new_head) in obstacles:
                game_over = True

            if not game_over:
                snake.insert(0, new_head)

                if new_head == food:
                    score += FOOD_SCORE
                    buffer = FOOD_WALL_BUFFER
                    excluded = {tuple(seg) for seg in snake} | obstacles
                    food = random_grid_position(
                        exclude=excluded,
                        min_x=buffer,
                        max_x=cols - buffer,
                        min_y=buffer,
                        max_y=rows - buffer
                    )
                    if SPEED_INCREMENT_ON_FOOD:
                        fps += FPS_STEP
                else:
                    snake.pop()

        screen.fill(BLACK)

        for ox, oy in obstacles:
            x, y = ox * TILE_SIZE, oy * TILE_SIZE
            pygame.draw.rect(screen, GREY, (x, y, TILE_SIZE, TILE_SIZE))
            # Im a tranny femboy ^w^

        for idx, segment in enumerate(snake):
            x, y = segment[0] * TILE_SIZE, segment[1] * TILE_SIZE
            color = DARK_GREEN if idx == 0 else GREEN
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

        fx, fy = food[0] * TILE_SIZE, food[1] * TILE_SIZE
        pygame.draw.rect(screen, RED, (fx, fy, TILE_SIZE, TILE_SIZE))

        draw_text(screen, f"Score: {score}", 20, WHITE, 5, 5)
        draw_text(
            screen,
            f"FPS: {fps:.1f}  Obstacles: {'ON' if ENABLE_OBSTACLES else 'OFF'}",
            16,
            WHITE,
            5,
            25,
        )
        if WRAP_AROUND_WALLS:
            draw_text(screen, "Wrap: ON", 16, WHITE, 5, 45)
        else:
            draw_text(screen, "Wrap: OFF", 16, WHITE, 5, 45)

        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(PAUSE_BLUE)
            screen.blit(overlay, (0, 0))
            draw_text(screen, "PAUSED (P to toggle)", 28, WHITE, 150, HEIGHT // 2)

        if game_over:
            draw_text(screen, "GAME OVER - R to restart", 24, RED, 80, HEIGHT // 2 - 20)

        pygame.display.flip()
        clock.tick(fps)

if __name__ == "__main__":
    main()
