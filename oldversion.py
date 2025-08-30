import pygame
import random
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 50
GRAVITY = 0.5
FLAP_STRENGTH = -10
PIPE_SPEED = 3
PIPE_GAP = 150

WHITE = (255, 255, 255)
BLUE = (0, 180, 255)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)

bird = pygame.Rect(50, HEIGHT//2, 30, 30)
bird_velocity = 0

pipes = []
score = 0

def create_pipe():
    height = random.randint(100, 400)
    top = pygame.Rect(WIDTH, 0, 50, height)
    bottom = pygame.Rect(WIDTH, height + PIPE_GAP, 50, HEIGHT - height - PIPE_GAP)
    return top, bottom

def move_pipes(pipes):
    for pipe in pipes:
        pipe.x -= PIPE_SPEED
    return [pipe for pipe in pipes if pipe.x + pipe.width > 0]

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, pipe)

def check_collision(bird, pipes):
    for pipe in pipes: 
        if bird.colliderect(pipe):
            return True
    if bird.top <= 0 or bird.bottom >= HEIGHT:
        return True
    return False


running = True
frame_count = 0

while running:
    clock.tick(FPS)
    screen.fill(BLUE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_velocity = FLAP_STRENGTH

    # Bird movement
    bird_velocity += GRAVITY
    bird.y += int(bird_velocity)

    # Pipes management
    if frame_count % 90 == 0:
        pipes.extend(create_pipe())

    pipes = move_pipes(pipes)
    draw_pipes(pipes)

    # Score update
    for pipe in pipes:
        if pipe.x == bird.x:
            score += 0.5  # Add 0.5 twice (top and bottom) = 1 per pipe set

    # Draw bird
    pygame.draw.rect(screen, WHITE, bird)

    # Collision
    if check_collision(bird, pipes):
        print("Game Over! Score:", int(score))
        pygame.quit()
        sys.exit()

    # Draw score
    score_surface = font.render(f"Score: {int(score)}", True, WHITE)
    screen.blit(score_surface, (10, 10))

    pygame.display.flip()
    frame_count += 1