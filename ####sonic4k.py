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

# Colors
SKY_TOP = (100, 200, 255)
SKY_BOTTOM = (200, 230, 255)
GROUND_COLOR = (34, 139, 34)
GROUND_STRIPE = (85, 107, 47)
RING_MAIN = (255, 255, 0)
RING_HOLE = (50, 50, 50)

# Sonic CD Palette
SONIC_BLUE = (66, 170, 255)
SONIC_DARK_BLUE = (40, 100, 200)
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
# Simple tile map for Green Hill Zone
level_map = [
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000001110000000001110000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000011100011110000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000011111000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "11111111111111111111111111111111111111111111111111111111111111111111111111111111",
]

# ----------------------------------------------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True
        
        # --- CREATE THE 2D ASSET ---
        # We generate a Pygame Surface once. This acts as our "Sprite Asset".
        # This is much more efficient than drawing shapes every frame.
        self.asset = self._generate_sonic_asset()

    def _generate_sonic_asset(self):
        """Generates a Sonic CD style sprite surface."""
        # Create a transparent surface
        image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Coordinates are relative to the surface (0,0 to 32,32)
        
        # 1. Quills (Back ones first for layering)
        # Dark blue for depth
        # Points for the 3 iconic quills
        # Quill 1 (Bottom)
        pygame.draw.polygon(image, SONIC_DARK_BLUE, [(2, 20), (8, 0), (16, 16)])
        # Quill 2 (Middle)
        pygame.draw.polygon(image, SONIC_BLUE, [(10, 18), (18, -4), (26, 14)])
        # Quill 3 (Top)
        pygame.draw.polygon(image, SONIC_DARK_BLUE, [(18, 16), (26, -2), (32, 10)])

        # 2. Body (Blue)
        pygame.draw.ellipse(image, SONIC_BLUE, (6, 8, 20, 18))
        
        # 3. Muzzle (Skin) - Sonic CD has a distinct rounded muzzle
        pygame.draw.ellipse(image, SONIC_SKIN, (10, 14, 14, 12))
        # Hide the top part of muzzle to merge with face
        pygame.draw.rect(image, SONIC_BLUE, (10, 14, 14, 4))

        # 4. Eyes
        # Large connected eyes style
        # Left Eye White
        pygame.draw.ellipse(image, SONIC_WHITE, (8, 6, 12, 10))
        # Right Eye White
        pygame.draw.ellipse(image, SONIC_WHITE, (16, 6, 12, 10))
        
        # Pupils (Looking forward/right)
        pygame.draw.circle(image, SONIC_BLACK, (18, 10), 3)
        pygame.draw.circle(image, SONIC_BLACK, (26, 10), 3)
        
        # Eye highlights (tiny white pixels for life)
        pygame.draw.circle(image, SONIC_WHITE, (19, 9), 1)
        pygame.draw.circle(image, SONIC_WHITE, (27, 9), 1)

        # 5. Nose
        pygame.draw.ellipse(image, SONIC_SKIN, (24, 10, 6, 6))
        
        # 6. Ears
        pygame.draw.polygon(image, SONIC_BLUE, [(4, 4), (10, 2), (8, 10)])
        pygame.draw.polygon(image, SONIC_SKIN, [(6, 5), (9, 4), (8, 8)])

        # 7. Belly (Peach area on body)
        pygame.draw.ellipse(image, SONIC_SKIN, (10, 18, 10, 8))

        # 8. Shoes (Sonic CD style: streamlined red shoes with white stripes)
        # Back Shoe
        pygame.draw.ellipse(image, SONIC_RED, (4, 26, 10, 6))
        # Front Shoe
        pygame.draw.ellipse(image, SONIC_RED, (18, 26, 12, 6))
        
        # White Stripes on shoes
        pygame.draw.line(image, SONIC_WHITE, (6, 28), (10, 30), 2)
        pygame.draw.line(image, SONIC_WHITE, (20, 28), (26, 30), 2)
        
        # 9. Socks/Ankles (White cuffs)
        pygame.draw.rect(image, SONIC_WHITE, (5, 24, 8, 3))
        pygame.draw.rect(image, SONIC_WHITE, (19, 24, 10, 3))

        return image

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
        """Draw the pre-rendered asset."""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y

        # Blit the asset
        if self.facing_right:
            screen.blit(self.asset, (screen_x, screen_y))
        else:
            # Flip horizontally if facing left
            flipped_asset = pygame.transform.flip(self.asset, True, False)
            screen.blit(flipped_asset, (screen_x, screen_y))

# ----------------------------------------------------------------------
class Tile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw(self, screen, camera_x):
        screen_rect = self.rect.copy()
        screen_rect.x -= camera_x
        pygame.draw.rect(screen, GROUND_COLOR, screen_rect)
        stripe_rect = pygame.Rect(screen_rect.x, screen_rect.bottom-4, TILE_SIZE, 4)
        pygame.draw.rect(screen, GROUND_STRIPE, stripe_rect)
        # Grass tufts
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
        pygame.draw.circle(screen, RING_MAIN, center, TILE_SIZE//4)
        pygame.draw.circle(screen, RING_HOLE, center, TILE_SIZE//6)

# ----------------------------------------------------------------------
def draw_sky(screen):
    """Gradient sky with clouds."""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(SKY_TOP[0] * (1-ratio) + SKY_BOTTOM[0] * ratio)
        g = int(SKY_TOP[1] * (1-ratio) + SKY_BOTTOM[1] * ratio)
        b = int(SKY_TOP[2] * (1-ratio) + SKY_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    # Draw some clouds
    cloud_color = (255, 255, 255, 180)
    random.seed(42) # Consistent clouds
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
            # Place rings on specific tiles (just examples)
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

        title = font.render("Sonic CD - Green Hill Zone", True, TEXT_COLOR)
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
    pygame.display.set_caption("Sonic CD - Green Hill Zone (2D Asset Demo)")
    clock = pygame.time.Clock()

    state = MENU

    while True:
        if state == MENU:
            state = main_menu(screen, clock)
        elif state == PLAYING:
            state = play_game(screen, clock)

if __name__ == "__main__":
    main()
