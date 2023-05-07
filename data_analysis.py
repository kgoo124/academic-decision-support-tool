import pandas as pd

df = pd.read_csv('courses.csv')
print("Average words in course description", df['Description'].apply(lambda text: len(text.split(" "))).mean())

df = pd.read_csv('program_courses.csv')


num_courses_per_program_gb = df.groupby("Major")["Course Name"]
num_programs_per_course_gb = df.groupby("Course Name")["Major"]


print("\nMin # of courses per program:")
print(num_courses_per_program_gb.size().sort_values().head(5))
print("\nAverage # of courses per program: ", num_courses_per_program_gb.count().mean())
print("\nMax # of courses per program:")
print(num_courses_per_program_gb.size().sort_values(ascending=False).head(5))

print("\nMin # of programs per course:")
print(num_programs_per_course_gb.size().sort_values().head(5))
print("Average # of programs per course: ", num_programs_per_course_gb.count().mean())
print("\nMax # of programs per course:")
print(num_programs_per_course_gb.size().sort_values(ascending=False).head(5))