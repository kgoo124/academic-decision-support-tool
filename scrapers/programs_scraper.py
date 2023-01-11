import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from distinctipy import distinctipy

MAJOR_FILE_NAME: str = "major_courses.csv"
PROG_FILE_NAME: str = "program_courses.csv"


GE_COURSE_FILE: str = "GE_courses.csv"


BASE_CATALOG_URL: str = "https://catalog.calpoly.edu/"
BASE_PROGRAMS_URL: str = "https://catalog.calpoly.edu/programsaz/"
UNDERGRAD_PROG_HTML_ID = "textcontainer"

program_course_dict = {}
colleges = {}
major_concentration_dict = {}
crosslist_courses = {}
ge_courses_df = pd.DataFrame()

colors = [(0, 0, 0), (1, 1, 1)]


def getTextWithinParentheses(text: str):
    return text[text.find('(')+1:text.find(')')]


def clean_text(text):
    # add spaces and replace leading "and" or "&"
    return re.sub('^(and|&)', '', text.replace('\xa0', " ")).strip()


def extract_class_codes_from_html(html):
    return [clean_text(a.text) for a in html.find_all('a')]


def extract_text_from_html(html):
    if (html.span):
        return [clean_text(content.text) for content in html.contents if content.name != 'br']
    return [clean_text(html.text)]


def process_program_text(text):
    BACHELOR_DEGREES_REGEX = ', BA|, BFA|, BS|, BArch|, BLA'
    program = re.split(BACHELOR_DEGREES_REGEX, text)
    return program[0].strip()


def get_all_program_links():
    course_page = requests.get(BASE_PROGRAMS_URL)
    soup = BeautifulSoup(course_page.content, "html.parser")
    soup = soup.find(id=UNDERGRAD_PROG_HTML_ID)
    # print(soup.prettify())
    # find all majors
    return [(process_program_text(a.text), a['href']) for a in soup.find_all(
        'a', href=True) if "collegesandprograms" in a['href']]
    # find all majors, minors, and crossdisciplinary
    return [(process_program_text(a.text), a['href']) for a in soup.find_all(
        'a', href=True) if "collegesandprograms" in a['href'] and not "minor" in a['href'] or "crossdisciplinarystudies" in a['href']]


def extract_major(program_link):
    split_link = program_link.split("/")
    if "concentration" in program_link:
        if "orfaleacollegeofbusiness" in program_link or "interdisciplinarystudiesliberalarts" in program_link:
            return split_link[len(split_link)-2]
        else:
            return split_link[len(split_link)-3]
    elif "general-curriculum" in program_link or "generalcurriculum" in program_link:
        return split_link[len(split_link)-3]
    elif "minor" in program_link:
        return [link for link in split_link if "minor" in link][0]
    else:
        return split_link[len(split_link)-2]


def process_crosslisted_courses(class_code):
    prefixes = class_code.split('/')
    prefixes.sort()

    split_prefixes = re.split('/| ', class_code)
    split_prefixes = [code.strip() for code in split_prefixes]
    split_prefixes.sort()

    contains_single_num = len(
        [code for code in split_prefixes if code.isdigit()]) == 1

    if (not contains_single_num):
        if(len(split_prefixes) % 2 == 1):  # [201, 202, PSY]
            (*nums, dept) = split_prefixes
            crosslisted_code = f"{dept} {'/'.join(nums)}"
            for num in nums:
                key = f'{dept} {num}'
                crosslist_courses[key] = crosslisted_code
        else:  # [ENGR 322, SCM 302]
            crosslisted_code = '/'.join(prefixes)
            for prefix in prefixes:
                crosslist_courses[prefix] = crosslisted_code
    else:  # default format EX.PSY/WGS 324
        (num, *depts) = split_prefixes
        crosslisted_code = f"{'/'.join(depts)} {num}"
        for dept in depts:
            key = f'{dept} {num}'
            crosslist_courses[key] = crosslisted_code
    crosslist_courses[class_code] = crosslisted_code
    crosslist_courses[crosslisted_code] = crosslisted_code


def process_ge_course_table(ge_table):
    ge_areas = []
    ge_courses = set()

    for row in ge_table.find_all('tr'):
        hours = row.find('td', {"class": "hourscol"}).text
        if (hours == '' or hours == "0"):
            continue
        ge_area = row.find('td').text.split(
            '(')[0].strip().split('- ')[0].strip()  # get first col
        ge_areas.append(ge_area)

    for area in ge_areas:
        df = ge_courses_df[ge_courses_df['GE Type'] == area]
        if df.empty:
            continue
        df = df.loc[:, df.columns != 'GE Type']
        records = map(tuple, df.to_records(index=False))
        ge_courses.update(records)

    return ge_courses


def get_courses_for_program(major: str, program_link: str):
    COURSE_TABLE_CLASS = "sc_courselist"

    program_page = requests.get(f'{BASE_CATALOG_URL}{program_link}')
    soup = BeautifulSoup(program_page.content,
                         "html.parser")
    course_tables = soup.find_all('table', {'class': COURSE_TABLE_CLASS})

    # all tables but the last one (GE table)
    program_is_major = (
        "concentration" not in program_link and "minor" not in program_link and "general-curriculum" not in program_link and "generalcurriculum" not in program_link)
    program_course_tables = course_tables[:-
                                          1] if program_is_major else course_tables
    for course_table in program_course_tables:
        # get all rows in course table
        for tr in course_table.find_all('tr'):
            if (len(tr.contents) != 3):
                continue
            class_codes = extract_class_codes_from_html(tr.contents[0])

            processed_class_codes = []
            for class_code in class_codes:
                # add to dictionary
                if('/' in class_code and class_code not in crosslist_courses):
                    process_crosslisted_courses(class_code)
                # lookup code in dictionary
                processed_class_codes.append(
                    crosslist_courses[class_code] if class_code in crosslist_courses else class_code)

            class_name = extract_text_from_html(tr.contents[1])
            courses = set(zip(processed_class_codes, class_name))

            program_course_dict[major]["courses"].update(courses)

    # if(program_is_major):
    #     ge_courses = process_ge_course_table(course_tables[-1])
    #     program_course_dict[major]["courses"].update(ge_courses)


def process_program(program: str, program_link: str):
    major = extract_major(program_link)

    if ("concentration" not in program_link and not ("general-curriculum" in program_link or "generalcurriculum" in program_link)) or "orfaleacollegeofbusiness" in program_link or "interdisciplinarystudiesliberalarts" in program_link:
        major_concentration_dict[major] = program

    major = major in major_concentration_dict and major_concentration_dict[major]

    if major not in program_course_dict:
        program_course_dict[major] = {
            "college": program_link.split("/")[2],
            "major": major,
            "program": program,
            "courses": set()
        }

    get_courses_for_program(major, program_link)


def build_df():
    data = []
    for program_info in program_course_dict.values():
        for course in program_info["courses"]:
            college = program_info['college']
            color = get_color_attribute(college, colors)
            major = program_info['major']
            program = program_info['program']
            data.append([college, major, program, course[0], course[1], color])

    column_names = ["College", "Major", "Program",
                    "Course Prefix", "Course Name", "Color"]
    df = pd.DataFrame(data, columns=column_names)
    return df


def get_color_attribute(college, colors):
    if (college in colleges):
        return colleges[college]
    color = distinctipy.get_colors(1, colors)[0]
    colors.append(color)
    color = rgb_to_hex(color)
    colleges[college] = color
    return color


def rgb_to_hex(rgb):
    r, g, b = [round(val * 255) for val in rgb]
    return '#%02x%02x%02x' % (r, g, b)


if __name__ == "__main__":
    GE_PREFIX_COL = "Prefix"
    ge_courses_df = pd.read_csv(GE_COURSE_FILE)
    ge_courses_df[GE_PREFIX_COL] = ge_courses_df[GE_PREFIX_COL].apply(
        clean_text)
    crosslisted_ge_courses_df = ge_courses_df[ge_courses_df[GE_PREFIX_COL].str.contains(
        '/')]

    for index, row in crosslisted_ge_courses_df.iterrows():
        prefix = clean_text(row[GE_PREFIX_COL])
        process_crosslisted_courses(prefix)

    program_links = get_all_program_links()

    # (program_name, program_link) = program_links[23]
    # courses = get_courses_for_program(program_name, program_link)

    for program in program_links:
        (program_name, program_link) = program
        process_program(program_name, program_link)

    # print(program_course_dict)
    # print(major_concentration_dict)
    programs_courses_df = build_df()
    print(len(pd.unique(df['Course Prefix'])))
    programs_courses_df.to_csv(PROG_FILE_NAME, index=False)
