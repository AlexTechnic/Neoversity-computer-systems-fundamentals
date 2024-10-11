import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt

# Функція для завантаження тексту за URL
def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching text: {e}")
        return None

# Функція для видалення знаків пунктуації
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))

# Map-функція для підрахунку частоти слів
def map_function(word):
    return word, 1

# Shuffle-функція для групування однакових слів
def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

# Reduce-функція для підсумування кількості слів
def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

# Виконання MapReduce
def map_reduce(text, search_words=None):
    # Видалення знаків пунктуації
    text = remove_punctuation(text)
    words = text.split()

    # Якщо задано список слів для пошуку, враховувати тільки ці слова
    if search_words:
        words = [word for word in words if word in search_words]

    # Паралельний Мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)

# Функція для візуалізації результатів
def visualize_top_words(word_counts, top_n=10):
    """
    Візуалізує топ N слів за частотою їх використання.
    """
    # Сортуємо слова за частотою використання
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    # Отримуємо окремі списки слів і їхніх частот
    words = [word for word, count in sorted_word_counts]
    counts = [count for word, count in sorted_word_counts]
    
    # Відображаємо результати у вигляді стовпчикової діаграми
    plt.figure(figsize=(10, 5))  # Розмір графіка
    plt.bar(words, counts, color='skyblue')  # Будуємо діаграму
    plt.title('Top Words by Frequency')  # Заголовок графіка
    plt.xlabel('Words')  # Підпис осі X
    plt.ylabel('Frequency')  # Підпис осі Y
    plt.xticks(rotation=45)  # Повертаємо слова для зручності читання
    plt.show()  # Відображаємо графік

# Головний блок коду
if __name__ == '__main__':
    # Вхідний текст для обробки за URL
    url = "https://www.gutenberg.org/files/1342/1342-0.txt"  # Приклад  (PRIDE and PREJUDICE by Jane Austen)
    text = get_text(url)
    
    if text:
        # Виконання MapReduce на вхідному тексті
        search_words = None  # Можна вказати слова для фільтрації, наприклад: ['war', 'peace', 'love']
        result = map_reduce(text, search_words)
        
        # Виведення результатів підрахунку топ-10 слів
        visualize_top_words(result, top_n=10)
    else:
        print("Помилка: Не вдалося отримати вхідний текст.")
