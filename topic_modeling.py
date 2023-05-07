import pandas as pd
import re
import json


from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

from sentence_transformers import SentenceTransformer

from bertopic import BERTopic
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords

DESCRIPTION = "Description"
RANDOM_STATE = 52  # states used 5 | 23 | 52

nltk_stopwords = list(stopwords.words('english'))

# removes any words composed of less than 2 or more than 21 letters.


def two_letters(list_of_tokens):
    two_letter_word = []
    for token in list_of_tokens:
        if len(token) <= 3 or len(token) >= 21:
            two_letter_word.append(token)
    return two_letter_word

# removes a list of words (ie. stopwords) from a tokenized list.


def remove_words(list_of_tokens, list_of_words):
    remaining_tokens = [
        token for token in list_of_tokens if token.strip() not in list_of_words]
    return remaining_tokens

# defines a custom vectorizer class


class CustomVectorizer(CountVectorizer):

    # overwrite the build_analyzer method, allowing one to
    # create a custom analyzer for the vectorizer
    def build_analyzer(self):

        # load stop words using CountVectorizer's built in method
        stop_words = self.get_stop_words()

        # create the analyzer that will be returned by this method
        def analyser(doc):

            lemmatizer = WordNetLemmatizer()

            # apply the preprocessing and tokenzation steps
            doc_clean = doc.lower()
            doc_clean.replace('/', ' ')          # Removes backslashes
            # removes specials characters and leaves only words
            doc_clean = re.sub('\W_', ' ', doc_clean)
            # removes numbers and words concatenated with numbers IE h4ck3r
            doc_clean = re.sub("\S*\d\S*", " ", doc_clean)

            list_of_tokens = word_tokenize(doc_clean)
            # remove stop words and words less than 2 or greater than 21
            two_letter_word = two_letters(list_of_tokens)
            list_of_tokens = remove_words(list_of_tokens, two_letter_word)

            lemmatized_tokens = [
                lemmatizer.lemmatize(t) for t in list_of_tokens]

            # use CountVectorizer's _word_ngrams built in method
            # to remove stop words and extract n-grams
            return(self._word_ngrams(lemmatized_tokens, stop_words))
        return(analyser)


def build_vectorizer_model():
    course_prefixes = [line.rstrip('\n') for line in open(
        'stopwords/course_prefixes.txt')]  # Load .txt file line by line
    ge_areas = [line.rstrip('\n') for line in open(
        'stopwords/ge_areas.txt')]  # Load .txt file line by line
    university_specific_words = [line.rstrip('\n') for line in open(
        'stopwords/calpoly_specific.txt')]  # Load .txt file line by line
    other_words = [line.rstrip('\n') for line in open(
        'stopwords/other_words.txt')]  # Load .txt file line by line

    stopwords_list = nltk_stopwords + course_prefixes + \
        ge_areas + university_specific_words + other_words
    vectorizer = CustomVectorizer(
        ngram_range=(1, 1), stop_words=stopwords_list)
    return vectorizer


def build_topic_model():
    # other good n_neighbors options: 60 | 80
    umap_model = UMAP(n_neighbors=75, random_state=RANDOM_STATE)
    # random_state: 5 | 23 | 52

    topic_model = BERTopic(
        language="english",
        # nr_topics="auto",
        diversity=0.5,
        umap_model=umap_model
    )
    topic_model.save("BERTopic_model")
    return topic_model


def write_topics(topics, topic_name):
    with open(topic_name, "w") as outfile:
        json.dump(topics, outfile)


if __name__ == "__main__":
    df = pd.read_csv("courses.csv")
    doc_corpus = df[DESCRIPTION].tolist()
    # sentences_corpus = ".".join(doc_corpus).split(".")
    # sentences_corpus = [sentence.strip() for sentence in sentences_corpus]

    NUM_TOPICS_OPTIONS = [10, 20, 25, 30]
    TOP_N_WORDS_OPTIONS = [5, 10, 15, 20]
    # TOP_N_WORDS_OPTIONS = [10]

    topic_model = build_topic_model()
    for top_n_words in TOP_N_WORDS_OPTIONS:
        for num_topics in NUM_TOPICS_OPTIONS:

            topic_model = BERTopic.load("BERTopic_model")
            topics, probs = topic_model.fit_transform(doc_corpus)

            vectorizer_model = build_vectorizer_model()
            topic_model.update_topics(
                doc_corpus, vectorizer_model=vectorizer_model, top_n_words=top_n_words)
            topic_model.reduce_topics(doc_corpus, nr_topics=num_topics)

            topics = topic_model.get_topics()
            write_topics(
                topics, f'topic-models/rs-{RANDOM_STATE}/{num_topics}topics-{top_n_words}words.json')
    # num_topics = len(topics)
    # # print(topics)

    # hierarchical_topics = topic_model.hierarchical_topics(doc_corpus)

    # print(topic_model.get_topic_info())
    # fig = topic_model.visualize_topics()
    # fig2 = topic_model.visualize_barchart(top_n_topics=num_topics, n_words=N_WORDS)
    # fig3 = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
    # fig.show()
    # fig2.show()
    # fig3.show()
