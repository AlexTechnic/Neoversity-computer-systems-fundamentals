import psycopg2

# Підключення до бд PostgreSQL
conn = psycopg2.connect(
    dbname="task_management",
    user="ваше_ім'я_користувача",  # Логін до PostgreSQL
    password="ваш_пароль",  # Пароль до PostgreSQL
    host="localhost"
)
cursor = conn.cursor()

# Створення таблиць
try:
    # Створення таблиці users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            fullname VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        );
    """)
    
    # Створення таблиці status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        );
    """)

    # Додавання початкових статусів
    cursor.execute("""
        INSERT INTO status (name) VALUES ('new'), ('in progress'), ('completed')
        ON CONFLICT (name) DO NOTHING;  -- Уникнення дублювання статусів
    """)
    
    # Створення таблиці tasks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            status_id INTEGER REFERENCES status(id),
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    
    print("Таблиці створено успішно.")
except Exception as e:
    print(f"Помилка під час створення таблиць: {e}")
finally:
    # Збереження змін і закриття з'єднання
    conn.commit()
    cursor.close()
    conn.close()