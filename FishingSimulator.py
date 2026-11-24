import pygame
import random

# Список доступных рыб
FISH = [
    {"name": "Карась", "price": 10},
    {"name": "Окунь", "price": 20},
    {"name": "Щука", "price": 35},
    {"name": "Сом", "price": 50}
]


# Создание игрока
def create_game():
    game = {
        "coins": 0,
        "inventory": []
    }
    return game


# Ловля рыбы
def catch_fish(game):
    if random.randint(1, 100) <= 80:
        fish = random.choice(FISH)
        game["inventory"].append(fish)

        return fish

    return None


# Продажа рыбы
def sell_fish(game):
    if len(game["inventory"]) == 0:
        return 0

    total = 0

    for fish in game["inventory"]:
        total = total + fish["price"]

    game["coins"] = game["coins"] + total
    game["inventory"] = []

    return total


# Получение инвентаря
def get_inventory(game):
    return game["inventory"]


# Получение баланса
def get_coins(game):
    return game["coins"]


# Управление игроком
def handle_player_input(event, game):

    if event.type == pygame.QUIT:
        return "exit"

    if event.type == pygame.KEYDOWN:

        if event.key == pygame.K_SPACE:
            fish = catch_fish(game)

            if fish is None:
                return "Рыба не клюнула!"

            return "Ты поймал: " + fish["name"]

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

            return result

        elif event.key == pygame.K_ESCAPE:
            return "exit"

    return None
