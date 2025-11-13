#!/usr/bin/env python3
#точка входа для игры, вызывает play из game.py

# безопасный импорт play (чтобы импорт не ломал запуск, если game.py отсутствует)
try:
    from game import play
except Exception:
    play = None

import pygame
import sys #интерфейс к интерпретатору
import os #API для взаимодействия с ОС
import json #импортируем модуль для работы с JSON

FPS = 60

# Убедиться, что рабочая директория — папка проекта.
# Это важно при запуске через ярлык (который может задавать другой cwd).
project_dir = os.path.dirname(os.path.abspath(__file__))
try:
    os.chdir(project_dir)
except Exception:
    pass

def init():
    """Инициализация pygame и создание игрового окна.
    Читает d:/.../config.json, если там указан параметр resolution — использует его.
    Если конфигурации нет, создаётся config.json с разрешением по умолчанию (800 x 600).
    """
    global WIDTH, HEIGHT
    pygame.init()

    project_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(project_dir, 'config.json')

    # значения по умолчанию, если глобальные не заданы
    default_w, default_h = 800, 600
    res = [globals().get('WIDTH', default_w), globals().get('HEIGHT', default_h)]
    try:
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            r = cfg.get('resolution')
            if isinstance(r, list) and len(r) == 2:
                res = r
        else:
            # создаём конфиг с дефолтным разрешением
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump({'resolution': res}, f)
    except Exception:
        res = [default_w, default_h]

    WIDTH, HEIGHT = int(res[0]), int(res[1])
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("First game RPG")
    return screen

def draw_menu(screen, menu_font, hint_font, items, selected_index):
    """Отрисовать вертикальное меню, выровненное по центру экрана.
    menu_font — шрифт для пунктов меню.
    hint_font — шрифт для подсказки внизу экрана.
    """
    sw, sh = screen.get_size()
    screen.fill((20, 24, 30))
    total_h = 0
    spacing = 10
    texts = []
    for it in items:
        surf = menu_font.render(it, True, (200, 200, 200))
        texts.append(surf)
        total_h += surf.get_height() + spacing
    if texts:
        total_h -= spacing

    start_y = (sh - total_h) // 2
    for idx, surf in enumerate(texts):
        x = (sw - surf.get_width()) // 2
        y = start_y + idx * (surf.get_height() + spacing)
        # выделение выбранного пункта
        if idx == selected_index:
            # рисуем фон выделения с отступом
            rect = pygame.Rect(x - 20, y - 5, surf.get_width() + 40, surf.get_height() + 10)
            pygame.draw.rect(screen, (60, 100, 140), rect, border_radius=6)
            text_surf = menu_font.render(items[idx], True, (255, 255, 255))
            screen.blit(text_surf, (x, y))
        else:
            screen.blit(surf, (x, y))

    hint = hint_font.render("Use UP/DOWN to navigate, ENTER to select, ESC to quit", True, (140,140,140))
    screen.blit(hint, ((sw - hint.get_width()) // 2, sh - 40))

def main():
    """Главный игровой цикл приложения.

    Основные обязанности:
    - инициализировать экран, шрифт и таймер (clock)
    - отображать стартовое меню и вызывать соответствующие модули
    - корректно завершать работу (pygame.quit() и sys.exit())
    """
    screen = init()
    clock = pygame.time.Clock()
    # шрифты будут создаваться динамически в зависимости от текущего разрешения
    prev_size = screen.get_size()
    def make_fonts_for(size):
        w, h = size
        # масштабируем размер шрифта пропорционально высоте окна
        menu_size = max(16, int(h * 0.06))  # примерно 6% высоты
        hint_size = max(12, int(h * 0.025))  # примерно 2.5% высоты
        try:
            menu_font = pygame.font.SysFont("Arial", menu_size)
        except Exception:
            menu_font = pygame.font.SysFont(None, menu_size)
        try:
            hint_font = pygame.font.SysFont("Times New Roman", hint_size)
        except Exception:
            hint_font = pygame.font.SysFont(None, hint_size)
        return menu_font, hint_font
    menu_font, hint_font = make_fonts_for(prev_size)

    # меню
    menu_items = ["Стартуем", "Настройки", "Об игре", "Выход"]
    selected = 0
    in_menu = True

    while in_menu:
        # если размер окна изменился (например, после настроек) — пересоздать шрифты
        if screen.get_size() != prev_size:
            prev_size = screen.get_size()
            menu_font, hint_font = make_fonts_for(prev_size)

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
                    elif choice == "Стартуем":
                        # импортируем модуль при выборе, чтобы избежать ненужных зависимостей
                        import start as start_mod
                        start_mod.run(screen)
                    elif choice == "Настройки":
                        import settings as settings_mod
                        screen = settings_mod.run(screen)
                        # после возврата из настроек экран мог измениться — обновить шрифты
                        if screen.get_size() != prev_size:
                            prev_size = screen.get_size()
                            menu_font, hint_font = make_fonts_for(prev_size)
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