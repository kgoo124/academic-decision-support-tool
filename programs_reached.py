from collections import OrderedDict
from itertools import combinations
import json
import math
from pprint import pprint

import pandas as pd
from InterestCluster import InterestCluster
from build_data_dict import build_course_program_dict, build_word_course_dict

from generate_clusters_old import build_ranking_dict
from program_decision_support import aggregate_rankings

import matplotlib.pyplot as plt
import seaborn as sns

# COMBINATION_OPTIONS = [5]
COMBINATION_OPTIONS = [1,2,3,4,5,6]
TOPICS = [30]
# TOPICS = [10,20,25,30]
TOP_WORDS = [20]
NUM_TOP_PROGRAMS_OPTIONS = [3,5,7] # 3,5,7
RANDOM_STATE = 23 # states used 5 | 23 | 52

COLORS_COMBINATION = {
    2: "blue",
    3: "orange",
    4: "purple",
    5: "teal",
}

def sort_aggregated_rankings(aggregated_ranking_dict):
    return sorted(aggregated_ranking_dict.items(),
                          key=lambda x: x[1]['relative_count'], reverse=True)

def calc_reachable_programs(num_combinations=3):
    cluster_nums = list(topics.keys())[1:]

    # get list of all possible combinations
    topic_combinations = list(combinations(cluster_nums, num_combinations))

    # create dictionary where key is the number of top programs
        # values: reachable_programs_set, num_programs_reached, percent_programs_reached
    reachable_programs_dict = {}
    for num_top_programs in NUM_TOP_PROGRAMS_OPTIONS:
        reachable_programs_dict.update({num_top_programs: {"programs_reachable": set(), "num_programs_reached": 0, "percent_programs_reached": 0 }})
    

    total_programs = len(program_ranking_dict.keys())

    # go through every topic combo
    for topic_combos in topic_combinations:

        # aggregate rankings
        aggregated_ranking_dict = OrderedDict()
        for topic in topic_combos:
            aggregated_ranking_dict = aggregate_rankings(aggregated_ranking_dict, interest_clusters[int(topic)].program_ranking)
        sorted_aggregrated_dict = sort_aggregated_rankings(aggregated_ranking_dict)

        # for all top program options
        for num_top_programs in NUM_TOP_PROGRAMS_OPTIONS:
            # add programs into programs reachable set
            top_programs = sorted_aggregrated_dict[:num_top_programs]

            reachable_programs = reachable_programs_dict[num_top_programs]['programs_reachable']
            
            for program, counts in top_programs:
                reachable_programs.add(program)

    # once all topic combos are finished, calculate program reachability metrucs
    for num_top_programs in NUM_TOP_PROGRAMS_OPTIONS:
        reachable_programs = reachable_programs_dict[num_top_programs]['programs_reachable']
        reachable_programs_dict[num_top_programs]['num_programs_reached'] = len(reachable_programs)
        reachable_programs_dict[num_top_programs]['percent_programs_reached'] = len(reachable_programs) * 100 / total_programs
    
    # pprint(reachable_programs_dict)
    # quit()
    return reachable_programs_dict

def visualize_programs_reached(filename):
    programs_reached_df = pd.read_csv(filename)

    # drop UMAP random state column
    programs_reached_df = programs_reached_df.drop("UMAP Random State", axis=1)

    aggregated_programs_reached = programs_reached_df.groupby(["Num Top Programs", "Num Topics", "Num Combinations", "Num Top Words"]).mean()
    aggregated_programs_reached = aggregated_programs_reached.reset_index()
    print(aggregated_programs_reached)
    g = sns.FacetGrid(aggregated_programs_reached, row="Num Topics", col="Num Combinations", hue="Num Top Words")
    g.map(plt.plot, "Num Top Programs", "Reachable Programs %", marker='o')
    fig = g.fig
    fig.subplots_adjust(top=0.9, wspace=0.4)
    fig.suptitle('Reachable Program % Based on Num Topics, Num Combinations, Num Top Programs and Num Top Words')
    l = g.add_legend(title="Num Top Words")
    new_list = range(math.floor(min(aggregated_programs_reached["Num Top Programs"])), math.ceil(max(aggregated_programs_reached["Num Top Programs"]))+1,2)
    plt.xticks(new_list)
    plt.savefig("program_reachability.png")
    quit()


if __name__ == "__main__":
    # visualize_programs_reached("programs_reached_new.csv")
    # # quit()
    rows = []
    for num_topics in TOPICS:
        # ax = plt.subplot()
        # ax.set_title(f"Program Reachability for {num_topics} topics")
        # ax.set_xlabel('Number of Words in Cluster')
        # ax.set_ylabel("% of Reachable Programs")  
        # ax.legend(["2 combinations", "3 combinations", "4 combinations", "5 combinations"]) 
            percents_per_num_words = []
            for num_top_word in TOP_WORDS:
                with open(f'topic-models/rs-23/{num_topics}topics-{num_top_word}words.json') as json_file:
                    topics = json.load(json_file)

                # build interest clusters
                interest_clusters = []

                for i, words in topics.items():
                    i = int(i)
                    if i == -1:
                        continue;
                    words = [word[0] for word in words]
                    program_ranking_dict = build_ranking_dict()
                    interest_clusters.append(InterestCluster(i, words, program_ranking_dict))
                
                # rank programs for each cluster
                word_course_dict = build_word_course_dict()
                program_course_dict = build_course_program_dict()
                for cluster in interest_clusters:
                    for word in cluster.words:
                        courses = word_course_dict[word]
                        for course in courses:
                            if course in program_course_dict:
                                programs = program_course_dict[course]
                                for program in programs:
                                    cluster.program_ranking[program]['count'] += 1
                
                for cluster in interest_clusters:
                    cluster.calculate_relative_counts()

                # top_program_options = range(3, 8)

                for num_combos in COMBINATION_OPTIONS:
                    reachable_programs_dict = calc_reachable_programs(num_combos)

                    for num_top_programs, program_reachability in reachable_programs_dict.items():
                        programs_ct = program_reachability['num_programs_reached']
                        programs_percent = program_reachability['percent_programs_reached']
                        rows.append([RANDOM_STATE, num_topics, num_combos, num_top_word, num_top_programs, programs_ct, programs_percent])
                #     counts.append(calc_reachable_programs(i, num_combos))

    #         plt.scatter(TOP_WORDS, percents_per_num_words, c=COLORS_COMBINATION[num_combos])
    # plt.show()
    programs_reached_df = pd.DataFrame(rows, columns=["UMAP Random State", "Num Topics", "Num Combinations", "Num Top Words", "Num Top Programs", "Reachable Programs", "Reachable Programs %"])
    programs_reached_df.to_csv("programs_reached-1.csv", index=False)
    