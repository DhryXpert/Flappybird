import pygame
import random
import sys
import os
import math
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
GRAVITY = 0.6
FLAP_STRENGTH = -12
PIPE_SPEED = 4
PIPE_GAP = 180
PIPE_FREQUENCY = 120  # frames between pipes
BIRD_SIZE = 25

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.rect = pygame.Rect(x, y, BIRD_SIZE, BIRD_SIZE)
        self.rotation = 0
        self.animation_frame = 0
        self.animation_speed = 0.2
        
    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Update rectangle position
        self.rect.y = self.y
        
        # Update rotation based on velocity
        self.rotation = max(-30, min(90, self.velocity * 3))
        
        # Update animation frame
        self.animation_frame += self.animation_speed
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def draw(self, screen):
        # Create bird surface with rotation
        bird_surface = pygame.Surface((BIRD_SIZE, BIRD_SIZE), pygame.SRCALPHA)
        
        # Draw bird body (circle)
        pygame.draw.circle(bird_surface, YELLOW, (BIRD_SIZE//2, BIRD_SIZE//2), BIRD_SIZE//2)
        
        # Draw bird eye
        pygame.draw.circle(bird_surface, BLACK, (BIRD_SIZE//2 + 5, BIRD_SIZE//2 - 5), 3)
        
        # Draw bird wing (animated)
        wing_offset = int(3 * abs(math.sin(self.animation_frame)))
        pygame.draw.ellipse(bird_surface, WHITE, (5, BIRD_SIZE//2 - wing_offset, 8, 6))
        
        # Draw bird beak
        pygame.draw.polygon(bird_surface, RED, [(BIRD_SIZE, BIRD_SIZE//2), (BIRD_SIZE - 8, BIRD_SIZE//2 - 3), (BIRD_SIZE - 8, BIRD_SIZE//2 + 3)])
        
        # Rotate and draw
        rotated_surface = pygame.transform.rotate(bird_surface, self.rotation)
        screen.blit(rotated_surface, (self.x - rotated_surface.get_width()//2 + BIRD_SIZE//2, self.y - rotated_surface.get_height()//2 + BIRD_SIZE//2))

class Pipe:
    def __init__(self, x, height):
        self.x = x
        self.height = height
        self.top_rect = pygame.Rect(x, 0, 60, height)
        self.bottom_rect = pygame.Rect(x, height + PIPE_GAP, 60, HEIGHT - height - PIPE_GAP)
        self.passed = False
        
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
        
    def draw(self, screen):
        # Draw pipe body
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        
        # Draw pipe caps
        cap_width = 80
        cap_height = 20
        pygame.draw.rect(screen, (0, 100, 0), (self.x - 10, self.height - cap_height, cap_width, cap_height))
        pygame.draw.rect(screen, (0, 100, 0), (self.x - 10, self.height + PIPE_GAP, cap_width, cap_height))
        
    def is_off_screen(self):
        return self.x + 60 < 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird - College Project")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 32)
        self.font_small = pygame.font.SysFont("Arial", 24)
        
        self.state = MENU
        self.reset_game()
        self.load_sounds()
        
    def load_sounds(self):
        # Create simple sound effects using pygame's built-in sound generation
        self.flap_sound = self.generate_beep(800, 100)
        self.score_sound = self.generate_beep(1000, 150)
        self.death_sound = self.generate_beep(200, 300)
        


    def generate_beep(self, frequency, duration):
        sample_rate = 22050
        samples = int(duration * sample_rate / 1000)

        # Generate sine wave
        t = np.linspace(0, duration / 1000, samples, False)
        waveform = 32767 * np.sin(2 * np.pi * frequency * t)

        # Convert to 16-bit signed integers
        waveform = waveform.astype(np.int16)

        # Convert to stereo by duplicating the channel
        stereo_waveform = np.column_stack((waveform, waveform))

        return pygame.sndarray.make_sound(stereo_waveform)

        
    def reset_game(self):
        self.bird = Bird(100, HEIGHT // 2)
        self.pipes = []
        self.score = 0
        self.high_score = self.load_high_score()
        self.frame_count = 0
        self.game_speed = 1.0
        
    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0
            
    def save_high_score(self):
        try:
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
            
    def create_pipe(self):
        height = random.randint(100, HEIGHT - 200)
        return Pipe(WIDTH, height)
        
    def update(self):
        if self.state == PLAYING:
            # Bird update
            self.bird.update()
            
            # Create new pipes
            if self.frame_count % PIPE_FREQUENCY == 0:
                self.pipes.append(self.create_pipe())
                
            # Update pipes
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.is_off_screen():
                    self.pipes.remove(pipe)
                    
            # Score update
            for pipe in self.pipes:
                if not pipe.passed and pipe.x + 60 < self.bird.x:
                    pipe.passed = True
                    self.score += 1
                    self.score_sound.play()
                    
            # Collision detection
            if self.check_collision():
                self.state = GAME_OVER
                self.death_sound.play()
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                    
            # Increase game speed gradually
            if self.score > 0 and self.score % 5 == 0:
                self.game_speed = min(2.0, 1.0 + self.score * 0.1)
                
            self.frame_count += 1
            
    def check_collision(self):
        # Check wall collision
        if self.bird.y <= 0 or self.bird.y + BIRD_SIZE >= HEIGHT:
            return True
            
        # Check pipe collision
        for pipe in self.pipes:
            if (self.bird.rect.colliderect(pipe.top_rect) or 
                self.bird.rect.colliderect(pipe.bottom_rect)):
                return True
                
        return False
        
    def draw(self):
        # Draw background
        self.screen.fill(BLUE)
        
        # Draw clouds (simple decoration)
        self.draw_clouds()
        
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game_over()
        elif self.state == PAUSED:
            self.draw_paused()
            
        pygame.display.flip()
        
    def draw_clouds(self):
        # Simple cloud decoration
        for i in range(3):
            x = (pygame.time.get_ticks() // 50 + i * 300) % (WIDTH + 100)
            y = 50 + i * 30
            pygame.draw.circle(self.screen, WHITE, (x, y), 20)
            pygame.draw.circle(self.screen, WHITE, (x + 20, y), 25)
            pygame.draw.circle(self.screen, WHITE, (x + 40, y), 20)
            
    def draw_menu(self):
        # Title
        title = self.font_large.render("FLAPPY BIRD", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "Press SPACE to start",
            "Press SPACE to flap",
            "Press P to pause",
            "Press R to restart",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + i * 30))
            self.screen.blit(text, text_rect)
            
        # High score
        if self.high_score > 0:
            high_score_text = self.font_medium.render(f"High Score: {self.high_score}", True, YELLOW)
            high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT * 3//4))
            self.screen.blit(high_score_text, high_score_rect)
            
    def draw_game(self):
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
            
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw speed indicator
        speed_text = self.font_small.render(f"Speed: {self.game_speed:.1f}x", True, WHITE)
        self.screen.blit(speed_text, (10, 50))
        
    def draw_game_over(self):
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # High score
        if self.score == self.high_score:
            new_record_text = self.font_medium.render("NEW RECORD!", True, YELLOW)
            new_record_rect = new_record_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            self.screen.blit(new_record_text, new_record_rect)
        else:
            high_score_text = self.font_medium.render(f"High Score: {self.high_score}", True, YELLOW)
            high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            self.screen.blit(high_score_text, high_score_rect)
            
        # Instructions
        restart_text = self.font_small.render("Press R to restart or SPACE for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT * 3//4))
        self.screen.blit(restart_text, restart_rect)
        
    def draw_paused(self):
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        resume_text = self.font_small.render("Press P to resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        self.screen.blit(resume_text, resume_rect)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                if self.state == MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = PLAYING
                        
                elif self.state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.bird.flap()
                        self.flap_sound.play()
                    elif event.key == pygame.K_p:
                        self.state = PAUSED
                        
                elif self.state == PAUSED:
                    if event.key == pygame.K_p:
                        self.state = PLAYING
                        
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = PLAYING
                    elif event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = MENU
                        
        return True
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Main game loop
if __name__ == "__main__":
    game = Game()
    game.run()
