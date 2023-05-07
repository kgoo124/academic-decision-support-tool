import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from textwrap import wrap
import seaborn
seaborn.set()

CAL_POLY_STUDENT = "Are you a Cal Poly student?"
MAJOR = "Major"
PROGRAM_RECOMMENDED = "My current program was recommended"
MATCHED_INTERESTS = 'One or more of the recommended programs matched my interests'
UNEXPECTED_PROGRAM = "There is an unexpected program that I did not consider yet"
CONSIDERED_PROGRAM_NOT_REC = "A program that I would consider (besides the one I'm enrolled in) is not recommended"
USEFUL = "Do you agree or disagree with following statements below [I think this tool can be useful to select a major]"
CONSIDER_USING = "Do you agree or disagree with following statements below [I would consider using this tool in addition to existing resources]"
MEANINGFUL_CLOUDS = "Do you agree or disagree with following statements below [I think the interest word clouds were mostly meaningful]"
EASY_TO_SELECT_CLOUDS = "Do you agree or disagree with following statements below [It was easy for me to select interesting word clouds]"
OVERALL_USE = "Do you agree or disagree with following statements below [Overall, it was easy to use this tool]"

BINARY_Q = [PROGRAM_RECOMMENDED, MATCHED_INTERESTS, UNEXPECTED_PROGRAM, CONSIDERED_PROGRAM_NOT_REC]
LIKERT_Q = [USEFUL, CONSIDER_USING, MEANINGFUL_CLOUDS, EASY_TO_SELECT_CLOUDS, OVERALL_USE]

def build_graphs(df):
    # plot pie charts for binary questions
    fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(12, 5))
    fig.suptitle("Binary Questions", fontsize='x-large')
    plt.tight_layout()
    plt.subplots_adjust(left=0.05, right=0.95)

    axes[0].set_title(PROGRAM_RECOMMENDED, fontsize='x-small',
                      wrap=True)
    axes[0].pie(df[PROGRAM_RECOMMENDED].value_counts(), autopct='%1.1f%%')

    axes[1].set_title("\n".join(wrap(MATCHED_INTERESTS, 40)),
                      fontsize='x-small', wrap=True)
    axes[1].pie(df[MATCHED_INTERESTS].value_counts(), autopct='%1.1f%%')

    axes[2].set_title("\n".join(wrap(UNEXPECTED_PROGRAM, 30)),
                      fontsize='x-small', wrap=True)
    axes[2].pie(df[UNEXPECTED_PROGRAM].value_counts(), autopct='%1.1f%%')

    axes[3].set_title("\n".join(wrap(CONSIDERED_PROGRAM_NOT_REC, 55)),
                      fontsize='x-small')
    axes[3].pie(df[CONSIDERED_PROGRAM_NOT_REC].value_counts(),
                autopct='%1.1f%%')

    plt.savefig("user_survey_binary.png")

    # plot likert scale
    df[USEFUL].value_counts()
    likert_df = pd.merge(df[USEFUL].value_counts(),
                         df[CONSIDER_USING].value_counts(), left_index=True, right_index=True)
    likert_df.plot(kind="barh")
    plt.show()

    fig, axes = plt.subplots(constrained_layout=True)
    width = 0.2  # the width of the bars
    multiplier = 0

    questions = ("Useful", "Consider", "Gentoo")
    responses = {
        'Strongly Agree': (12, 2, 5),
        'Agree': (38.79, 48.83, 47.50),
        'Neutral': (189.95, 195.82, 217.19),
        'Disagree': (189.95, 195.82, 217.19),
        'Strongly Disagree': (189.95, 195.82, 217.19),
    }

    y = np.arange(len(questions))
    for attribute, measurement in responses.items():
        offset = width * multiplier
        rects = axes.barh(y + offset, measurement, width, label=attribute)
        axes.bar_label(rects, padding=5)
        multiplier += 1

    axes.set_xlabel('Number of Responses')
    axes.set_title('Likert scale')
    axes.set_yticks(y + width, questions)
    axes.legend(loc='upper left', ncols=3)
    axes.set_xlim(0, 250)

    # useful = df[USEFUL].value_counts()
    # y_pos = np.arange(len(useful))
    # axes.barh(y_pos, useful.values)
    # axes.set_yticks(y_pos, labels=useful.index)

    # consider = df[CONSIDER_USING].value_counts()
    # y_pos = np.arange(len(consider))
    # axes.barh(y_pos + width, consider.values)
    # axes.set_yticks(y_pos + width, labels=consider.index)
    # axes.legend()
    plt.show()

    # print(df)


if __name__ == "__main__":
    user_survey_df = pd.read_table("user_survey.tsv")
    total_surveyed = len(user_survey_df)

    calpoly_student_df = user_survey_df[user_survey_df[CAL_POLY_STUDENT] == "Yes"]

    num_calpoly_students = len(calpoly_student_df)
    unique_majors = len(calpoly_student_df[MAJOR].unique())

    print(f"{total_surveyed} total surveyed")
    print(f"{num_calpoly_students} Cal Poly students surveyed")
    print(f"Unique Majors: {unique_majors}")

    print()
    for binary_q in BINARY_Q:
        print(f'{binary_q}: {len(calpoly_student_df[calpoly_student_df[binary_q] == "Yes"])} said Yes')

    print()
    for likert_q in LIKERT_Q:
        print(likert_q, calpoly_student_df[likert_q].value_counts())
        # print(f'{likert_q}: {len(calpoly_student_df[(calpoly_student_df[likert_q] == "Strongly Agree") | (calpoly_student_df[likert_q] == "Agree")])} agreed')

    
