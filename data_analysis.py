import pandas as pd

df = pd.read_csv('program_courses.csv')
counts = df.Major.value_counts()
counts.to_csv('major_counts.csv')
