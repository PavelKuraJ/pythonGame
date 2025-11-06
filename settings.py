import pygame

def run(screen):
    """Заглушка для настроек. Позже здесь будут параметры и значения."""
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Times New Roman", 36)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((30, 10, 30))
        text = font.render("Settings - press ESC to return to menu", True, (255,255,255))
        screen.blit(text, ((screen.get_width() - text.get_width())//2, screen.get_height()//2))
        pygame.display.flip()
        clock.tick(60)
