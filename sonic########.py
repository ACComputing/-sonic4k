import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60
TILE_SIZE = 32
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_POWER = -12
FRICTION = 0.8

# Colors (used for drawing)
SKY_TOP = (100, 200, 255)
SKY_BOTTOM = (200, 230, 255)
GROUND_COLOR = (34, 139, 34)
GROUND_STRIPE = (85, 107, 47)
RING_MAIN = (255, 255, 0)
RING_HOLE = (50, 50, 50)
SONIC_BLUE = (66, 170, 255)
SONIC_SKIN = (255, 220, 150)
SONIC_RED = (220, 20, 20)
SONIC_WHITE = (255, 255, 255)
SONIC_BLACK = (0, 0, 0)
MENU_BG = (30, 30, 60)
TEXT_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 255, 0)

# Game states
MENU = 0
PLAYING = 1

# ----------------------------------------------------------------------
# Simple tile map for Green Hill Zone (0 = empty, 1 = solid ground)
level_map = [
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "11111111111111111111111111111111111111111111111111111111111111111111111111111111",
]

# Add some floating platforms
level_map[7] = "00000000000000000000000000000000000000000000000000011111000000000000000000000000"
level_map[5] = "00000000000000000000000000000000000000000000000011100011110000000000000000000000"
level_map[3] = "00000000000000000000000000000000000000000000001110000000001110000000000000000000"

# ----------------------------------------------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True

    def update(self, tiles, rings):
        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vx = PLAYER_SPEED
            self.facing_right = True
        else:
            self.vx *= FRICTION

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_POWER
            self.on_ground = False

        # Gravity
        self.vy += GRAVITY
        if self.vy > 15:
            self.vy = 15

        # Move horizontally and check collisions
        self.rect.x += self.vx
        self.collide(self.vx, 0, tiles)

        # Move vertically and check collisions
        self.rect.y += self.vy
        self.on_ground = False
        self.collide(0, self.vy, tiles)

        # Collect rings
        collected = []
        for ring in rings:
            if self.rect.colliderect(ring.rect):
                collected.append(ring)
        for ring in collected:
            rings.remove(ring)

    def collide(self, dx, dy, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if dx > 0:
                    self.rect.right = tile.rect.left
                if dx < 0:
                    self.rect.left = tile.rect.right
                if dy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = tile.rect.bottom
                    self.vy = 0

    def draw(self, screen, camera_x):
        """Draw Sonic in Sonic Advance style using primitive shapes."""
        # Calculate on-screen position
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y

        # --- Body (blue rounded shape) ---
        # Use an ellipse for a more character-like body
        body_rect = pygame.Rect(screen_x + 4, screen_y + 4, TILE_SIZE - 8, TILE_SIZE - 6)
        pygame.draw.ellipse(screen, SONIC_BLUE, body_rect)

        # --- Muzzle / Tummy (peach) ---
        if self.facing_right:
            muzzle_rect = pygame.Rect(screen_x + 12, screen_y + 12, 12, 10)
        else:
            muzzle_rect = pygame.Rect(screen_x + 8, screen_y + 12, 12, 10)
        pygame.draw.ellipse(screen, SONIC_SKIN, muzzle_rect)

        # --- Eyes ---
        # Eye whites (larger, more expressive)
        eye_y = screen_y + 10
        if self.facing_right:
            left_eye_center = (screen_x + 12, eye_y)
            right_eye_center = (screen_x + 22, eye_y)
        else:
            left_eye_center = (screen_x + 10, eye_y)
            right_eye_center = (screen_x + 20, eye_y)

        pygame.draw.circle(screen, SONIC_WHITE, left_eye_center, 5)
        pygame.draw.circle(screen, SONIC_WHITE, right_eye_center, 5)

        # Pupils (black) – offset slightly based on facing
        pupil_offset = 2 if self.facing_right else -2
        pygame.draw.circle(screen, SONIC_BLACK, (left_eye_center[0] + pupil_offset, left_eye_center[1]), 2)
        pygame.draw.circle(screen, SONIC_BLACK, (right_eye_center[0] + pupil_offset, right_eye_center[1]), 2)

        # Eye highlights (tiny white dots)
        highlight_offset = pupil_offset + 1
        pygame.draw.circle(screen, SONIC_WHITE, (left_eye_center[0] + highlight_offset, left_eye_center[1] - 1), 1)
        pygame.draw.circle(screen, SONIC_WHITE, (right_eye_center[0] + highlight_offset, right_eye_center[1] - 1), 1)

        # --- Quills (spikes on head) ---
        # Use polygons for the three main quills
        spike_color = (40, 40, 140)  # darker blue
        if self.facing_right:
            # Quill 1 (back)
            pts1 = [(screen_x + 4, screen_y + 4), (screen_x + 12, screen_y - 6), (screen_x + 18, screen_y + 2)]
            # Quill 2 (middle)
            pts2 = [(screen_x + 12, screen_y + 2), (screen_x + 20, screen_y - 8), (screen_x + 24, screen_y + 2)]
            # Quill 3 (front)
            pts3 = [(screen_x + 20, screen_y + 2), (screen_x + 28, screen_y - 4), (screen_x + 30, screen_y + 4)]
        else:
            # Mirror for left-facing
            pts1 = [(screen_x + 28, screen_y + 4), (screen_x + 20, screen_y - 6), (screen_x + 14, screen_y + 2)]
            pts2 = [(screen_x + 20, screen_y + 2), (screen_x + 12, screen_y - 8), (screen_x + 8, screen_y + 2)]
            pts3 = [(screen_x + 12, screen_y + 2), (screen_x + 4, screen_y - 4), (screen_x + 2, screen_y + 4)]

        pygame.draw.polygon(screen, spike_color, pts1)
        pygame.draw.polygon(screen, spike_color, pts2)
        pygame.draw.polygon(screen, spike_color, pts3)

        # --- Shoes (red) ---
        shoe_width = 10
        shoe_height = 6
        shoe_y = screen_y + TILE_SIZE - shoe_height - 2
        if self.facing_right:
            left_shoe = pygame.Rect(screen_x + 4, shoe_y, shoe_width, shoe_height)
            right_shoe = pygame.Rect(screen_x + 18, shoe_y, shoe_width, shoe_height)
        else:
            left_shoe = pygame.Rect(screen_x + 8, shoe_y, shoe_width, shoe_height)
            right_shoe = pygame.Rect(screen_x + 22, shoe_y, shoe_width, shoe_height)

        pygame.draw.rect(screen, SONIC_RED, left_shoe)
        pygame.draw.rect(screen, SONIC_RED, right_shoe)

        # Shoe stripes (white)
        stripe_y = shoe_y + 2
        if self.facing_right:
            pygame.draw.line(screen, SONIC_WHITE, (screen_x + 8, stripe_y), (screen_x + 12, stripe_y), 2)
            pygame.draw.line(screen, SONIC_WHITE, (screen_x + 22, stripe_y), (screen_x + 26, stripe_y), 2)
        else:
            pygame.draw.line(screen, SONIC_WHITE, (screen_x + 12, stripe_y), (screen_x + 16, stripe_y), 2)
            pygame.draw.line(screen, SONIC_WHITE, (screen_x + 26, stripe_y), (screen_x + 30, stripe_y), 2)

# ----------------------------------------------------------------------
class Tile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw(self, screen, camera_x):
        screen_rect = self.rect.copy()
        screen_rect.x -= camera_x
        # Base grass
        pygame.draw.rect(screen, GROUND_COLOR, screen_rect)
        # Dark green stripe at bottom (like grass edge)
        stripe_rect = pygame.Rect(screen_rect.x, screen_rect.bottom-4, TILE_SIZE, 4)
        pygame.draw.rect(screen, GROUND_STRIPE, stripe_rect)
        # Little grass tufts (small arcs or lines)
        for i in range(3):
            x = screen_rect.x + i*8 + 2
            y = screen_rect.y
            pygame.draw.line(screen, (50, 150, 50), (x, y), (x+4, y-4), 2)

# ----------------------------------------------------------------------
class Ring:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE//2, TILE_SIZE//2)

    def draw(self, screen, camera_x):
        screen_rect = self.rect.copy()
        screen_rect.x -= camera_x
        center = screen_rect.center
        # Draw outer ring (yellow)
        pygame.draw.circle(screen, RING_MAIN, center, TILE_SIZE//4)
        # Draw inner hole (dark) to make it look like a ring
        pygame.draw.circle(screen, RING_HOLE, center, TILE_SIZE//6)

# ----------------------------------------------------------------------
def draw_sky(screen):
    """Gradient sky with clouds."""
    for y in range(SCREEN_HEIGHT):
        # Linear gradient from top to bottom
        ratio = y / SCREEN_HEIGHT
        r = int(SKY_TOP[0] * (1-ratio) + SKY_BOTTOM[0] * ratio)
        g = int(SKY_TOP[1] * (1-ratio) + SKY_BOTTOM[1] * ratio)
        b = int(SKY_TOP[2] * (1-ratio) + SKY_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    # Draw some clouds (random circles)
    cloud_color = (255, 255, 255, 180)
    # Use a fixed seed for consistent clouds every frame
    random.seed(42)
    for _ in range(8):
        x = (pygame.time.get_ticks() // 100 + random.randint(0, 600)) % 800 - 100
        y = random.randint(20, 150)
        pygame.draw.circle(screen, cloud_color, (x, y), 30)
        pygame.draw.circle(screen, cloud_color, (x+30, y-10), 25)
        pygame.draw.circle(screen, cloud_color, (x-20, y-5), 20)
    random.seed()

# ----------------------------------------------------------------------
def load_level(map_data):
    tiles = []
    rings = []
    for row_idx, row in enumerate(map_data):
        for col_idx, tile in enumerate(row):
            if tile == '1':
                tiles.append(Tile(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
            # Place some rings (you can define more positions)
            if (row_idx == 5 and col_idx == 40) or (row_idx == 3 and col_idx == 50) or (row_idx == 7 and col_idx == 55):
                rings.append(Ring(col_idx * TILE_SIZE, row_idx * TILE_SIZE - TILE_SIZE//2))
    return tiles, rings

# ----------------------------------------------------------------------
def main_menu(screen, clock):
    font = pygame.font.Font(None, 36)
    options = ["Start Game", "Quit"]
    selected = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return PLAYING
                    elif selected == 1:
                        pygame.quit()
                        sys.exit()

        screen.fill(MENU_BG)

        title = font.render("Sonic Advance (Green Hill Zone)", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title, title_rect)

        for i, opt in enumerate(options):
            color = SELECTED_COLOR if i == selected else TEXT_COLOR
            text = font.render(opt, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 200 + i*50))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

# ----------------------------------------------------------------------
def play_game(screen, clock):
    tiles, rings = load_level(level_map)
    player = Player(100, SCREEN_HEIGHT - 2*TILE_SIZE)

    camera_x = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MENU

        player.update(tiles, rings)

        # Camera follow (smooth)
        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_x += (target_x - camera_x) * 0.1
        max_camera_x = len(level_map[0]) * TILE_SIZE - SCREEN_WIDTH
        camera_x = max(0, min(camera_x, max_camera_x))

        # Draw everything
        draw_sky(screen)

        for tile in tiles:
            tile.draw(screen, camera_x)

        for ring in rings:
            ring.draw(screen, camera_x)

        player.draw(screen, camera_x)

        pygame.display.flip()
        clock.tick(FPS)

    return MENU

# ----------------------------------------------------------------------
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sonic Advance - Green Hill Zone (Vibe Coded)")
    clock = pygame.time.Clock()

    state = MENU

    while True:
        if state == MENU:
            state = main_menu(screen, clock)
        elif state == PLAYING:
            state = play_game(screen, clock)

if __name__ == "__main__":
    main()
