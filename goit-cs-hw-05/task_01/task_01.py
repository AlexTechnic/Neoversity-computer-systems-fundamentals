import argparse
import asyncio
import os
import shutil
import logging
from pathlib import Path


# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def copy_file(file_path: Path, output_folder: Path):
    """
    Асинхронна функція для копіювання файлів до підпапок на основі розширення.

    :param file_path: Шлях до файлу, який потрібно скопіювати.
    :param output_folder: Шлях до папки, куди буде скопійовано файл.
    """
    try:
        ext = file_path.suffix[1:]  # Отримуємо розширення файлів
        target_folder = output_folder / ext  # Визначаємо цільову папку на основі розширення

        # Створення підпапки якщо вона не існує
        target_folder.mkdir(parents=True, exist_ok=True)

        # Копіювання файлу
        shutil.copy(file_path, target_folder / file_path.name)
        logging.info(f"Файл {file_path.name} скопійовано до {target_folder}")
    except Exception as e:
        logging.error(f"Помилка під час копіювання файлу {file_path}: {e}")

async def read_folder(source_folder: Path, output_folder: Path):
    """
    Асинхронна функція для читання файлів з вихідної папки.

    :param source_folder: Шлях до вихідної папки.
    :param output_folder: Шлях до папки для збереження файлів.
    """
    tasks = []  # Список для зберігання асинхронних завдань

    # Рекурсивний обхід усіх файлів у вихідній папці
    for root, _, files in os.walk(source_folder):
        for file in files:
            file_path = Path(root) / file  # Формуємо повний шлях до файлу
            tasks.append(copy_file(file_path, output_folder))  # Додаємо задачу копіювання

    # Виконуємо всі завдання асинхронно
    await asyncio.gather(*tasks)

def main():
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням")
    parser.add_argument("source_folder", type=str, help="Вихідна папка з файлами")
    parser.add_argument("output_folder", type=str, help="Папка для збереження файлів")

    args = parser.parse_args()
    source_folder = Path(args.source_folder)  # Конвертуємо шлях до вихідної папки
    output_folder = Path(args.output_folder)  # Конвертуємо шлях до папки призначення

    # Перевірка існування вихідної папки
    if not source_folder.exists() or not source_folder.is_dir():
        logging.error(f"Папка {source_folder} не існує або не є папкою.")
        return

    # Запуск асинхронної функції для читання папки
    asyncio.run(read_folder(source_folder, output_folder))
    logging.info("Сортування файлів завершено.")

if __name__ == "__main__":
    main()
