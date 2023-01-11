# Corpus Processing
import re
import nltk.corpus
from unidecode import unidecode
from nltk.tokenize import word_tokenize
from nltk import SnowballStemmer
from nltk.stem import WordNetLemmatizer

# removes a list of words (ie. stopwords) from a tokenized list.
def remove_words(list_of_tokens, list_of_words):
    remaining_tokens = [
        token for token in list_of_tokens if token.strip() not in list_of_words]
    return remaining_tokens

# removes any words composed of less than 2 or more than 21 letters.


def two_letters(list_of_tokens):
    two_letter_word = []
    for token in list_of_tokens:
        if len(token) <= 2 or len(token) >= 21:
            two_letter_word.append(token)
    return two_letter_word

# applies stemming to a list of tokenized words


def apply_stemming(list_of_tokens, stemmer):
    return [stemmer.stem(token) for token in list_of_tokens]

# lemmatizes each word.


def apply_lemmatization(list_of_tokens, lemmatizer):
    return [lemmatizer.lemmatize(token) for token in list_of_tokens]

def process_corpus(corpus, language="english"):
    stopwords = nltk.corpus.stopwords.words(language)
    param_stemmer = SnowballStemmer(language)
    lemmatizer = WordNetLemmatizer()
    course_prefixes = [line.rstrip('\n') for line in open(
        'lists/course_prefixes.txt')]  # Load .txt file line by line
    other_words = [line.rstrip('\n') for line in open(
        'lists/other_words.txt')]  # Load .txt file line by line

    tags_to_remove = ['IN', 'TO', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    for document in corpus:
        index = corpus.index(document)

        corpus[index] = corpus[index].replace(
            ',', '')          # Removes commas
        corpus[index] = corpus[index].replace(
            '/', ' ')          # Removes backslashes
        corpus[index] = corpus[index].rstrip(
            '\n')              # Removes line breaks
        # Makes all letters lowercase
        corpus[index] = corpus[index].casefold()

        # removes specials characters and leaves only words
        corpus[index] = re.sub('\W_', ' ', corpus[index])
        # removes numbers and words concatenated with numbers IE h4ck3r
        corpus[index] = re.sub("\S*\d\S*", " ", corpus[index])

        list_of_tokens = word_tokenize(corpus[index])

        # remove stop words and words less than 2 or greater than 21
        two_letter_word = two_letters(list_of_tokens)
        list_of_tokens = remove_words(list_of_tokens, stopwords)
        list_of_tokens = remove_words(list_of_tokens, two_letter_word)

        # remove words by part of speech
        list_of_tokens = [token[0] for token in nltk.pos_tag(
            list_of_tokens) if token[1] not in tags_to_remove]

        # remove other stopwords
        list_of_tokens = remove_words(list_of_tokens, course_prefixes)
        list_of_tokens = remove_words(list_of_tokens, other_words)

        # list_of_tokens = apply_stemming(list_of_tokens, param_stemmer)
        list_of_tokens = apply_lemmatization(list_of_tokens, lemmatizer)
        list_of_tokens = remove_words(list_of_tokens, other_words)

        corpus[index] = " ".join(list_of_tokens)

        if "majors" in list_of_tokens:
            print(list_of_tokens)
            quit()

        corpus[index] = unidecode(corpus[index])

    return corpus