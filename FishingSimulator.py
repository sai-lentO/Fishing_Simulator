import random
import pygame


COMMON_FISH = [
    ["Карась", 10],
    ["Плотва", 15],
    ["Лещ", 20]
]

UNCOMMON_FISH = [
    ["Окунь", 30],
    ["Линь", 35]
]

RARE_FISH = [
    ["Щука", 60],
    ["Судак", 75]
]

EPIC_FISH = [
    ["Сом", 120],
    ["Осётр", 160]
]

LEGENDARY_FISH = [
    ["Золотая рыба", 350]
]


def catch_fish(bite_chance, luck):
    if random.randint(1, 100) > bite_chance:
        return None

    rarity_roll = random.randint(1, 100) + luck

    if rarity_roll > 100:
        rarity_roll = 100

    if rarity_roll <= 50:
        selected_fish = random.choice(COMMON_FISH)
        rarity = "Обычная"
    elif rarity_roll <= 75:
        selected_fish = random.choice(UNCOMMON_FISH)
        rarity = "Необычная"
    elif rarity_roll <= 90:
        selected_fish = random.choice(RARE_FISH)
        rarity = "Редкая"
    elif rarity_roll <= 98:
        selected_fish = random.choice(EPIC_FISH)
        rarity = "Эпическая"
    else:
        selected_fish = random.choice(LEGENDARY_FISH)
        rarity = "Легендарная"

    return [selected_fish[0], rarity, selected_fish[1]]


def add_fish(inventory, fish):
    inventory.append(fish)


def sell_fish(inventory):
    earned_money = 0

    for fish in inventory:
        earned_money = earned_money + fish[2]

    inventory.clear()
    return earned_money


def upgrade_bite(money, bite_level):
    max_level = 7

    if bite_level >= max_level:
        return money, bite_level, "Шанс поклёвки уже максимальный!"

    price = 50 + (bite_level - 1) * 50

    if money >= price:
        money = money - price
        bite_level = bite_level + 1
        message = "Шанс поклёвки улучшен!"
    else:
        message = "Недостаточно денег для улучшения."

    return money, bite_level, message


def upgrade_luck(money, luck_level):
    max_level = 4

    if luck_level >= max_level:
        return money, luck_level, "Удача уже максимальная!"
      
      price = 100 + luck_level * 75

    if money >= price:
        money = money - price
        luck_level = luck_level + 1
        message = "Удача улучшена!"
    else:
        message = "Недостаточно денег для улучшения."

    return money, luck_level, message


pygame.init()

WIDTH = 900
HEIGHT = 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Симулятор рыбалки")

font = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 21)

BACKGROUND = (35, 91, 125)
WHITE = (255, 255, 255)
LIGHT_BLUE = (175, 220, 240)

money = 100
inventory = []

bite_level = 1
luck_level = 0

bite_chance = 60 + (bite_level - 1) * 5
luck = luck_level * 5

message = "Добро пожаловать! Нажмите SPACE, чтобы рыбачить."
clock = pygame.time.Clock()


def draw_text(text, x, y, text_font=small_font, color=WHITE):
    text_image = text_font.render(text, True, color)
    screen.blit(text_image, (x, y))


def draw_screen():
    screen.fill(BACKGROUND)

    draw_text("СИМУЛЯТОР РЫБАЛКИ", 285, 25, font)

    draw_text("Деньги: " + str(money), 35, 100)
    draw_text("Шанс поклёвки: " + str(bite_chance) + "%", 35, 135)
    draw_text("Удача: " + str(luck), 35, 170)

    draw_text("ИНВЕНТАРЬ", 35, 235, font)
    draw_text("Количество рыб: " + str(len(inventory)), 35, 275)

    if len(inventory) == 0:
        draw_text("Пока ничего не поймано.", 35, 315)
    else:
        draw_text("Последний улов:", 35, 315)

        for i in range(min(5, len(inventory))):
            fish = inventory[-1 - i]
            fish_text = fish[0] + " | " + fish[1] + " | " + str(fish[2]) + " монет"
            draw_text(fish_text, 35, 350 + i * 27)

    draw_text("УПРАВЛЕНИЕ", 570, 235, font)
    draw_text("SPACE — забросить удочку", 570, 285)
    draw_text("S — продать весь улов", 570, 320)
    draw_text("1 — улучшить поклёвку", 570, 355)
    draw_text("2 — улучшить удачу", 570, 390)
    draw_text("ESC — выйти из игры", 570, 425)

    draw_text("СООБЩЕНИЕ", 35, 535, font, LIGHT_BLUE)
    draw_text(message, 35, 575)

    pygame.display.update()


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                bite_chance = 60 + (bite_level - 1) * 5
                luck = luck_level * 5

                fish = catch_fish(bite_chance, luck)

                if fish is None:
                    message = "Поклёвки не было. Попробуйте ещё раз!"
                else:
                    add_fish(inventory, fish)
                    message = "Улов: " + fish[0] + " (" + fish[1] + ") — " + str(fish[2]) + " монет."

            elif event.key == pygame.K_s:
                if len(inventory) > 0:
                    earned_money = sell_fish(inventory)
                    money = money + earned_money
                    message = "Рыба продана! Получено " + str(earned_money) + " монет."
                else:
                    message = "Инвентарь пуст — нечего продавать."

            elif event.key == pygame.K_1:
                money, bite_level, message = upgrade_bite(money, bite_level)
                bite_chance = 60 + (bite_level - 1) * 5

            elif event.key == pygame.K_2:
                money, luck_level, message = upgrade_luck(money, luck_level)
                luck = luck_level * 5

    draw_screen()
    clock.tick(60)


pygame.quit()
