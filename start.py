import pygame
import os

# путь к файлу фонового изображения (относительно каталога проекта)
IMAGE_PATH = "images/start.jpeg"  # замените на имя вашего файла в папке проекта

def wrap_text(text, font, max_width):
    """Разбивает текст на строки, чтобы каждая строка не превышала max_width."""
    words = text.split()
    lines = []
    if not words:
        return lines
    cur = words[0]
    for w in words[1:]:
        test = cur + ' ' + w
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines

def run(screen):
    """Запуск игрового режима с фоновым изображением и последовательной анимацией текста.

    Поведение:
    - загружает IMAGE_PATH (если не найден — используется заливка цветом)
    - масштабирует фон под текущее разрешение screen.get_size()
    - последовательно показывает два текста с эффектом появления и затухания
      (время появления и затухания задаётся в миллисекундах ниже)
    - после второго текста показывает чёрный экран-заглушку с инструкцией выхода

    Возвращает текущий screen (тот же объект или перезаписанный после изменения разрешения).
    """
    clock = pygame.time.Clock()

    # настройки времени в миллисекундах
    APPEAR_MS = 1500
    HOLD_MS = 800
    FADE_MS = 1500

    # тексты
    TEXT1 = "Приготовьтесь окунуться в мир и стать участником событий, на которые иногда..."
    TEXT2 = "...вы не сможете повлиять..."

    # загрузка и масштабирование фона
    bg = None
    project_dir = os.path.dirname(os.path.abspath(__file__))
    image_full = os.path.join(project_dir, IMAGE_PATH)
    try:
        loaded = pygame.image.load(image_full)
        bg = pygame.transform.smoothscale(loaded.convert(), screen.get_size())
    except Exception:
        bg = None

    # подготовка шрифта
    title_font = pygame.font.SysFont("Times New Roman", 32)

    # стадии: 0 - текст1, 1 - пауза между текстами, 2 - текст2, 3 - black placeholder
    stage = 0
    stage_start = pygame.time.get_ticks()
    running = True

    # время паузы между окончанием первого текста и началом второго (в миллисекундах)
    GAP_MS = 600  # можно быстро изменить

    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen
            elif event.type == pygame.KEYDOWN:
                # ESC возвращает в меню только на завершающей стадии
                if event.key == pygame.K_ESCAPE and stage == 3:
                    running = False

        # если размер экрана изменился (например, сменили разрешение) — пересоздать фон
        if bg is not None and screen.get_size() != bg.get_size():
            try:
                loaded = pygame.image.load(image_full)
                bg = pygame.transform.smoothscale(loaded.convert(), screen.get_size())
            except Exception:
                bg = None

        # отрисовка фона
        if bg:
            screen.blit(bg, (0,0))
        else:
            screen.fill((10, 30, 10))

        # логика стадий появления/затухания
        def compute_alpha(t_rel):
            if t_rel < APPEAR_MS:
                return int(255 * (t_rel / APPEAR_MS))
            elif t_rel < APPEAR_MS + HOLD_MS:
                return 255
            elif t_rel < APPEAR_MS + HOLD_MS + FADE_MS:
                return int(255 * (1 - (t_rel - APPEAR_MS - HOLD_MS) / FADE_MS))
            else:
                return -1  # сигнал окончания стадии

        if stage == 0:
            # отображение первого текста
            t_rel = now - stage_start
            alpha0 = compute_alpha(t_rel)
            if alpha0 < 0:
                # после окончания показа первого текста — перейти в паузу
                stage = 1
                stage_start = now
            else:
                # рисуем первый текст
                margin = 60
                max_text_width = max(100, screen.get_width() - 2 * margin)
                lines0 = wrap_text(TEXT1, title_font, max_text_width)
                line_surfs0 = [title_font.render(line, True, (255,255,255)).convert_alpha() for line in lines0]
                spacing = 6
                text_block_w = max(s.get_width() for s in line_surfs0)
                text_block_h = sum(s.get_height() for s in line_surfs0) + spacing * (len(line_surfs0) - 1)
                frame_padding = 20
                box_w = text_block_w + 2 * frame_padding
                box_h = text_block_h + 2 * frame_padding
                box_x = (screen.get_width() - box_w) // 2
                box_y = (screen.get_height() - box_h) // 2

                frame_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                # рисуем полную форму и затем задаём общую альфу, чтобы рамка появлялась/затухала с текстом
                pygame.draw.rect(frame_surf, (80, 80, 80, 255), frame_surf.get_rect(), border_radius=12)
                frame_surf.set_alpha(alpha0)
                screen.blit(frame_surf, (box_x, box_y))

                text_surf0 = pygame.Surface((text_block_w, text_block_h), pygame.SRCALPHA)
                y_off = 0
                for s in line_surfs0:
                    x_off = (text_block_w - s.get_width()) // 2
                    text_surf0.blit(s, (x_off, y_off))
                    y_off += s.get_height() + spacing
                text_surf0.set_alpha(alpha0)
                screen.blit(text_surf0, (box_x + frame_padding, box_y + frame_padding))

        elif stage == 1:
            # простая пауза между текстами
            if now - stage_start >= GAP_MS:
                stage = 2
                stage_start = now

        elif stage == 2:
            # отображение второго текста
            t_rel = now - stage_start
            alpha = compute_alpha(t_rel)
            if alpha < 0:
                stage = 3
                stage_start = now
            else:
                margin = 60
                max_text_width = max(100, screen.get_width() - 2 * margin)
                lines = wrap_text(TEXT2, title_font, max_text_width)
                line_surfs = [title_font.render(line, True, (255,255,255)).convert_alpha() for line in lines]
                spacing = 6
                text_block_w = max(s.get_width() for s in line_surfs)
                text_block_h = sum(s.get_height() for s in line_surfs) + spacing * (len(line_surfs) - 1)
                frame_padding = 20
                box_w = text_block_w + 2 * frame_padding
                box_h = text_block_h + 2 * frame_padding
                box_x = (screen.get_width() - box_w) // 2
                box_y = (screen.get_height() - box_h) // 2

                frame_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                pygame.draw.rect(frame_surf, (80, 80, 80, 255), frame_surf.get_rect(), border_radius=12)
                frame_surf.set_alpha(alpha)
                screen.blit(frame_surf, (box_x, box_y))

                text_surf = pygame.Surface((text_block_w, text_block_h), pygame.SRCALPHA)
                y_off = 0
                for s in line_surfs:
                    x_off = (text_block_w - s.get_width()) // 2
                    text_surf.blit(s, (x_off, y_off))
                    y_off += s.get_height() + spacing
                text_surf.set_alpha(alpha)
                screen.blit(text_surf, (box_x + frame_padding, box_y + frame_padding))

        elif stage == 3:
            # чёрный экран-заглушка с инструкцией выхода
            screen.fill((0,0,0))
            info_font = pygame.font.SysFont("Arial", 20)
            info = info_font.render("Заглушка: нажмите ESC, чтобы вернуться в меню", True, (200,200,200))
            screen.blit(info, ((screen.get_width() - info.get_width())//2, screen.get_height()//2))

        pygame.display.flip()
        clock.tick(60)

    return screen
