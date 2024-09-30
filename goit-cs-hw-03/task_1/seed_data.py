from faker import Faker
import psycopg2

# Підключення до бази даних PostgreSQL
conn = psycopg2.connect(
    dbname="task_management",
    user="ваше_ім'я_користувача",  # Вкажіть ваш логін до PostgreSQL
    password="ваш_пароль",  # Вкажіть ваш пароль до PostgreSQL
    host="localhost"
)
cursor = conn.cursor()

# Ініціалізація Faker
fake = Faker()

# Заповнення таблиці users випадковими значеннями
try:
    for _ in range(10):  # Створення 10 користувачів
        fullname = fake.name()
        email = fake.email()
        cursor.execute(
            "INSERT INTO users (fullname, email) VALUES (%s, %s)",
            (fullname, email)
        )
    print("Користувачі додані успішно.")
    
    # Заповнення таблиці tasks випадковими значеннями
    for _ in range(20):  # Створення 20 завдань
        title = fake.sentence()
        description = fake.text()
        status_id = fake.random_int(min=1, max=3)  # статуси мають id від 1 до 3
        user_id = fake.random_int(min=1, max=10)   # користувачі мають id від 1 до 10
        cursor.execute(
            "INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s)",
            (title, description, status_id, user_id)
        )
    print("Завдання додані успішно.")
except Exception as e:
    print(f"Помилка під час вставки даних: {e}")
finally:
    # Збереження змін і закриття з'єднання
    conn.commit()
    cursor.close()
    conn.close()