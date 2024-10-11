import os
import multiprocessing
import time
import glob

def search_in_files(file_list, keywords, result_queue):
    """
    Функція для пошуку ключових слів у списку файлів.
    
    :param file_list: Список файлів для обробки.
    :param keywords: Список ключових слів для пошуку.
    :param result_queue: Черга для зберігання результатів пошуку.
    """
    result_dict = {}  # Словник для зберігання результатів поточного процесу

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
                        if word not in result_dict:
                            result_dict[word] = {'files': [], 'count': 0}  # Ініціалізуємо структуру, якщо ключа немає
                        result_dict[word]['files'].append(file_path)  # Додаємо шлях до файлу
                        result_dict[word]['count'] += found_words_count[word]  # Додаємо кількість знайдених слів
        except Exception as e:
            # Обробка винятків при відкритті файлу
            print(f"Помилка при обробці файлу {file_path}: {e}")

    # Відправляємо результати поточного процесу в чергу
    result_queue.put(result_dict)

def multiprocessing_search(files, keywords):
    """
    Функція для запуску пошуку в багатопроцесорному режимі.
    
    :param files: Список файлів для обробки.
    :param keywords: Список ключових слів для пошуку.
    :return: Словник результатів пошуку.
    """
    num_processes = min(4, len(files))  # Кількість процесів не більше кількості файлів
    processes = []  # Список для зберігання процесів
    result_queue = multiprocessing.Queue()  # Черга для обміну результатами

    # Розподіл файлів між процесами
    files_per_process = len(files) // num_processes  # Кількість файлів на кожен процес
    for i in range(num_processes):
        start_index = i * files_per_process  # Початковий індекс для процесу
        # Визначаємо кінцевий індекс; для останнього процесу беремо залишок
        end_index = (i + 1) * files_per_process if i != num_processes - 1 else len(files)
        process_files = files[start_index:end_index]  # Вибір файлів для процесу
        # Створення нового процесу
        p = multiprocessing.Process(target=search_in_files, args=(process_files, keywords, result_queue))
        processes.append(p)  # Додаємо процес до списку
        p.start()  # Запускаємо процес

    for p in processes:
        p.join()  # Чекаємо завершення всіх процесів

    # Збираємо результати з черги
    result_dict = {}
    while not result_queue.empty():
        process_result = result_queue.get()
        for word, data in process_result.items():
            if word not in result_dict:
                result_dict[word] = {'files': [], 'count': 0}  # Ініціалізуємо структуру, якщо ключа немає
            result_dict[word]['files'].extend(data['files'])  # Додаємо файли
            result_dict[word]['count'] += data['count']  # Додаємо кількість знайдених слів

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
        results = multiprocessing_search(files, keywords)  # Викликаємо функцію пошуку
        end_time = time.time()  # Записуємо час завершення виконання

        print("Результати багатопроцесорного пошуку:")
        # Виводимо результати пошуку
        for word, data in results.items():
            print(f"{word}: {data['files']} (Знайдено слів: {data['count']})")

        # Виводимо час виконання
        print(f"Час виконання: {end_time - start_time:.2f} секунд")