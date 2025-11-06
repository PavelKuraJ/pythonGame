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

def draw_menu(screen, menu_font, hint_font, items, selected_index):
    """Отрисовать вертикальное меню, выровненное по центру экрана.

    menu_font — шрифт для пунктов меню.
    hint_font — шрифт для подсказки внизу экрана.
    """
    screen.fill((20, 24, 30))
    total_h = 0
    spacing = 10
    texts = []
    for it in items:
        surf = menu_font.render(it, True, (200, 200, 200))
        texts.append(surf)
        total_h += surf.get_height() + spacing
    total_h -= spacing

    start_y = (HEIGHT - total_h) // 2
    for idx, surf in enumerate(texts):
        x = (WIDTH - surf.get_width()) // 2
        y = start_y + idx * (surf.get_height() + spacing)
        # выделение выбранного пункта
        if idx == selected_index:
            # рисуем фон
            rect = pygame.Rect(x - 20, y - 5, surf.get_width() + 40, surf.get_height() + 10)
            pygame.draw.rect(screen, (60, 100, 140), rect, border_radius=6)
            text_surf = menu_font.render(items[idx], True, (255, 255, 255))
            screen.blit(text_surf, (x, y))
        else:
            screen.blit(surf, (x, y))

    hint = hint_font.render("Use UP/DOWN to navigate, ENTER to select, ESC to quit", True, (140,140,140))
    screen.blit(hint, ((WIDTH - hint.get_width()) // 2, HEIGHT - 40))

def main():
    """Главный игровой цикл приложения.

    Основные обязанности:
    - инициализировать экран, шрифт и таймер (clock)
    - отображать стартовое меню и вызывать соответствующие модули
    - корректно завершать работу (pygame.quit() и sys.exit())
    """
    screen = init()
    clock = pygame.time.Clock()
    # menu font (для пунктов меню)
    menu_font = pygame.font.SysFont("Arial", 36)
    # hint font (меньше, для подсказки)
    hint_font = pygame.font.SysFont("Times New Roman", 18)

    # меню
    menu_items = ["Начать игру", "Настройки", "Об игре", "Выход"]
    selected = 0
    in_menu = True

    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    choice = menu_items[selected]
                    if choice == "Выход":
                        pygame.quit()
                        sys.exit()
                    elif choice == "Начать игру":
                        # импортируем модуль при выборе, чтобы избежать ненужных зависимостей
                        import start as start_mod
                        start_mod.run(screen)
                    elif choice == "Настройки":
                        import settings as settings_mod
                        settings_mod.run(screen)
                    elif choice == "Об игре":
                        import about as about_mod
                        about_mod.run(screen)

        draw_menu(screen, menu_font, hint_font, menu_items, selected)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    print("Простая игра: меню запуска")
    # play() оставлен, но не требуется для показа меню
    # play()
    main()