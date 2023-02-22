import json
import pandas as pd
import matplotlib.pyplot as plt
from InterestCluster import InterestCluster
from build_data_dict import build_course_program_dict, build_word_course_dict
from program_decision_support import get_programs
from wordcloud import WordCloud

JSON_PATH = "topic-models-test/rs-23/30topics-20words.json"
PROGRAM = "Program"

def build_ranking_dict():
    df = pd.read_csv('program_courses.csv')
    programs = df[PROGRAM].unique().tolist()
    program_counts = {'count': 0, 'relative_count': 0}
    # use dictionary comprehension to avoid mutating the same dictionary for program counts
    return {key: dict(program_counts) for key in list(set(programs))}

def build_wordclouds():
     # load json file
    with open(f'{JSON_PATH}', 'r') as f:
        data = json.load(f)
    # remove -1 index (topic outliers)
    del data["-1"]

    for index, words in data.items():
        topic_dict = {}
        for word, frequency in words:
            topic_dict[word] = frequency if int(index) < 10 else words[10][1]

        wordcloud = WordCloud(
            max_font_size=70, background_color='white', colormap="winter")

        wordcloud.generate_from_frequencies(topic_dict)

        plt.figure()
        plt.title('Cluster {}'.format(index))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig(f'wordclouds/topic{index}.png')


def generate_program_rankings(path):
    with open(f'{path}.json', 'r') as f:
        topics = json.load(f)
        # remove -1 index (topic outliers)
    del topics["-1"]

    program_ranking_dict = build_ranking_dict()

    interest_clusters = []
    for topic_num, word_data in topics.items():
        words = [word[0] for word in word_data]
        interest_clusters.append(InterestCluster(topic_num, words, program_ranking_dict))

    all_programs = get_programs()

    topic_program_ranking_cts = pd.DataFrame(0, columns=range(0, len(interest_clusters)), index=all_programs)
    topic_program_ranking_relative_cts = pd.DataFrame(0, columns=range(0, len(interest_clusters)), index=all_programs)
    topic_program_ranking_cts.index.name='Programs'
    topic_program_ranking_relative_cts.index.name='Programs'
    
    word_course_dict = build_word_course_dict()
    program_course_dict = build_course_program_dict()

    for cluster in interest_clusters:
        for word in cluster.words:
            courses = word_course_dict[word]
            for course in courses:
                if course in program_course_dict:
                    programs = program_course_dict[course]

                    for program in programs:
                        topic_program_ranking_cts.loc[program, int(cluster.id)] += 1
                        cluster.program_ranking[program]['count'] += 1
    
    for cluster in interest_clusters:
        cluster.calculate_relative_counts()
        for program in all_programs:
            topic_program_ranking_relative_cts.loc[program, int(cluster.id)] = cluster.program_ranking[program]["relative_count"]

    topic_program_ranking_cts.to_csv(f"{path}_program_rankings_ct.csv")
    topic_program_ranking_relative_cts.to_csv(
        f"{path}_program_rankings_relative_ct.csv")

def iterate_through_topic_models():
    # seeds = ["rs-5"]
    seeds = ["rs-23", "rs-52"]
    TOPICS = [10,20,25,30]
    TOP_WORDS = [5, 10, 15, 20]
    for seed in seeds:
        for topic in TOPICS:
            for top_word in TOP_WORDS:
                path = f"topic-models/{seed}/{topic}topics-{top_word}words"
                # print(path)
                generate_program_rankings(path)

if __name__ == "__main__":
    # build_wordclouds()
    iterate_through_topic_models()
  