from collections import OrderedDict
from copy import deepcopy
from pprint import pprint
import inquirer
import pandas as pd

JSON_PATH = "topic-models/rs-23/30topics-20words.json"
PROGRAM = "Program"


def get_programs():
    df = pd.read_csv('program_courses.csv')
    return df[PROGRAM].unique().tolist()

def aggregate_rankings_sum(ranking_df, topic_nums):
    return ranking_df[topic_nums].sum(axis=1)


def aggregate_rankings_mean(ranking_df, topic_nums):
    return ranking_df[topic_nums].sum(axis=1)


if __name__ == "__main__":
    program_ranking_cts = pd.read_csv("program_rankings_ct.csv", index_col=0)
    program_ranking_relative_cts = pd.read_csv(
        "program_rankings_relative_ct.csv", index_col=0)

    # prompt user for to select clusters
    questions = [inquirer.Text('interest_clusters',
                               message="Enter the cluster nums separated by one space"
                               ),
                #  inquirer.List('programs_sorted_by',
                #                message="How would you like to sort the results?",
                #                choices=[('Counts', 'count'), ('Relative Counts', 'relative_count')]),
                #  inquirer.Text('num_programs',
                #                message="How many programs would you like to be recommended? (hit enter to show all)"
                #                )
                ]
    answers = inquirer.prompt(questions)

    cluster_indexes = answers['interest_clusters'].split()
    programs_sorted_by = "count" # answers["programs_sorted_by"]
    num_programs = 7  #int(answers["num_programs"]) if answers["num_programs"] else program_ranking_cts.shape[0]

    # aggregate counts or relative count
    if (programs_sorted_by == "relative_count"):
        aggregated_rankings = program_ranking_relative_cts[cluster_indexes].mean(
            axis=1)
    else:
        aggregated_rankings = program_ranking_cts[cluster_indexes].sum(axis=1)

    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.precision', 3,
                           ):
        print("\nHere are the programs that best match the topic word clouds that you picked:")
        top_programs = aggregated_rankings.sort_values(ascending=False)[:num_programs].index.tolist()
        # print(aggregated_rankings.sort_values(ascending=False)[:num_programs]) # print all programs
        for index, program in enumerate(top_programs):
            print(f'{index+1}. {program}')
