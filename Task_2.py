import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter

import matplotlib.pyplot as plt
import requests


def get_text(url):
    """
    Завантажує текст за вказаною URL-адресою.
    Додано обробку помилок для випадків, коли URL недоступний.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Помилка при завантаженні тексту: {e}")
        return None


def remove_punctuation(text):
    """
    Видаляє знаки пунктуації з тексту.
    """
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    """
    Функція Map: повертає пару (слово, 1).
    """
    return word.lower(), 1  # Приводимо слова до нижнього регістру


def shuffle_function(mapped_values):
    """
    Функція Shuffle: групує значення за ключами.
    """
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    """
    Функція Reduce: підраховує кількість входжень кожного слова.
    """
    key, values = key_values
    return key, sum(values)


def map_reduce(text, search_words=None):
    """
    Виконує MapReduce на тексті.
    Якщо задано search_words, враховує лише ці слова.
    """
    text = remove_punctuation(text)
    words = text.split()

    # Якщо задано список слів для пошуку, враховувати тільки ці слова
    if search_words:
        words = [word for word in words if word.lower() in search_words]

    # Виконати паралельний маппінг за допомогою ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Виконати паралельну редукцію за допомогою ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(result, top_n=10):
    """
    Візуалізує топ-N найчастіше використовуваних слів.
    """
    # Визначення ТОП-N найчастіше використовуваних слів
    top_words = Counter(result).most_common(top_n)

    # Розділення даних на слова та їх частоти
    words, counts = zip(*top_words)

    # Створення графіка
    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color="skyblue")
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title(f"Top {top_n} Most Frequent Words")
    plt.gca().invert_yaxis()  # Перевернути графік, найбільші значення зверху
    plt.show()


if __name__ == "__main__":
    # Вхідний текст для обробки
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    text = get_text(url)

    if text:
        # Виконання MapReduce на вхідному тексті
        result = map_reduce(text)

        # Візуалізація топ-10 слів
        visualize_top_words(result)
