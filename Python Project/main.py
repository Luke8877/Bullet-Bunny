import pygame 
import sys  
import random
import os  

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Game")

# Define color constants
Black = (0, 0, 0)
White = (255, 255, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
Yellow = (255, 255, 0)

# Define fonts for various text elements
font = pygame.font.Font(None, 74)  
small_font = pygame.font.Font(None, 50) 
tiny_font = pygame.font.Font(None, 30)  

# Global Variables for game state
wave = 1
score = 0
high_score = 0
bullets = []
enemies = []
pause_cooldown = 0
game_over = False
instructions = False
menu = True
running = True
paused = False


def load_high_score():
    """Load the high score from a file."""
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            try:
                return int(file.read().strip())
            except ValueError:
                return 0
    return 0


def save_high_score(score):
    """Save the high score to a file."""
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))


# SpriteSheet class to handle sprite sheet animations
class SpriteSheet:
    def __init__(self, file_path, frame_width, frame_height):
        self.sheet = pygame.image.load(file_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.columns = self.sheet.get_width() // frame_width
        self.rows = self.sheet.get_height() // frame_height
        self.frames = [
            self.sheet.subsurface(pygame.Rect(x * frame_width, y * frame_height, frame_width, frame_height))
            for y in range(self.rows)
            for x in range(self.columns)
        ]

# Player class to handle player properties and behaviours 
class Player:
    def __init__(self, x, y, sprite_sheet):
        """Initialize the player with position, sprite sheet and attributes."""
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.sprite_sheet = sprite_sheet
        self.current_frame = 0
        self.frame_timer = 0
        self.speed = 300

    def draw(self, screen):
        """Draw the current frame of the player's sprite on the screen."""
        screen.blit(self.sprite_sheet.frames[self.current_frame], (self.x, self.y))

    def move(self, keys, screen_width, dt):
        """Handle player movement and animation based on input."""
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
        self.x = max(0, min(self.x, screen_width - self.width))

        # Update animation frame
        self.frame_timer += dt
        if self.frame_timer >= 0.1:  # Switch frame every 0.1 seconds
            self.current_frame = (self.current_frame + 1) % len(self.sprite_sheet.frames)
            self.frame_timer = 0

# Enemy class to handle enemy properties and behaviors
class Enemy:
    """Initialize the enemy with position, sprite sheet, and attributes."""
    def __init__(self, x, y, sprite_sheet):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 80
        self.sprite_sheet = sprite_sheet
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = 0.15
        self.speed = 100

    def draw(self, screen):
        """Draw the current frame of the enemy's sprite on the screen."""
        screen.blit(self.sprite_sheet.frames[self.current_frame], (self.x, self.y))

    def move(self, dt):
        """Update enemy position and handle animation."""
        self.y += self.speed * dt
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.sprite_sheet.frames)
            self.frame_timer = 0

# Bullet class to handle bullets fired by the player 
class Bullet:
    """Initialize the bullet with position and attributes."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 10
        self.color = Yellow
        self.speed = 500

    def draw(self, screen):
        """Draw the bullet on the screen."""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def move(self, dt):
        """Update the position of the bullet."""
        self.y -= self.speed * dt

# Function to initialize enemies for a wave
def initialize_enemies(sprite_sheet):
    """Generate a list of enemies based on the current wave."""
    global wave
    enemies = []
    num_enemies = 5 + wave
    speed_multiplier = 1 + (wave - 1) * 0.1

    for _ in range(num_enemies):
        x = random.randint(0, WIDTH - 120)
        y = random.randint(-200, -50)
        enemy = Enemy(x, y, sprite_sheet)
        enemy.speed *= speed_multiplier
        enemies.append(enemy)

    return enemies

# Function to reset the game state
def reset_game():
    """Reset the game variables and restart the game."""
    global wave, score, bullets, enemies, game_over
    wave = 1
    score = 0
    bullets = []
    enemies = initialize_enemies(enemy_sprite_sheet)
    game_over = False

# Function to handle user input events 
def handle_events():
    """Process player input and manage game state transitions."""
    global running, paused, instructions, menu, bullets
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if instructions:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                instructions = False
            continue

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and pause_cooldown <= 0:
                paused = not paused

        if menu and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            buttons = draw_menu()
            if buttons["Start"].collidepoint(mouse_pos):
                menu = False
                reset_game()
            elif buttons["Instructions"].collidepoint(mouse_pos):
                instructions = True
            elif buttons["Quit"].collidepoint(mouse_pos):
                running = False

        if event.type == pygame.KEYDOWN and not menu:
            if event.key == pygame.K_SPACE:
                bullet = Bullet(player.x + player.width // 2 - 2, player.y)
                bullets.append(bullet)

# Function execute core gameplay logic
def run_gameplay(dt):
    """Execute the gameplay loop, including movement, drawing and collision detection."""
    global wave, game_over, score, high_score
    keys = pygame.key.get_pressed()
    player.move(keys, WIDTH, dt)
    screen.fill(Black)
    player.draw(screen)

    # Update and draw bullets
    for bullet in bullets[:]:
        bullet.move(dt)
        if bullet.y < 0:
            bullets.remove(bullet)
        else:
            bullet.draw(screen)

    # Update and draw enemies
    for enemy in enemies:
        enemy.move(dt)
        enemy.draw(screen)

    # Check if all enemies are cleared
    if not enemies:
        wave += 1
        enemies.extend(initialize_enemies(enemy_sprite_sheet))

    # Check collisions
    for enemy in enemies[:]:
        enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        if enemy.y + enemy.height >= HEIGHT or enemy_rect.colliderect(player_rect):
            game_over = True

        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
            if bullet_rect.colliderect(enemy_rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                if score > high_score:
                    high_score = score

    display_score()

# Function to display score, wave, and high score
def display_score():
    """Render the score, wave and high score on the screen."""
    score_text = tiny_font.render(f"Score: {score}", True, White)
    wave_text = tiny_font.render(f"Wave: {wave}", True, White)
    high_score_text = tiny_font.render(f"High Score: {high_score}", True, White)
    screen.blit(score_text, (10, 10))
    screen.blit(wave_text, (10, 50))
    screen.blit(high_score_text, (10, 90))

# Function to draw the menu
def draw_menu():
    """Display the main menu."""
    screen.fill(Black)  # Clear the screen

    # Title
    title = font.render("BULLET BUNNY", True, White)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    # Buttons
    start_button = small_font.render("START GAME", True, Green)
    instructions_button = small_font.render("INSTRUCTIONS", True, White)
    quit_button = small_font.render("QUIT", True, Red)

    # Draw buttons and center
    screen.blit(start_button, (WIDTH // 2 - start_button.get_width() // 2, 250))
    screen.blit(instructions_button, (WIDTH // 2 - instructions_button.get_width() // 2, 350))
    screen.blit(quit_button, (WIDTH // 2 - quit_button.get_width() // 2, 450))

    return {
        "Start": pygame.Rect(WIDTH // 2 - start_button.get_width() // 2, 250, start_button.get_width(), start_button.get_height()),
        "Instructions": pygame.Rect(WIDTH // 2 - instructions_button.get_width() // 2, 350, instructions_button.get_width(), instructions_button.get_height()),
        "Quit": pygame.Rect(WIDTH // 2 - quit_button.get_width() // 2, 450, quit_button.get_width(), quit_button.get_height()),
    }


def draw_instructions():
    """Display the instructions screen."""
    screen.fill(Black)  # Clear the screen

    # Instructions title
    title = font.render("Instructions", True, White)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    # Add instructions text
    instructions_text = [
        "Use LEFT/RIGHT arrow keys or A/D to move.",
        "Press SPACEBAR to shoot bullets.",
        "Avoid enemies reaching the bottom.",
        "Defeat all enemies to advance waves.",
        "Press ESC to pause the game.",
    ]

    # Render and display each instruction line
    for i, line in enumerate(instructions_text):
        line_text = tiny_font.render(line, True, White)
        screen.blit(line_text, (WIDTH // 2 - line_text.get_width() // 2, 200 + i * 50))

    # Add a "Back" button to return to the menu
    back_button = small_font.render("Press ESC to Return", True, Green)
    screen.blit(back_button, (WIDTH // 2 - back_button.get_width() // 2, HEIGHT - 100))

def draw_pause_menu():
    """Display the pause menu."""
    screen.fill(Black)  
    pause_text = font.render("PAUSED", True, White)
    resume_text = small_font.render("Press ESC to Resume", True, White)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 3))
    screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2))

def game_over_screen():
    """Display the game-over screen and wait for user input."""
    screen.fill(Black)  
    game_over_text = font.render("GAME OVER", True, Red)
    restart_text = small_font.render("CLICK TO RESTART", True, White)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 300))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 400))
    pygame.display.flip()  

    save_high_score(high_score)
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Wait for mouse click
                waiting = False



# Load sprite sheets
player_sprite_sheet = SpriteSheet("Assets/Images/BunnyWalk-Sheet.png", 32, 32)
enemy_sprite_sheet = SpriteSheet("Assets/Images/_AttackCombo.png", 120, 80)
HIGH_SCORE_FILE = "Data/high_score.txt"

# Initialize player and high score
player = Player(WIDTH // 2 - 25, HEIGHT - 100, player_sprite_sheet)
high_score = load_high_score()


# Main game loop
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60) / 1000
    if pause_cooldown > 0:
        pause_cooldown -= dt

    handle_events()

    if instructions:
        draw_instructions()
        pygame.display.flip()
        continue

    if paused:
        draw_pause_menu()
        pygame.display.flip()
        continue

    if menu:
        draw_menu()
    elif game_over:
        game_over_screen()
        menu = True  
        game_over = False  
    else:
        run_gameplay(dt)

    pygame.display.flip()

pygame.quit()
sys.exit()
