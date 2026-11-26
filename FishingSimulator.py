import math
import random
import sys
import pygame

pygame.init()

WIDTH = 960
HEIGHT = 600
WATER_Y = 220
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Речная рыбалка // Радар")
clock = pygame.time.Clock()

# Загружаем шрифт напрямую без SysFont, чтобы не падало на Windows
try:
    font = pygame.font.Font("C:/Windows/Fonts/arial.ttf", 21)
    small_font = pygame.font.Font("C:/Windows/Fonts/arial.ttf", 16)
except OSError:
    font = pygame.font.Font(None, 26)
    small_font = pygame.font.Font(None, 20)

# Чёрно-зелёная палитра
BLACK = (0, 0, 0)
DARK_GREEN = (0, 55, 0)
MID_GREEN = (0, 130, 0)
GREEN = (0, 220, 0)
BRIGHT_GREEN = (130, 255, 130)

# Виды рыб: название, цена продажи, сила сопротивления, размер
fish_types = [
    {"name": "Карась", "price": 15, "pull": 22, "w": 34, "h": 16},
    {"name": "Окунь", "price": 25, "pull": 32, "w": 40, "h": 18},
    {"name": "Щука", "price": 45, "pull": 46, "w": 56, "h": 20},
    {"name": "Осётр", "price": 85, "pull": 62, "w": 66, "h": 22},
]


def create_fish():
    info = random.choice(fish_types)
    direction = random.choice([-1, 1])
    x = random.randint(240, WIDTH - 80)
    y = random.randint(WATER_Y + 55, HEIGHT - 65)
    speed = random.uniform(1.0, 2.0) * direction
    return {
        "name": info["name"],
        "price": info["price"],
        "pull": info["pull"],
        "w": info["w"],
        "h": info["h"],
        "x": float(x),
        "y": float(y),
        "speed": speed,
        "dir": direction,
    }


def draw_fish(surf, fish):
    x = int(fish["x"])
    y = int(fish["y"])
    w = fish["w"]
    h = fish["h"]
    d = fish["dir"]

    # Тело рыбы
    pygame.draw.ellipse(surf, GREEN, (x - w // 2, y - h // 2, w, h))
    pygame.draw.ellipse(surf, BRIGHT_GREEN, (x - w // 2, y - h // 2, w, h), 1)

    # Хвост
    tail_x = x - d * (w // 2 + 10)
    tail_joint_x = x - d * (w // 2 - 2)
    pygame.draw.polygon(
        surf,
        GREEN,
        [
            (tail_joint_x, y),
            (tail_x, y - h // 2),
            (tail_x, y + h // 2),
        ],
    )

    # Глаз
    eye_x = x + d * (w // 4)
    pygame.draw.circle(surf, BLACK, (eye_x, y - 2), 2)

    # Подпись над рыбой
    name_surf = small_font.render(fish["name"], True, GREEN)
    surf.blit(name_surf, (x - name_surf.get_width() // 2, y - h // 2 - 20))


def main():
    # Состояния: "idle", "waiting", "bite", "pulling"
    state = "idle"

    money = 0
    total_caught = 0
    bag = []  # пойманные рыбы, которые можно продать

    rod_level = 1
    upgrade_cost = 50

    message = "Наведи на рыбу и жми ЛКМ/ПРОБЕЛ | S — продать | U — качать удочку"

    rod_base = (115, WATER_Y - 25)
    rod_tip = (195, WATER_Y - 85)

    bob_x = 450.0
    bob_y = float(WATER_Y + 75)
    target_x = 450.0
    target_y = float(WATER_Y + 75)

    scan_x = 200.0
    scan_dir = 1

    bite_timer = 0.0
    distance_left = 100.0  # 100 — далеко, 0 — вытащили
    tension = 0.0        # натяжение лески от 0 до 100
    current_fish = None

    fishes = []
    for _ in range(7):
        fishes.append(create_fish())

    # Прямоугольники кнопок для клика мышкой
    sell_btn = pygame.Rect(540, 14, 185, 32)
    upgrade_btn = pygame.Rect(738, 14, 205, 32)

    def sell_fish():
        nonlocal money, message
        if len(bag) == 0:
            message = "Садок пуст — нечего продавать!"
            return
        earned = 0
        for item in bag:
            earned += item["price"]
        money += earned
        count = len(bag)
        bag.clear()
        message = f"Продал рыб ({count} шт.) за +{earned} монет!"

    def upgrade_rod():
        nonlocal money, rod_level, upgrade_cost, message
        if money < upgrade_cost:
            message = f"Не хватает монет! Нужно {upgrade_cost}, у тебя {money}."
            return
        money -= upgrade_cost
        rod_level += 1
        upgrade_cost += 40
        message = f"Удочка прокачана до {rod_level} ур.! Тянет быстрее и прочнее."

    while True:
        dt = clock.tick(FPS) / 1000.0

        # Двигаем вертикальный луч радара по воде
        scan_x += scan_dir * 180 * dt
        if scan_x > WIDTH - 30:
            scan_x = WIDTH - 30
            scan_dir = -1
        elif scan_x < 190:
            scan_x = 190
            scan_dir = 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_s:
                    sell_fish()

                if event.key == pygame.K_u:
                    upgrade_rod()

                if event.key == pygame.K_SPACE:
                    if state == "idle":
                        state = "waiting"
                        bob_x = target_x
                        bob_y = target_y
                        message = "Забросил! Подведи крючок к рыбе или жди, пока подплывёт."
                    elif state == "bite":
                        state = "pulling"
                        distance_left = 100.0
                        tension = 20.0
                        message = "Подсёк! Удерживай ПРОБЕЛ или ЛКМ, чтобы тянуть!"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Проверка клика по кнопкам вверху
                if sell_btn.collidepoint(mx, my):
                    sell_fish()
                    continue
                if upgrade_btn.collidepoint(mx, my):
                    upgrade_rod()
                    continue

                if state == "idle":
                    state = "waiting"
                    bob_x = target_x
                    bob_y = target_y
                    message = "Забросил! Подведи крючок к рыбе или жди, пока подплывёт."
                elif state == "bite":
                    state = "pulling"
                    distance_left = 100.0
                    tension = 20.0
                    message = "Подсёк! Удерживай ПРОБЕЛ или ЛКМ, чтобы тянуть!"

        keys = pygame.key.get_pressed()
        mouse_down = pygame.mouse.get_pressed()[0]
        pulling_now = state == "pulling" and (keys[pygame.K_SPACE] or mouse_down)

        # Двигаем рыбу в реке
        for fish in fishes:
            fish["x"] += fish["speed"]
            if fish["x"] < 230:
                fish["x"] = 230
                fish["dir"] = 1
                fish["speed"] = abs(fish["speed"])
            elif fish["x"] > WIDTH - 60:
                fish["x"] = WIDTH - 60
                fish["dir"] = -1
                fish["speed"] = -abs(fish["speed"])

        # Логика состояний рыбалки
        if state == "idle":
            mx, my = pygame.mouse.get_pos()
            target_x = float(max(230, min(WIDTH - 70, mx)))
            target_y = float(max(WATER_Y + 35, min(HEIGHT - 55, my)))
            bob_x = target_x
            bob_y = target_y

        elif state == "waiting":
            # Можно слегка вести приманку мышкой в воде
            mx, my = pygame.mouse.get_pos()
            bob_x = float(max(230, min(WIDTH - 70, mx)))
            bob_y = float(max(WATER_Y + 35, min(HEIGHT - 55, my)))

            # Проверяем реальное попадание крючка рядом с рыбой
            found_fish = None
            for fish in fishes:
                dist = math.hypot(fish["x"] - bob_x, fish["y"] - bob_y)
                if dist < 38:
                    found_fish = fish
                    break

            if found_fish is not None:
                current_fish = found_fish
                state = "bite"
                bite_timer = 1.6
                message = f"Зацепил: {current_fish['name']}! Жми ПРОБЕЛ или ЛКМ!"

        elif state == "bite":
            bite_timer -= dt
            bob_y += random.uniform(-4, 4)
            if bite_timer <= 0:
                current_fish = None
                state = "idle"
                message = "Рыба ушла, не успел подсечь!"

        elif state == "pulling":
            # Прокачка удочки ускоряет подмотку и снижает рост натяжения
            pull_speed = 38 + (rod_level - 1) * 9
            tension_gain_mult = max(0.55, 1.0 - (rod_level - 1) * 0.08)

            if pulling_now:
                distance_left -= pull_speed * dt
                tension += (34 + current_fish["pull"] * 0.45) * tension_gain_mult * dt
            else:
                distance_left += current_fish["pull"] * 0.4 * dt
                tension -= 48 * dt

            if tension < 0:
                tension = 0
            if distance_left > 130:
                distance_left = 130

            # Подтягиваем крючок и рыбу к удочке
            k = min(distance_left / 100.0, 1.0)
            bob_x = rod_tip[0] + (target_x - rod_tip[0]) * k
            bob_y = WATER_Y + 25 + (target_y - (WATER_Y + 25)) * k
            current_fish["x"] = bob_x
            current_fish["y"] = bob_y

            if tension >= 100:
                fishes.remove(current_fish)
                fishes.append(create_fish())
                current_fish = None
                state = "idle"
                message = "Леска порвалась! Прокачай удочку или тяни плавнее."

            elif distance_left >= 130:
                current_fish = None
                state = "idle"
                message = "Рыба сорвалась! Тяни активнее."

            elif distance_left <= 0:
                total_caught += 1
                bag.append(current_fish)
                caught_name = current_fish["name"]
                caught_price = current_fish["price"]

                fishes.remove(current_fish)
                fishes.append(create_fish())
                current_fish = None

                state = "idle"
                message = f"Поймал: {caught_name} (в садке, цена {caught_price})!"

        # Отрисовка
        screen.fill(BLACK)

        # Сетка радара
        for x in range(0, WIDTH, 60):
            pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y), 1)

        # Поверхность реки и луч радара
        pygame.draw.line(screen, BRIGHT_GREEN, (0, WATER_Y), (WIDTH, WATER_Y), 2)
        pygame.draw.line(screen, MID_GREEN, (int(scan_x), WATER_Y), (int(scan_x), HEIGHT), 2)

        # Берег слева и рыбак
        pygame.draw.rect(screen, DARK_GREEN, (0, WATER_Y - 15, 175, 30))
        pygame.draw.line(screen, GREEN, (0, WATER_Y - 15), (175, WATER_Y - 15), 2)

        pygame.draw.circle(screen, BRIGHT_GREEN, (105, WATER_Y - 58), 9, 2)
        pygame.draw.line(screen, BRIGHT_GREEN, (105, WATER_Y - 49), (105, WATER_Y - 15), 3)

        # Удочка (толщина растёт с уровнем)
        pygame.draw.line(screen, BRIGHT_GREEN, rod_base, rod_tip, 3 + rod_level)

        # Рыбки под водой
        for fish in fishes:
            draw_fish(screen, fish)

        # Прицел или леска и крючок
        if state == "idle":
            pygame.draw.circle(screen, BRIGHT_GREEN, (int(target_x), int(target_y)), 12, 2)
        else:
            pygame.draw.line(screen, BRIGHT_GREEN, rod_tip, (int(bob_x), int(bob_y)), 2)
            r_size = 10 if state == "bite" else 6
            pygame.draw.circle(screen, BRIGHT_GREEN, (int(bob_x), int(bob_y)), r_size, 2)

        # Верхняя панель статистики и кнопок
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 60))
        pygame.draw.line(screen, GREEN, (0, 60), (WIDTH, 60), 2)

        stats_text = font.render(
            f"Монеты: {money}  |  Поймано: {total_caught}  |  В садке: {len(bag)}  |  Уд. ур.{rod_level}",
            True,
            BRIGHT_GREEN,
        )
        screen.blit(stats_text, (16, 18))

        # Кнопка продажи
        pygame.draw.rect(screen, DARK_GREEN, sell_btn)
        pygame.draw.rect(screen, BRIGHT_GREEN, sell_btn, 2)
        sell_label = small_font.render("Продать рыбу [S]", True, BRIGHT_GREEN)
        screen.blit(sell_label, (sell_btn.x + 16, sell_btn.y + 8))

        # Кнопка прокачки
        pygame.draw.rect(screen, DARK_GREEN, upgrade_btn)
        pygame.draw.rect(screen, BRIGHT_GREEN, upgrade_btn, 2)
        up_label = small_font.render(f"Удочка ({upgrade_cost}) [U]", True, BRIGHT_GREEN)
        screen.blit(up_label, (upgrade_btn.x + 14, upgrade_btn.y + 8))

        # Шкала натяжения лески при вываживании
        if state == "pulling":
            bar_x = WIDTH - 60
            bar_y = 250
            bar_w = 22
            bar_h = 220
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_w, bar_h), 2)
            fill_h = int(bar_h * min(tension, 100) / 100)
            pygame.draw.rect(screen, BRIGHT_GREEN, (bar_x + 3, bar_y + bar_h - fill_h, bar_w - 6, fill_h))
            t_text = small_font.render(f"{int(tension)}%", True, BRIGHT_GREEN)
            screen.blit(t_text, (bar_x - 4, bar_y + bar_h + 8))

        # Нижняя строка подсказок
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 44, WIDTH, 44))
        msg_surf = font.render(message, True, BRIGHT_GREEN)
        screen.blit(msg_surf, (16, HEIGHT - 34))

        pygame.display.flip()


if __name__ == "__main__":
    main()
