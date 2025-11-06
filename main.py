#!/usr/bin/env python3
# точка входа для игрыб вызывает play из game.py
from game import play
import pygame
import sys

WIDTH, HEIGHT = 800, 600
FPS = 60

def init():
    """Инициализация pygame и создание игрового окна.

    Отвечает за:
    - вызов pygame.init()
    - создание окна с размерами WIDTH x HEIGHT
    - установку заголовка окна

    Возвращает:
    - screen: pygame Surface для отрисовки содержимого окна
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("First game RPG")
    return screen

def main():
    """Главный игровой цикл приложения.

    Основные обязанности:
    - инициализировать экран, шрифт и таймер (clock)
    - обрабатывать события (выход, клавиши управления)
    - обновлять состояние игры (например, переключение хода по SPACE)
    - отрисовывать интерфейс и поддерживать стабильный FPS
    - корректно завершать работу (pygame.quit() и sys.exit())
    """
    screen = init()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    running = True

    # базовое состояние игры
    game_state = {"turn": "player"}  # 'player' или 'enemy'

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # заглушка: пробел переключает ход
                elif event.key == pygame.K_SPACE:
                    if game_state["turn"] == "player":
                        game_state["turn"] = "enemy"
                    else:
                        game_state["turn"] = "player"

        screen.fill((30, 30, 40))

        # отрисовка UI
        text = font.render(f"Turn: {game_state['turn']} - Press SPACE to toggle, ESC to quit", True, (255,255,255))
        screen.blit(text, (20,20))

        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (200,200,200))
        screen.blit(fps_text, (20, 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("Простая игра: угадай число")
    play()
    main()