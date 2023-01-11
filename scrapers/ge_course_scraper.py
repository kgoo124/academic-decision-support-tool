import requests
from bs4 import BeautifulSoup

GE_COURSES_URL = "https://catalog.calpoly.edu/generalrequirementsbachelorsdegree/"

ge_course_dict = {}

if __name__ == "__main__":
    GE_HEADER_ID = "General-Education-Courses"

    program_page = requests.get(f'{GE_COURSES_URL}')
    soup = BeautifulSoup(program_page.content,
                         "html.parser")
    ge = soup.find('a', {'id': GE_HEADER_ID}).parent

    # print(ge.prettify())

    for table in ge.find_next_siblings("table"):
        for tr in table.tbody.find_all("tr"):
            if('last' in tr['class'] and "class" in tr.td.attrs and "column0" in tr.td['class']):
                ge_course_dict[tr.td] = {"courses": set()}
                print(tr.td.text)
            # print(tr, "\n")
        # quit()
    print(ge_course_dict)
