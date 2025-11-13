import pygame
import os
import json  # добавлено для записи файла сохранения

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
    APPEAR_MS = 2500 # длительность появления
    HOLD_MS = 2000 # длительность удержания
    FADE_MS = 2500 # длительность затухания

    # тексты
    TEXT1 = "Приготовьтесь окунуться в мир и стать участником событий, на которые иногда..."
    TEXT2 = "...вы не сможете повлиять..."

    # текст перед выбором цвета: последним предложением — вопрос
    PROMPT_TEXT = "Мир полон оттенков и выборов. Ваш путь начнёт меняться в зависимости от одного простого выбора. Какой цвет ты выберешь?"

    # варианты цветов (имя, rgb)
    COLOR_OPTIONS = [("Красный", (200, 40, 40)), ("Зелёный", (40, 160, 40)), ("Синий", (40, 80, 200))]
    color_selected = 0
    color_chosen = None  # сохранённый выбор после подтверждения
    SAVE_FILENAME = "save.json"

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
                # обработка клавиш для стадии выбора цвета (stage == 3)
                if stage == 3:
                    if event.key == pygame.K_ESCAPE:
                        stage = 4
                        stage_start = now
                    elif event.key in (pygame.K_LEFT, pygame.K_UP):
                        color_selected = (color_selected - 1) % len(COLOR_OPTIONS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                        color_selected = (color_selected + 1) % len(COLOR_OPTIONS)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # подтверждение выбранного варианта
                        color_chosen = COLOR_OPTIONS[color_selected][0]
                        save_path = os.path.join(project_dir, SAVE_FILENAME)
                        try:
                            with open(save_path, "w", encoding="utf-8") as f:
                                json.dump({"color": color_chosen}, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                        stage = 4
                        stage_start = now
                    elif event.key in (pygame.K_1, pygame.K_KP1, pygame.K_2, pygame.K_KP2, pygame.K_3, pygame.K_KP3):
                        # быстрый выбор по цифрам 1/2/3
                        if event.key in (pygame.K_1, pygame.K_KP1):
                            idx = 0
                        elif event.key in (pygame.K_2, pygame.K_KP2):
                            idx = 1
                        else:
                            idx = 2
                        color_selected = idx
                        color_chosen = COLOR_OPTIONS[color_selected][0]
                        save_path = os.path.join(project_dir, SAVE_FILENAME)
                        try:
                            with open(save_path, "w", encoding="utf-8") as f:
                                json.dump({"color": color_chosen}, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                        stage = 4
                        stage_start = now
                else:
                    # ESC возвращает в меню только на завершающей стадии (stage==4)
                    if event.key == pygame.K_ESCAPE and stage == 4:
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
                # постоянная прозрачность рамки ~50%; value = int(percent/100 * 255)
                pygame.draw.rect(frame_surf, (80, 80, 80, 127), frame_surf.get_rect(), border_radius=12)
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
                # постоянная прозрачность рамки ~50%; value = int(percent/100 * 255)
                pygame.draw.rect(frame_surf, (80, 80, 80, 127), frame_surf.get_rect(), border_radius=12)
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
            # PROMPT_TEXT + нумерованный список располагаются в нижней части окна,
            # список выровнен по левому краю (margin_x)
            screen.fill((0,0,0))
            prompt_font = pygame.font.SysFont("Times New Roman", 22)
            opt_font = pygame.font.SysFont("Arial", 26)
            hint_font = pygame.font.SysFont("Arial", 16)

            sw, sh = screen.get_size()
            margin_x = 80
            margin_bottom = 40  # место для подсказки внизу

            # подготовить строки PROMPT_TEXT и вычислить высоту блока текста
            wrap_w = sw - 2 * margin_x
            prompt_lines = wrap_text(PROMPT_TEXT, prompt_font, wrap_w)
            prompt_heights = [prompt_font.size(l)[1] for l in prompt_lines]
            prompt_total_h = sum(h + 6 for h in prompt_heights)  # 6px между строками

            # высота списка
            line_h = opt_font.get_height() + 8
            list_total_h = len(COLOR_OPTIONS) * line_h

            # общий блок (текст сверху, список сразу под ним), привязан к нижней части окна
            total_h = prompt_total_h + 12 + list_total_h  # 12px отступ между текстом и списком
            start_y = sh - margin_bottom - total_h

            # отрисовать PROMPT_TEXT (в верхней части блока), выровненный по левому краю margin_x
            y = start_y
            for line in prompt_lines:
                surf = prompt_font.render(line, True, (200,200,200))
                screen.blit(surf, (margin_x, y))
                y += surf.get_height() + 6

            # небольшой отступ перед списком
            y += 12

            # отрисовать нумерованный список под текстом, выровненный по левому краю (margin_x)
            list_x = margin_x
            for i, (name, rgb) in enumerate(COLOR_OPTIONS):
                prefix = f"{i+1}. "
                text = prefix + name
                is_sel = (i == color_selected)
                color = (255,255,255) if is_sel else (200,200,200)
                txt_surf = opt_font.render(text, True, color)
                screen.blit(txt_surf, (list_x, y + i * line_h))
                if is_sel:
                    # небольшая вертикальная метка слева от выбранного пункта
                    mark_x = list_x - 12
                    mark_y = y + i * line_h + 2
                    pygame.draw.rect(screen, (255,255,255), (mark_x, mark_y, 6, txt_surf.get_height() - 4))

            # подсказка внизу экрана (по центру)
            hint = hint_font.render("←/→ или ↑/↓ — навигация, 1/2/3 — быстрый выбор, ENTER — подтвердить", True, (150,150,150))
            screen.blit(hint, ((sw - hint.get_width()) // 2, sh - 30))

        elif stage == 4:
            # чёрный экран-заглушка с инструкцией выхода (раньше был stage==3)
            screen.fill((0,0,0))
            info_font = pygame.font.SysFont("Arial", 20)
            if color_chosen:
                info_text = f"Вы выбрали: {color_chosen}. Нажмите ESC, чтобы вернуться в меню"
            else:
                info_text = "Заглушка: нажмите ESC, чтобы вернуться в меню"
            info = info_font.render(info_text, True, (200,200,200))
            screen.blit(info, ((screen.get_width() - info.get_width())//2, screen.get_height()//2))

        # обновление экрана и тикер (для стадий без событий обработка выше не должна мешать)
        pygame.display.flip()
        clock.tick(60)

    return screen
