from collections import OrderedDict
from copy import deepcopy
from pprint import pprint
from generate_clusters_old import build_interest_clusters
import inquirer


def aggregate_rankings(dict1, dict2):
    dict3 = deepcopy({**dict1, **dict2})
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
            dict3[key]['count'] = value['count'] + dict1[key]['count']
            dict3[key]['relative_count'] = value['relative_count'] + \
                dict1[key]['relative_count']
    return dict3


if __name__ == "__main__":
    create_word_clouds = inquirer.prompt([inquirer.Confirm('word_clouds',
                                                           message="Would you like to see the clusters visualized as word clouds?", default=False), ])['word_clouds']
    print("Getting interest clusters, hold tight...")
    interest_clusters = build_interest_clusters(
        create_word_clouds=create_word_clouds)
    clusters = [cluster.get_tuple() for cluster in interest_clusters]

    # prompt user for to select clusters
    questions = [inquirer.Checkbox('interest_clusters',
                                   message="Choose the clusters that interest you the most",
                                   choices=clusters),
                 inquirer.List('programs_sorted_by',
                               message="How would you like to sort the results?",
                               choices=[('Counts', 'count'), ('Relative Counts', 'relative_count')])]
    answers = inquirer.prompt(questions)

    cluster_indexes = answers['interest_clusters']
    programs_sorted_by = answers["programs_sorted_by"]

    # aggregate clusters
    aggregated_cluster_dict = OrderedDict()
    for i in cluster_indexes:
        aggregated_cluster_dict = aggregate_rankings(aggregated_cluster_dict,
                                                     interest_clusters[i].program_ranking)

    NUM_PROGRAMS = 20
    # print(aggregated_cluster_dict)
    # find the top programs for the aggregated cluster
    top_programs = sorted(aggregated_cluster_dict.items(),
                          key=lambda x: x[1][programs_sorted_by], reverse=True)[:]
    for key, value in top_programs:
        print(f"{key};{value['relative_count']}")
    # pprint(OrderedDict(top_programs))
