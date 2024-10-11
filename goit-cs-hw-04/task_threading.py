import os
import threading
import time
import glob

def search_in_files(file_list, keywords, result_dict, lock):
    """
    Функція для пошуку ключових слів у списку файлів.
    
    :param file_list: Список файлів для обробки.
    :param keywords: Список ключових слів для пошуку.
    :param result_dict: Словник для зберігання результатів пошуку.
    :param lock: Об'єкт Lock для синхронізації доступу до словника.
    """
    for file_path in file_list:
        try:
            # Відкриття файлу для читання
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()  # Читання вмісту файлу
                # Ініціалізація лічильника знайдених слів для цього файлу
                found_words_count = {word: 0 for word in keywords}
                # Перевірка наявності кожного ключового слова у вмісті файлу
                for word in keywords:
                    if word in content:
                        found_words_count[word] += content.count(word)  # Підрахунок кількості знайдених слів
                        # Використання Lock для синхронізації доступу до словника
                        with lock:
                            if word not in result_dict:
                                result_dict[word] = {'files': [], 'count': 0}  # Ініціалізуємо структуру, якщо ключа немає
                            result_dict[word]['files'].append(file_path)  # Додаємо шлях до файлу
                            result_dict[word]['count'] += found_words_count[word]  # Додаємо кількість знайдених слів
        except Exception as e:
            # Обробка винятків при відкритті файлу
            print(f"Помилка при обробці файлу {file_path}: {e}")

def threaded_search(files, keywords):
    """
    Функція для запуску пошуку в багатопотоковому режимі.
    
    :param files: Список файлів для обробки.
    :param keywords: Список ключових слів для пошуку.
    :return: Словник результатів пошуку.
    """
    num_threads = min(4, len(files))  # Кількість потоків не більше кількості файлів
    threads = []  # Список для зберігання потоків
    result_dict = {}  # Словник для зберігання результатів
    lock = threading.Lock()  # Об'єкт Lock для синхронізації

    # Розподіл файлів між потоками
    files_per_thread = len(files) // num_threads  # Кількість файлів на кожен потік
    for i in range(num_threads):
        start_index = i * files_per_thread  # Початковий індекс для потоку
        # Визначаємо кінцевий індекс; для останнього потоку беремо залишок
        end_index = (i + 1) * files_per_thread if i != num_threads - 1 else len(files)
        thread_files = files[start_index:end_index]  # Вибір файлів для потоку
        # Створення нового потоку
        t = threading.Thread(target=search_in_files, args=(thread_files, keywords, result_dict, lock))
        threads.append(t)  # Додаємо потік до списку
        t.start()  # Запускаємо потік

    for t in threads:
        t.join()  # Чекаємо завершення всіх потоків

    return result_dict  # Повертаємо результати пошуку

if __name__ == "__main__":
    # Вказуємо шлях до директорії, де знаходяться текстові файли
    directory_path = 'D:/Programming/GoIT Neoversity/Neoversity-computer-systems-fundamentals/Neoversity-computer-systems-fundamentals/goit-cs-hw-04'
    os.chdir(directory_path)  # Змінюємо робочу директорію на вказану
    print("Поточна директорія:", os.getcwd())
    
    # Шукати файли .txt у вказаній директорії
    files = glob.glob('*.txt')
    keywords = ['CDE', 'QWERTY']  # Ключові слова для пошуку

    # Перевірка наявності файлів
    if not files:
        print("Не знайдено жодного файлу з розширенням .txt у поточній директорії.")
    else:
        start_time = time.time()  # Записуємо час початку виконання
        results = threaded_search(files, keywords)  # Викликаємо функцію пошуку
        end_time = time.time()  # Записуємо час завершення виконання

        print("Результати багатопотокового пошуку:")
        # Виводимо результати пошуку
        for word, data in results.items():
            print(f"{word}: {data['files']} (Знайдено слів: {data['count']})")

        # Виводимо час виконання
        print(f"Час виконання: {end_time - start_time:.2f} секунд")