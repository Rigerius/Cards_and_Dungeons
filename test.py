from database import init_database

if __name__ == "__main__":
    print("Инициализация базы данных...")
    db = init_database()
    print("База данных успешно инициализирована!")

    # Показать содержимое таблиц
    db.connect()

    print("\n=== Карты в базе данных ===")
    cards = db.get_all_cards()
    for card in cards:
        print(f"ID: {card[0]}, Имя: {card[1]}, Тип: {card[10]}")

    print("\n=== Типы слизней ===")
    slimes = db.get_slime_types()
    for slime in slimes:
        print(f"Тип: {slime[1]}, Имя: {slime[2]}, HP: {slime[3]}, Урон: {slime[4]}")

    print("\n=== Данные игрока ===")
    player = db.get_player_data()
    if player:
        print(f"Имя: {player[1]}, HP: {player[2]}, Мана: {player[3]}")

    db.disconnect()