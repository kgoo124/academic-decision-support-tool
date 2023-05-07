from collections import OrderedDict
from itertools import combinations
import json
import math
from pprint import pprint
import re

import pandas as pd
from InterestCluster import InterestCluster
from build_data_dict import build_course_program_dict, build_word_course_dict

from generate_clusters_old import build_ranking_dict
from program_decision_support import aggregate_rankings_sum

import matplotlib.pyplot as plt
import seaborn as sns

plt.rc('axes', labelsize=20)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rcParams['legend.title_fontsize'] = 18
plt.rcParams["font.family"] = "Times New Roman"

# COMBINATION_OPTIONS = [5]
COMBINATION_OPTIONS = [1,2,3,4,5,6]
# TOPICS = [30]
TOPICS = [10,20,25,30]
TOP_WORDS = [5,10,15,20]
# TOP_WORDS = [020]
NUM_TOP_PROGRAMS_OPTIONS = [3,5,7] # 3,5,7
# NUM_TOP_PROGRAMS_OPTIONS = [7] # 3,5,7
SEEDS = ["rs-23", "rs-52"]
# SEEDS = ["rs-5"]
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
            aggregated_ranking_dict = aggregate_rankings_sum(aggregated_ranking_dict, interest_clusters[int(topic)].program_ranking)
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


def calc_reachable_programs_mem(program_ranking_relative_cts):
    program_ranking_dict = build_ranking_dict()
    
    # create dictionary where key is the number of top programs
    # values: reachable_programs_set, num_programs_reached, percent_programs_reached
    reachable_programs_dict = {}
    for num_top_programs in NUM_TOP_PROGRAMS_OPTIONS:
        for num_combos in COMBINATION_OPTIONS:
            key = f"{num_combos}combos_{num_top_programs}top-programs"
            reachable_programs_dict.update({key: {"programs_reachable": set(
            ), "num_programs_reached": 0, "percent_programs_reached": 0}})

    total_programs = len(program_ranking_dict.keys())

    col_names = list(program_ranking_relative_cts.columns)

    # get list of all possible combinations
    topic_combinations = [] # nested array of combinations [all single combinations, all pairs, ...]
    for num_combos in COMBINATION_OPTIONS:
        topic_combinations.append(list(combinations(col_names, num_combos)))
    # for num in range(num_combinations): # (0), (1), ..., (0,1), (0,2), ..., (0,1,2), ...
    #     topic_combinations.extend(list(combinations(col_names, num + 1)))
    
    
    counter = 0
    for num_combos, combination_sublist in enumerate(topic_combinations):
        for combination in combination_sublist:
            aggregated_df = program_ranking_relative_cts[list(combination)].mean(axis=1).sort_values(ascending=False)
            
            for num_top_programs in NUM_TOP_PROGRAMS_OPTIONS:
                key = f"{num_combos + 1}combos_{num_top_programs}top-programs"
                top_programs = list(aggregated_df.head(num_top_programs).index)
                reachable_programs_dict[key]["programs_reachable"].update(top_programs)

            # if counter % 100000 == 0:
            #     print(combination, len(
            #         reachable_programs_dict[num_top_programs]["programs_reachable"]))
            # counter += 1

            # if (len(reachable_programs_dict[num_top_programs]["programs_reachable"]) >= total_programs):
            #     # print(combination)
            #     break

    # once all topic combos are finished, calculate program reachability metrics
    for key in reachable_programs_dict.keys():
        reachable_programs = reachable_programs_dict[key]['programs_reachable']
        reachable_programs_dict[key]['num_programs_reached'] = len(
            reachable_programs)
        reachable_programs_dict[key]['percent_programs_reached'] = len(
            reachable_programs) * 100 / total_programs
    
    # pprint(reachable_programs_dict)
    return reachable_programs_dict

def visualize_programs_reached(filename):
    programs_reached_df = pd.read_csv(filename)

    # drop UMAP random state column
    programs_reached_df = programs_reached_df.drop("UMAP Random State", axis=1)

    aggregated_programs_reached = programs_reached_df.groupby(["Num Top Programs", "Num Topics", "Num Combinations", "Num Top Words"]).mean()
    aggregated_programs_reached = aggregated_programs_reached.reset_index()
    # print(aggregated_programs_reached)

    g = sns.FacetGrid(aggregated_programs_reached, row="Num Topics", col="Num Combinations", hue="Num Top Words", margin_titles=True)
    g.map(plt.plot, "Num Top Programs", "Reachable Programs %", marker='o')
    g.set_titles(row_template = '{row_name} topics', col_template='{col_name} combinations')
    fig = g.fig
    fig.set_dpi(400)
    g.add_legend(title="Num Top Words", loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=4, fontsize=20)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.075, left=0.065, wspace=0.2)
    fig.supxlabel('Num Top Programs', fontsize=22)
    fig.supylabel('Reachable Programs %', fontsize=22)
    # fig.suptitle('Reachable Program % Based on Num Topics, Num Combinations, Num Top Programs and Num Top Words', fontsize='xx-large')
    new_list = range(math.floor(min(aggregated_programs_reached["Num Top Programs"])), math.ceil(max(aggregated_programs_reached["Num Top Programs"]))+1,2)
    # g.set_axis_labels("Num Top Programs", "Reachable Programs %")
    # g.set_xlabels(new_list)

    # # Iterate thorugh each axis
    for ax in g.axes.flat:
        ax.set(xlabel=None, ylabel=None)
        ax.set_xticks([3, 5, 7])
    #     # Make x and y-axis labels slightly larger
    #     ax.set_xlabel(ax.get_xlabel(), fontsize='x-large')
    #     ax.set_ylabel(ax.get_ylabel(), fontsize='x-large')
    #     ax.set_title(ax.get_title(), fontsize='xx-large')

    #     # Make title more human-readable and larger
    #     # if ax.get_title():
    #     #     ax.set_title(ax.get_title().split('=')[1],
    #     #                 fontsize='xx-large')
        
    #     # Make right ylabel more human-readable and larger
    #     # Only the 2nd and 4th axes have something in ax.texts
    #     if ax.texts:
    #         # This contains the right ylabel text
    #         txt = ax.texts[0]
    #         ax.text(txt.get_unitless_position()[0], txt.get_unitless_position()[1],
    #                 txt.get_text(),
    #                 transform=ax.transAxes,
    #                 va='center',
    #                 fontsize='xx-large',
    #                 rotation=-90)
    #         # Remove the original text
    #         ax.texts[0].remove()
    plt.savefig("program_reachability.png", bbox_inches='tight', pad_inches = 0.25)
    quit()


if __name__ == "__main__":
    # calc_reachable_programs_mem(4)
    visualize_programs_reached("programs_reached_new.csv")
    quit()
    rows = []
    for seed in SEEDS:
        for num_topics in TOPICS:
            print(num_topics)
            for num_top_word in TOP_WORDS:
                percents_per_num_words = []
                program_ranking_relative_cts = pd.read_csv(
                    f"topic-models/{seed}/{num_topics}topics-{num_top_word}words_program_rankings_relative_ct.csv", index_col=0)

                    # top_program_options = range(3, 8)

                reachable_programs_dict = calc_reachable_programs_mem(program_ranking_relative_cts)

                for key, program_reachability in reachable_programs_dict.items():
                    regex = r"(\d)combos_(\d)top-programs"
                    match = re.match(regex, key)
                    num_combos, num_top_programs = match.groups();
                    programs_ct = program_reachability['num_programs_reached']
                    programs_percent = program_reachability['percent_programs_reached']
                    rows.append([seed, num_topics, num_combos, num_top_word, num_top_programs, programs_ct, programs_percent])

    programs_reached_df = pd.DataFrame(rows, columns=["UMAP Random State", "Num Topics", "Num Combinations", "Num Top Words", "Num Top Programs", "Reachable Programs", "Reachable Programs %"])
    programs_reached_df.to_csv("programs_reached-1.csv", index=False)
    exit()
    