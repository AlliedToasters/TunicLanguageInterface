import numpy as np
import string
import json

def get_freq_distibution(
        letters, words, sentences
    ):
    bag_of_words = []
    for sentence in sentences:
        if not (isinstance(sentence, str) and sentence.isnumeric()):
            # these are likely test sentences
            continue
        sentence_data = sentences[sentence]
        components = sentence_data["components"]
        _words = [item["content"] for item in components if item["type"] == "word"]
        bag_of_words.extend(_words)
    bag_of_letters = []
    for i, word in enumerate(bag_of_words):
        word_data = words[word]
        letter_ids = word_data["letter_ids"]
        bag_of_letters.extend(letter_ids)

    word_frequency, word_counts = np.unique(bag_of_words, return_counts=True)
    letter_frequency, letter_counts = np.unique(bag_of_letters, return_counts=True)

    return word_frequency, word_counts, letter_frequency, letter_counts

def load_english_word_freq_sample(english_sample_path = "english_sample.txt"):

    with open(english_sample_path, "r") as f:
        text = f.read()

    words = text.split()
    words = [word.lower() for word in words]
    # remove tokens that contain punctuation
    words = [word for word in words if not any([char in string.punctuation for char in word])]
    word_counts = np.unique(words, return_counts=True)
    word_frequency = word_counts[0]
    word_counts = word_counts[1]

    print (f"The most common word is {word_frequency[np.argmax(word_counts)]} with {np.max(word_counts)} occurrences.")
    sorted_word_frequency = word_frequency[np.argsort(word_counts)][::-1]
    sorted_word_counts = np.sort(word_counts)[::-1]
    n_to_print = 25
    print(f"The {n_to_print} most common words are:")
    for i in range(n_to_print):
        print(f"{sorted_word_frequency[i]}: {sorted_word_counts[i]}")

    return sorted_word_frequency, sorted_word_counts

def translate_words_from_english_freq(
        letters, 
        words, 
        sentences,
        note_key="known",
        commit:bool=True
    ):
    import streamlit as st
    sorted_ewf, sorted_ewc = load_english_word_freq_sample()
    word_freq, word_count, _, _ = get_freq_distibution(letters, words, sentences)
    sort_indices = np.argsort(word_count)[::-1]
    words_by_freq = [str(word) for word in word_freq[sort_indices]]
    offset = 0
    for i, word_id in enumerate(words_by_freq):
        word_data = words[word_id] 
        likely_translation = str(sorted_ewf[i - offset]) # offset accounts for "skipped" word matches
        notes = word_data["notes"]
        if note_key in notes:
            known_translation = word_data["translation"]
            print(f"frequency suggested the translation for word {word_id} is {likely_translation}, but it is known to be {known_translation}")
            print("updating offset and skipping")
            offset += 1
            continue
        print(f"frequency suggests the translation for word {word_id} is {likely_translation}")
        word_data["translation"] = likely_translation
        words[word_id] = word_data

        if commit:
            with open("data/words.json", "w") as f:
                json.dump(words, f, indent=2)
