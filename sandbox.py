import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Scanline Effect")

# Create the scanline surface once
scanline_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
scanline_surface.fill((0, 0, 0, 0)) # Start fully transparent

# Draw semi-transparent black lines
for y in range(0, SCREEN_HEIGHT, 2): # Draw a line every 2 pixels
    pygame.draw.line(scanline_surface, (0, 0, 0, 100), (0, y), (SCREEN_WIDTH, y))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((50, 50, 50)) # Fill background

    # Blit the scanline surface
    screen.blit(scanline_surface, (0, 0))

    pygame.display.flip()

pygame.quit()