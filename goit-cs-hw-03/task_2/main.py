from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError


# Підключення до MongoDB
try:
    # Створення об'єкта клієнта для підключення до MongoDB на локальному хості
    client = MongoClient("mongodb://localhost:27017/")

    # Вибір бази даних "cat_database"
    db = client["cat_database"]

    # Вибір колекції "cats" у базі даних
    collection = db["cats"]

    # Перевірка з'єднання, виконавши команду 'ismaster'
    client.admin.command('ismaster')
    print("MongoDB підключено успішно")

except ConnectionFailure:
    # Якщо з'єднання не вдалось виводимо повідомлення і завершуємо виконання
    print("Не вдалося підключитися до MongoDB, перевірте з'єднання")
    exit()


def db_operation_error(func):
    """
    Декоратор для обробки помилок, які виникають під час взаємодії з MongoDB.
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PyMongoError as e:
            print(f"Помилка при роботі з MongoDB: {e}")
        except ValueError as e:
            print(f"Помилка введення: {e}")
        return None
    return inner

@db_operation_error
def create_cat(name: str, age: int, features: list[str]):
    """
    Створює новий запис про кота в колекції

    name (str): Ім'я кота
    age (int): Вік кота. Перевіряється, щоб вік не був від'ємним
    features (list[str]): Список особливостей кота
    """
    # Перевірка коректності віку: вік має бути невід'ємним
    if age < 0:
        print("Вік не може бути від'ємним.")
        return
    
    # Створення документа для вставки
    cat = {"name": name, "age": age, "features": features}

    # Вставка документа в колекцію
    collection.insert_one(cat)
    print(f"Кицька {name} додана до бази")

@db_operation_error
def read_all_cats():
    """
    Знаходить та виводить всі записи (документи) про котів у колекції
    """
    # Отримуємо всі документи з колекції "cats"
    cats = collection.find()
    print("В базі маємо такі записи:")
    # Ітеруємося по кожному документу та виводимо його
    for cat in cats:
        print(cat)

@db_operation_error
def read_cat_by_name(name: str):
    """
    Знаходить та виводить запис про кота за заданим ім'ям.
    
    Аргументи:
    name (str): Ім'я кота для пошуку.
    """
    # Знаходимо документ, де значення поля "name" відповідає заданому імені
    cat = collection.find_one({"name": name})
    # Перевірка, чи знайдено документ
    if cat:
        print(cat)
    else:
        print(f"Кицьку на ім'я {name} не знайдено")

@db_operation_error
def update_cat_age(name: str, new_age: int):
    """
    Оновлює вік кота за заданим ім'ям.
    
    Аргументи:
    name (str): Ім'я кота для пошуку.
    new_age (int): Новий вік кота.
    """
    # Перевірка коректності нового віку
    if new_age < 0:
        print("Вік не може бути від'ємним.")
        return
    # Оновлення поля "age" в документі, де значення "name" відповідає заданому
    result = collection.update_one({"name": name}, {"$set": {"age": new_age}})
    # Перевірка, чи оновлено документ
    if result.matched_count > 0:
        print(f"Вік кота '{name}' оновлено: '{new_age}'")
    else:
        print(f"Кота на ім'я '{name}' не знайдено")

@db_operation_error
def add_feature_to_cat(name: str, feature: str):
    """
    Додає нову характеристику до списку особливостей кота за заданим ім'ям.
    
    Аргументи:
    name (str): Ім'я кота для пошуку.
    feature (str): Новий атрибут, який додається до списку особливостей кота.
    """
    # Додаємо нову особливість до масиву "features" у відповідному документі
    result = collection.update_one({"name": name}, {"$push": {"features": feature}})
    # Перевірка, чи оновлено документ
    if result.matched_count > 0:
        print(f"Кицькі '{name}' було додано особливість {feature}")
    else:
        print(f"Кицьку на ім'я {name} не знайдено")

@db_operation_error
def delete_cat(name: str):
    """
    Видаляє запис про кота за заданим ім'ям.
    
    Аргументи:
    name (str): Ім'я кота для пошуку.
    """
    # Видалення документа, де значення "name" відповідає заданому
    result = collection.delete_one({"name": name})
    # Перевірка, чи видалено документ
    if result.deleted_count > 0:
        print(f"Кицька {name} була видалена з бази")
    else:
        print(f"Кицьку на ім'я {name} не знайдено")

@db_operation_error
def delete_all_cats():
    """
    Видаляє всі записи (документи) про котів у колекції після підтвердження.
    """
    # Підтвердження дії видалення всіх записів
    confirm = input("Ви впевнені, що хочете видалити всі записи? (так/ні): ").strip().lower()
    if confirm != "так":
        print("Видалення скасовано.")
        return
    # Видалення всіх документів у колекції
    result = collection.delete_many({})
    print(f"Всі записи було видалено. Загальна кількість видалених записів: {result.deleted_count}")

def main():
    """
    Основна функція, яка забезпечує взаємодію з користувачем та дозволяє виконувати різні операції з даними в MongoDB.
    """
    while True:
        # Виведення списку доступних дій
        print("\nДоступні операції:")
        print("1 - Створити запис")
        print("2 - Показати всі записи")
        print("3 - Пошук запису за ім'ям кота")
        print("4 - Оновити вік кота")
        print("5 - Додати особливість")
        print("6 - Видалити запис")
        print("7 - Видалити всі записи")
        print("8 - Вийти")
        choice = input("Ваш вибір: ")

        # Виконання дії відповідно до вибору користувача
        match choice:
            case "1":
                # Створення нового запису про кота
                name = input("Вкажіть ім'я: ").strip()
                if not name:
                    print("Ім'я не може бути порожнім.")
                    continue
                try:
                    age = int(input("Вкажіть вік: "))
                except ValueError:
                    print("Вік повинен бути числом.")
                    continue
                # Створення списку особливостей кота
                features = [f.strip() for f in input("Вкажіть особливості (через кому): ").split(",")]
                create_cat(name, age, features)
            case "2":
                # Виведення всіх записів про котів
                read_all_cats()
            case "3":
                # Пошук кота за ім'ям
                name = input("Вкажіть ім'я: ").strip()
                read_cat_by_name(name)
            case "4":
                # Оновлення віку кота за ім'ям
                name = input("Вкажіть ім'я: ").strip()
                try:
                    new_age = int(input("Вкажіть вік: "))
                except ValueError:
                    print("Вік повинен бути числом.")
                    continue
                update_cat_age(name, new_age)
            case "5":
                # Додавання нової особливості коту за ім'ям
                name = input("Вкажіть ім'я: ").strip()
                feature = input("Вкажіть особливість: ").strip()
                add_feature_to_cat(name, feature)
            case "6":
                # Видалення запису про кота за ім'ям
                name = input("Вкажіть ім'я: ").strip()
                delete_cat(name)
            case "7":
                # Видалення всіх записів про котів після підтвердження
                delete_all_cats()
            case "8":
                # Вихід з програми
                break
            case _:
                print("Не вірна команда, спробуйте ще.")

if __name__ == "__main__":
    try:
        # Виконання головної функції
        main()
    finally:
        # Закриття підключення до MongoDB перед завершенням роботи
        client.close()
        print("Підключення до MongoDB закрито")