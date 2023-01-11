import re
import pandas as pd

PROGRAM = "Program"


def clean_text(text):
    text_input = re.sub('[^a-zA-Z1-9]+', ' ', str(text))
    output = re.sub(r'\d+', '', text_input)
    return output.lower().strip()


def get_num_courses_per_program():
    df = pd.read_csv('program_courses.csv')
    return df.groupby([PROGRAM])[PROGRAM].count()
