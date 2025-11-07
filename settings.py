import pygame
import os

def run(screen):
    """Заглушка для настроек с выбором разрешения.

    Отображает строку с левой стороны "Разрешение" и правее поле с текущим
    выбором. По нажатию Enter на поле открывается выпадающий список, в
    котором можно выбрать разрешение стрелками UP/DOWN и подтвердить Enter.

    Возвращает обновлённый surface (screen) после возможной смены режима.
    """
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Times New Roman", 28)
    hint_font = pygame.font.SysFont(None, 20)
    project_dir = os.path.dirname(os.path.abspath(__file__))

    resolutions = [(640,480),(720,576),(800,600),(1024,768),(1280,960)]
    res_labels = [f"{w} x {h}" for (w,h) in resolutions]

    # определяем текущий индекс по текущему размеру экрана
    cur_size = screen.get_size()
    try:
        current_index = resolutions.index(cur_size)
    except ValueError:
        # если текущее разрешение не в списке — выбрать ближайшее (или 2-й элемент)
        current_index = 2  # 800x600 по умолчанию

    dropdown_open = False
    selected_index = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # закрываем настройки и возвращаем текущий screen
                    running = False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if not dropdown_open:
                        # открыть выпадающий список
                        dropdown_open = True
                        selected_index = current_index
                    else:
                        # выбрать разрешение
                        current_index = selected_index
                        new_size = resolutions[current_index]
                        screen = pygame.display.set_mode(new_size)
                        # сохраняем выбор в config.json
                        try:
                            cfg_path = os.path.join(project_dir, 'config.json')
                            with open(cfg_path, 'w', encoding='utf-8') as f:
                                import json
                                json.dump({'resolution': [new_size[0], new_size[1]]}, f)
                        except Exception:
                            pass
                        dropdown_open = False
                elif event.key == pygame.K_UP:
                    if dropdown_open:
                        selected_index = (selected_index - 1) % len(resolutions)
                elif event.key == pygame.K_DOWN:
                    if dropdown_open:
                        selected_index = (selected_index + 1) % len(resolutions)

        screen.fill((30, 10, 30))

        # отрисовка элементов: центрируем группу [label | поле] по центру экрана
        spacing = 20
        field_w = 300
        field_h = 40

        label_surf = font.render("Разрешение", True, (255,255,255))
        label_w = label_surf.get_width()

        group_width = label_w + spacing + field_w
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2

        label_x = center_x - group_width // 2
        label_y = center_y - field_h // 2
        field_x = label_x + label_w + spacing
        field_y = label_y

        # отрисовка метки
        screen.blit(label_surf, (label_x, label_y + (field_h - label_surf.get_height())//2))

        # поле текущего разрешения
        field_rect = pygame.Rect(field_x, field_y, field_w, field_h)
        pygame.draw.rect(screen, (60,60,60), field_rect, border_radius=6)

        # текущий текст
        cur_text = font.render(res_labels[current_index], True, (255,255,255))
        screen.blit(cur_text, (field_x + 12, field_y + (field_h - cur_text.get_height())//2))

        # стрелка раскрытия
        arrow = hint_font.render("v", True, (200,200,200))
        screen.blit(arrow, (field_x + field_w - 20, field_y + (field_h - arrow.get_height())//2))

        # если выпадающий список открыт — отрисовать варианты под полем
        if dropdown_open:
            opt_h = field_h
            for i, label_text in enumerate(res_labels):
                rect = pygame.Rect(field_x, field_y + (i+1)*opt_h, field_w, opt_h)
                color = (80,80,80) if i != selected_index else (100,140,180)
                pygame.draw.rect(screen, color, rect, border_radius=6)
                txt = font.render(label_text, True, (255,255,255))
                screen.blit(txt, (rect.x + 12, rect.y + (opt_h - txt.get_height())//2))

        # подсказка внизу
        hint = hint_font.render("Enter — открыть/выбрать, UP/DOWN — навигация, ESC — назад", True, (180,180,180))
        screen.blit(hint, ((screen.get_width() - hint.get_width())//2, screen.get_height() - 40))

        pygame.display.flip()
        clock.tick(60)

    return screen
