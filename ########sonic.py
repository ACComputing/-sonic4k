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
        # Make the hitbox slightly smaller than the tile for better feel
        self.rect = pygame.Rect(x, y, 28, 32)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True
        
        # Animation State
        self.state = 'idle'
        self.frame_index = 0
        self.anim_timer = 0
        self.animation_speed = 8 # Lower is faster
        
        # Generate sprites
        self.sprites = self._load_sprites()

    def _draw_pixel_art(self, surface, pattern, colors, offset=(0,0)):
        """Helper to draw pixel art from a string list."""
        x_off, y_off = offset
        for y, row in enumerate(pattern):
            for x, char in enumerate(row):
                if char != '.' and char in colors:
                    pygame.draw.rect(surface, colors[char], (x + x_off, y + y_off, 1, 1))

    def _load_sprites(self):
        """Generates a dictionary of sprite surfaces for different states."""
        sprites = {
            'idle': [],
            'run': [],
            'jump': []
        }
        
        # Palette Map for the generator
        # B: Blue, D: Dark Blue, S: Skin, R: Red, W: White, K: Black/Outline
        C = {
            'B': SONIC_BLUE, 'D': SONIC_DARK_BLUE, 'S': SONIC_SKIN,
            'R': SONIC_RED, 'W': SONIC_WHITE, 'K': SONIC_BLACK
        }

        # --- IDLE SPRITE (32x32) ---
        # Classic standing pose
        idle_pattern = [
            "...........DDDD............",
            "..........DDBBBD...........",
            ".........DDBBBBBD..........",
            "........DBBBBBBBBD.........",
            ".......DBBBBBBBBBBD........",
            "......DDDBBBBBBBBD.........",
            ".....DDDBBBBBBBBBD.........",
            "....DDDBBBBBBBBBBW.........",
            "...DDDBBBBWWSBBBWK.........",
            "..DDDBBBBWSSSWBBWK.........",
            "...DDBBBBWSSSWBWKK.........",
            "....DDDBBBWWSBBWDK.........",
            ".....DDBBBBBBBBBDK.........",
            "......DDDBBBBBDDDK.........",
            ".......DDDBBWDDDDK.........",
            "........DKKWWKDDDK.........",
            ".......DWWRWWRRDDK.........",
            ".......DWWRRWWRRDK.........",
            ".......DKRRWWRRRDK.........",
            "........DDDDDDDDDK.........",
            ".........DDDDDDDDDK........",
            "..........DDDDDDDDK........",
            "...........DDDDDDDK........",
            "............DDDDDDK........",
            ".............DDDDDK........",
            "..............DDDD.........",
        ]
        
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._draw_pixel_art(surf, idle_pattern, C, offset=(2, 4))
        sprites['idle'].append(surf)

        # --- RUN FRAMES (32x32) ---
        # Frame 1: Legs apart
        run1 = [
            "...........DDDD............",
            "..........DBBBBD...........",
            ".........DBBBBBBD..........",
            "........DBBBBBBBBD.........",
            ".......DBBBBBBBBBBD........",
            "......DDDBBBBBBBBD.........",
            ".....DDDBBBBBBBBBD.........",
            "....DDDBBBBBBBBW...........",
            "...DDDBBBBWWSBBWK..........",
            "..DDDBBBBWSSSWBWKK.........",
            "...DDBBBBWSSSWBWDK.........",
            "....DDDBBBWWSBBWDK.........",
            ".....DDBBBBBBBBBDK.........",
            "......DDDBBBBBDDDK.........",
            ".......DDDBBWDDDDK.........",
            "........DKKWWKDDDK.........",
            ".......DWWRRRWWDDK.........",
            ".......DKWRRRWW.K.........",
            "........DKRRWW...K.........",
            "........DDDDDDDDDK.........",
            ".........DDDDDDDDDK........",
            "..........DDDDDDDDK........",
            "...........DDDDDDDK........",
            "............DDDDDDK........",
            ".............DDDDDK........",
            "..............DDDD.........",
        ]
        surf1 = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._draw_pixel_art(surf1, run1, C, offset=(2, 4))
        sprites['run'].append(surf1)

        # Frame 2: Legs together (blur effect)
        run2 = [
            "...........DDDD............",
            "..........DBBBBD...........",
            ".........DBBBBBBD..........",
            "........DBBBBBBBBD.........",
            ".......DBBBBBBBBBBD........",
            "......DDDBBBBBBBBD.........",
            ".....DDDBBBBBBBBBD.........",
            "....DDDBBBBBBBBW...........",
            "...DDDBBBBWWSBBWK..........",
            "..DDDBBBBWSSSWBWKK.........",
            "...DDBBBBWSSSWBWDK.........",
            "....DDDBBBWWSBBWDK.........",
            ".....DDBBBBBBBBBDK.........",
            "......DDDBBBBBDDDK.........",
            ".......DDDBBWDDDDK.........",
            "........DKKWWKDDDK.........",
            ".......DWWRWWRRRDK.........",
            ".......DWWRRRWWWK.........",
            ".......DKRRWWWRRDK.........",
            "........DDDDDDDDDK.........",
            ".........DDDDDDDDDK........",
            "..........DKKKDDDDK........",
            "...........DKKDDDDK........",
            "............DKDDDDK........",
            ".............DDDDDK........",
            "..............DDDD.........",
        ]
        surf2 = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._draw_pixel_art(surf2, run2, C, offset=(2, 4))
        sprites['run'].append(surf2)

        # --- JUMP SPRITE (Ball) ---
        # Simplified spin ball
        jump_pattern = [
            "......DDDDDDDDDDDD......",
            "....DDBBBBBBBBBBBBBDD...",
            "..DBBBBBBBBBBBBBBBBBBD..",
            ".DBBBBBBBBBBBBBBBBBBBBD.",
            "DBBBBBBBBWWWWWWWWBBBBBBD",
            "DBBBBBBBWWSWWWSWWBBBBBBD",
            "DBBBBBBBWSSSWSSSWBBBBBBD",
            "DBBBBBBBWWSWWWSWWBBBBBBD",
            ".DBBBBBBBWWWWWWWWBBBBBD.",
            "..DBBBBBBBBBBBBBBBBBBD..",
            "....DDBBBBBBBBBBBBBDD...",
            "......DDDDDDDDDDDD......",
        ]
        surf_j = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._draw_pixel_art(surf_j, jump_pattern, C, offset=(3, 10))
        sprites['jump'].append(surf_j)

        return sprites

    def update(self, tiles, rings):
        # Horizontal movement
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_LEFT]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
            moving = True
        elif keys[pygame.K_RIGHT]:
            self.vx = PLAYER_SPEED
            self.facing_right = True
            moving = True
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

        # --- Animation Logic ---
        if not self.on_ground:
            self.state = 'jump'
        elif abs(self.vx) > 1.0:
            self.state = 'run'
        else:
            self.state = 'idle'

        # Update Animation Frame
        self.anim_timer += 1
        if self.anim_timer >= self.animation_speed:
            self.anim_timer = 0
            self.frame_index += 1
            
            # Loop frames based on state
            max_frames = len(self.sprites[self.state])
            if self.frame_index >= max_frames:
                self.frame_index = 0

        # Speed up animation if running fast
        if self.state == 'run':
            self.animation_speed = max(2, 8 - int(abs(self.vx)))
        else:
            self.animation_speed = 8

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
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y
        
        # Adjust draw position because the sprite is 32x32 but rect is smaller
        # Center the sprite horizontally over the rect
        draw_x = screen_x - (32 - self.rect.width) // 2
        draw_y = screen_y - (32 - self.rect.height) # Draw feet at bottom of rect

        # Get current frame
        frames = self.sprites[self.state]
        current_image = frames[self.frame_index % len(frames)]

        if self.facing_right:
            screen.blit(current_image, (draw_x, draw_y))
        else:
            # Flip horizontally if facing left
            flipped_asset = pygame.transform.flip(current_image, True, False)
            screen.blit(flipped_asset, (draw_x, draw_y))

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
    pygame.display.set_caption("Sonic CD - Green Hill Zone (Pixel Asset Demo)")
    clock = pygame.time.Clock()

    state = MENU

    while True:
        if state == MENU:
            state = main_menu(screen, clock)
        elif state == PLAYING:
            state = play_game(screen, clock)

if __name__ == "__main__":
    main()
