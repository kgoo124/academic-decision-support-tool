import pandas as pd

INTEREST_CLUSTERS = "Check all Interest Clusters Selected (up to 8)"
RECOMMENDATION_COLUMNS = ['1st Rec', '2nd Rec', '3rd Rec', '4th Rec', '5th Rec', '6th Rec', '7th Rec']

program_ranking_cts = pd.read_csv("program_rankings_ct.csv", index_col=0)
program_ranking_relative_cts = pd.read_csv(
        "program_rankings_relative_ct.csv", index_col=0)

def generate_recommendations(clusters):
    programs_sorted_by = "relative_count"
    num_programs = 7  #int(answers["num_programs"]) if answers["num_programs"] else program_ranking_cts.shape[0]

    # aggregate counts or relative count
    if (programs_sorted_by == "relative_count"):
        aggregated_rankings = program_ranking_relative_cts[clusters].mean(axis=1)
    else:
        aggregated_rankings = program_ranking_cts[clusters].sum(axis=1)
    
    return aggregated_rankings.sort_values(ascending=False)[:num_programs].index.tolist()

if __name__ == "__main__":
    user_survey_df = pd.read_table("user-survey/user_survey.tsv")

    for i in range(7):
        user_survey_df[RECOMMENDATION_COLUMNS[i]] = ''

    for ind in user_survey_df.index:
        clusters = user_survey_df[INTEREST_CLUSTERS][ind].split(", ")
        program_recs = generate_recommendations(clusters)

        for i in range(7):
            user_survey_df[RECOMMENDATION_COLUMNS[i]][ind] = program_recs[i]
    
    user_survey_df.to_csv('user-survey/user_survey_processed.tsv', sep='\t')