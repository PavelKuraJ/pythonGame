import pygame

def run(screen):
    """Заглушка для экрана 'Об игре'."""
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Times New Roman", 28)
    running = True
    lines = [
        "Пошаговая RPG - альфа-версия",
        "Разработчик: Вы",
        "Нажмите ESC, чтобы вернуться в меню"
    ]
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((10, 10, 30))
        y = screen.get_height()//2 - 40
        for line in lines:
            text = font.render(line, True, (200,200,255))
            screen.blit(text, ((screen.get_width() - text.get_width())//2, y))
            y += text.get_height() + 8

        pygame.display.flip()
        clock.tick(60)
