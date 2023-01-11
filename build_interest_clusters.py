import json
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

JSON_PATH="topic-models/rs-23/30topics-20words.json"

if __name__ == "__main__":
    # load json file
    with open(f'{JSON_PATH}', 'r') as f:
        data = json.load(f)
    # remove -1 index (topic outliers)
    del data["-1"]

    num_words = 20
    standard_scaling_factor = 1.5 # lower value means a greater difference in scaling
    for index, words in data.items():
        topic_dict = {}
        for word, frequency in words:
            topic_dict[word] = frequency if int(index) < 10 else words[10][1] 

        wordcloud = WordCloud(max_font_size=70, background_color='white', colormap="winter")

        wordcloud.generate_from_frequencies(topic_dict)

        plt.figure()
        plt.title('Cluster {}'.format(index))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig(f'wordclouds/topic{index}.png')
