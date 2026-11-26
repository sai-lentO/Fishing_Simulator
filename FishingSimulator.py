import random
import pygame


# ======================================
# ЧАСТЬ 1. ИГРОВЫЕ МЕХАНИКИ И УПРАВЛЕНИЕ
# ======================================

FISH = [
    {"name": "Карась", "price": 10},
    {"name": "Окунь", "price": 20},
    {"name": "Щука", "price": 35},
    {"name": "Сом", "price": 50}
]


def create_game():
    """Создаёт начальные данные игрока."""
    game = {
        "coins": 0,
        "inventory": []
    }
    return game


def catch_fish(game):
    if random.randint(1, 100) <= 80:
        fish = random.choice(FISH)
        game["inventory"].append(fish)
        return fish

    return None


def sell_fish(game):
    if len(game["inventory"]) == 0:
        return 0

    total = 0

    for fish in game["inventory"]:
        total = total + fish["price"]

    game["coins"] = game["coins"] + total
    game["inventory"] = []

    return total


def get_inventory(game):
    return game["inventory"]


def get_coins(game):
    return game["coins"]


def handle_player_input(event, game):
    if event.type == pygame.QUIT:
        return "exit"

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            fish = catch_fish(game)

            if fish is None:
                return "Рыба не клюнула! Попробуй ещё раз."

            return "Ты поймал: " + fish["name"] + "!"

        elif event.key == pygame.K_s:
            total = sell_fish(game)

            if total == 0:
                return "Нет рыбы для продажи!"

            return "Продано! Получено монет: " + str(total)

        elif event.key == pygame.K_i:
            if len(game["inventory"]) == 0:
                return "Инвентарь пуст!"

            result = "Твой улов: "

            for fish in game["inventory"]:
                result = result + fish["name"] + ", "

            return result.rstrip(", ")

        elif event.key == pygame.K_ESCAPE:
            return "exit"

    return None


# ==================
# ЧАСТЬ 2. ИНТЕРФЕЙС
# ==================

WIDTH = 960
HEIGHT = 600
WATER_Y = 220
FPS = 60

BLACK = (0, 0, 0)
DARK_GREEN = (0, 55, 0)
MID_GREEN = (0, 130, 0)
GREEN = (0, 220, 0)
BRIGHT_GREEN = (130, 255, 130)

FISH_SIZES = {
    "Карась": (34, 16),
    "Окунь": (40, 18),
    "Щука": (56, 20),
    "Сом": (62, 22)
}


def create_visual_fish():
    info = random.choice(FISH)
    direction = random.choice([-1, 1])
    width, height = FISH_SIZES[info["name"]]

    return {
        "name": info["name"],
        "price": info["price"],
        "w": width,
        "h": height,
        "x": float(random.randint(240, WIDTH - 80)),
        "y": float(random.randint(WATER_Y + 55, HEIGHT - 65)),
        "speed": random.uniform(35.0, 75.0) * direction,
        "dir": direction
    }


def draw_fish(surface, fish, small_font):
    x = int(fish["x"])
    y = int(fish["y"])
    width = fish["w"]
    height = fish["h"]
    direction = fish["dir"]

    # Тело рыбы.
    pygame.draw.ellipse(
        surface, GREEN,
        (x - width // 2, y - height // 2, width, height)
    )
    pygame.draw.ellipse(
        surface, BRIGHT_GREEN,
        (x - width // 2, y - height // 2, width, height), 1
    )

    # Хвост.
    tail_x = x - direction * (width // 2 + 10)
    tail_joint_x = x - direction * (width // 2 - 2)
    pygame.draw.polygon(
        surface,
        GREEN,
        [
            (tail_joint_x, y),
            (tail_x, y - height // 2),
            (tail_x, y + height // 2)
        ]
    )

    # Глаз.
    eye_x = x + direction * (width // 4)
    pygame.draw.circle(surface, BLACK, (eye_x, y - 2), 2)

    # Название рыбы.
    name_surface = small_font.render(fish["name"], True, GREEN)
    surface.blit(
        name_surface,
        (x - name_surface.get_width() // 2, y - height // 2 - 20)
    )


def draw_inventory(screen, font, small_font, inventory):
    panel_x = 18
    panel_y = 76
    panel_width = 245
    visible_fish = inventory[:8]
    extra_count = len(inventory) - len(visible_fish)
    panel_height = 48 + len(visible_fish) * 25

    if extra_count > 0:
        panel_height += 25

    pygame.draw.rect(
        screen, DARK_GREEN,
        (panel_x, panel_y, panel_width, panel_height)
    )
    pygame.draw.rect(
        screen, BRIGHT_GREEN,
        (panel_x, panel_y, panel_width, panel_height), 2
    )

    title = font.render("ТВОЙ УЛОВ", True, BRIGHT_GREEN)
    screen.blit(title, (panel_x + 12, panel_y + 9))

    y = panel_y + 43
    if len(inventory) == 0:
        empty_text = small_font.render("Инвентарь пуст", True, BRIGHT_GREEN)
        screen.blit(empty_text, (panel_x + 12, y))
    else:
        for fish in visible_fish:
            line = fish["name"] + " - " + str(fish["price"]) + " монет"
            fish_text = small_font.render(line, True, BRIGHT_GREEN)
            screen.blit(fish_text, (panel_x + 12, y))
            y += 25

        if extra_count > 0:
            extra_text = small_font.render(
                "И ещё рыб: " + str(extra_count), True, BRIGHT_GREEN
            )
            screen.blit(extra_text, (panel_x + 12, y))


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Симулятор рыбалки")
    clock = pygame.time.Clock()

    try:
        font = pygame.font.Font("C:/Windows/Fonts/arial.ttf", 21)
        small_font = pygame.font.Font("C:/Windows/Fonts/arial.ttf", 16)
    except OSError:
        font = pygame.font.Font(None, 26)
        small_font = pygame.font.Font(None, 20)

    game = create_game()
    message = "ПРОБЕЛ — рыбачить | S — продать | I — инвентарь | ESC — выход"
    running = True
    show_inventory = False

    rod_base = (115, WATER_Y - 25)
    rod_tip = (195, WATER_Y - 85)
    bobber_x = 450
    bobber_y = WATER_Y + 115

    scan_x = 200.0
    scan_dir = 1

    # Рыбы для анимации на экране. Они не являются игровым инвентарём.
    fishes = []
    for _ in range(7):
        fishes.append(create_visual_fish())

    while running:
        dt = clock.tick(FPS) / 1000.0

        # Движение луча радара.
        scan_x += scan_dir * 180 * dt
        if scan_x > WIDTH - 30:
            scan_x = WIDTH - 30
            scan_dir = -1
        elif scan_x < 190:
            scan_x = 190
            scan_dir = 1

        # Обработка событий через твою функцию управления.
        for event in pygame.event.get():
            result = handle_player_input(event, game)

            if result == "exit":
                running = False
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                show_inventory = not show_inventory
                if show_inventory:
                    message = "Инвентарь открыт. Нажми I, чтобы закрыть."
                else:
                    message = "Инвентарь закрыт."

            elif result is not None:
                message = result

        if not running:
            break

        # Движение декоративных рыб в воде.
        for fish in fishes:
            fish["x"] += fish["speed"] * dt

            if fish["x"] < 230:
                fish["x"] = 230
                fish["dir"] = 1
                fish["speed"] = abs(fish["speed"])
            elif fish["x"] > WIDTH - 60:
                fish["x"] = WIDTH - 60
                fish["dir"] = -1
                fish["speed"] = -abs(fish["speed"])

        # ----------------------------------------------------
        # Отрисовка интерфейса.
        # ----------------------------------------------------
        screen.fill(BLACK)

        # Сетка радара.
        for x in range(0, WIDTH, 60):
            pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y), 1)

        # Поверхность реки и луч радара.
        pygame.draw.line(
            screen, BRIGHT_GREEN, (0, WATER_Y), (WIDTH, WATER_Y), 2
        )
        pygame.draw.line(
            screen, MID_GREEN,
            (int(scan_x), WATER_Y), (int(scan_x), HEIGHT), 2
        )

        # Берег и рыбак.
        pygame.draw.rect(screen, DARK_GREEN, (0, WATER_Y - 15, 175, 30))
        pygame.draw.line(
            screen, GREEN,
            (0, WATER_Y - 15), (175, WATER_Y - 15), 2
        )
        pygame.draw.circle(
            screen, BRIGHT_GREEN, (105, WATER_Y - 58), 9, 2
        )
        pygame.draw.line(
            screen, BRIGHT_GREEN,
            (105, WATER_Y - 49), (105, WATER_Y - 15), 3
        )

        # Удочка, леска и поплавок — декоративные элементы.
        pygame.draw.line(screen, BRIGHT_GREEN, rod_base, rod_tip, 4)
        pygame.draw.line(
            screen, BRIGHT_GREEN,
            rod_tip, (bobber_x, bobber_y), 1
        )
        pygame.draw.circle(
            screen, BRIGHT_GREEN, (bobber_x, bobber_y), 7, 2
        )

        # Плавающие рыбы.
        for fish in fishes:
            draw_fish(screen, fish, small_font)

        # Верхняя панель со статистикой.
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 60))
        pygame.draw.line(screen, GREEN, (0, 60), (WIDTH, 60), 2)

        stats_text = font.render(
            "Монеты: " + str(get_coins(game))
            + "  |  Рыб в садке: " + str(len(get_inventory(game))),
            True,
            BRIGHT_GREEN
        )
        screen.blit(stats_text, (16, 18))

        # Подсказки управления вместо чужих игровых кнопок.
        controls_text = small_font.render(
            "ПРОБЕЛ: ловить   S: продать   I: улов",
            True,
            BRIGHT_GREEN
        )
        screen.blit(
            controls_text,
            (WIDTH - controls_text.get_width() - 18, 22)
        )

        # Панель инвентаря появляется по нажатию I.
        if show_inventory:
            draw_inventory(screen, font, small_font, get_inventory(game))

        # Нижняя строка сообщений.
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 44, WIDTH, 44))
        pygame.draw.line(
            screen, GREEN,
            (0, HEIGHT - 44), (WIDTH, HEIGHT - 44), 1
        )
        message_surface = small_font.render(message, True, BRIGHT_GREEN)
        screen.blit(message_surface, (16, HEIGHT - 31))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
