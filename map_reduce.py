from concurrent.futures import ThreadPoolExecutor
import string
from collections import defaultdict
import requests
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

URL = "https://gutenberg.net.au/ebooks01/0100021.txt"


def fetch_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return None


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text, search_words=None):
    text = remove_punctuation(text)
    words = text.split()

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def plot_top_words(word_freq, top_n=10):
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*sorted_words)
    plt.figure(figsize=(10, 8))
    plt.barh(words, counts)
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title(f"Top {top_n} Most Frequent Words")
    plt.xticks(rotation=45)
    plt.gca().invert_yaxis()
    plt.show()


if __name__ == "__main__":
    text = fetch_text(URL)
    if text:
        word_counts = map_reduce(text)
        plot_top_words(word_counts, 20)
    else:
        print("Error: Unable to fetch text")
