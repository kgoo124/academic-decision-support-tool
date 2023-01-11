from math import sqrt
import pandas as pd
import networkx as nx

DEPT_COURSE_FILE_NAME: str = "courses.csv"
COL_DEPT_COURSE_GRAPH: str = "dept_course.graphml"

MAJOR_COURSE_FILE_NAME: str = "major_courses.csv"
MAJOR_COURSE_GRAPH: str = "major_course.graphml"

PROG_COURSE_FILE_NAME: str = "program_courses.csv"
PROG_COURSE_GRAPH: str = "program_course.graphml"


def label_nodes(G):
    for node in G.nodes():
        G.nodes[node]['label'] = f'{node}'


def label_dept_course_nodes(G):
    types = nx.get_node_attributes(G, 'type')
    for node in G.nodes():
        label = node
        if (len(node.split('-')) == 2):
            (first, second) = node.split('-')
            label = f'<html><p style="font-weight:bold;text-align:center">{first}<br/>{second}</p></html>' if (
                types[node] == "major") else f'<html><p style="text-align:center">{first}<br/>{second}</p></html>'
        elif (len(node.split(',')) == 2):
            (first, second) = node.split(',')
            label = f'<html><p style="font-weight:bold;text-align:center">{first}<br/>{second}</p></html>' if (
                types[node] == "major") else f'<html><p style="text-align:center">{first}<br/>{second}</p></html>'
        elif (len(node.split(' ')) > 1):
            split_labels = node.split(' ')
            num_rows = round(sqrt(len(split_labels)))

            output = [split_labels[i:i + num_rows]
                      for i in range(0, len(split_labels), num_rows)]

            rows = [" ".join(row) for row in output]
            label = f'<html><p style="font-weight:bold;text-align:center">{"<br/>".join(rows)}</p></html>'
            # if (types[node] == "major") else f'<html><p style="text-align:center">{"<br/>".join(rows)}</p></html>'
        else:
            label = f'<html><p style="font-weight:bold;text-align:center">{label}</p></html>'
            # if (types[node] == "major") else f'<html><p style="text-align:center">{label}</p></html>'

        G.nodes[node]['label'] = label


def create_college_depart_course_graph():
    course_list: pd.DataFrame = pd.read_csv(DEPT_COURSE_FILE_NAME)

    G = nx.DiGraph()

    college_attributes = {
        "font_size": int(64)
    }

    dept_attributes = {
        "font_size": int(52)
    }

    course_attributes = {
        "font_size": int(40)
    }

    for index, row in course_list.iterrows():
        college = row['College']
        dept = row['Dept']
        course = row['Course Prefix']
        G.add_nodes_from([(college, college_attributes),
                         (dept, dept_attributes),
                         (course, course_attributes)])
        G.add_edge(college, dept)
        G.add_edge(dept, course)

    label_dept_course_nodes(G)

    nx.write_graphml(G, COL_DEPT_COURSE_GRAPH)


def create_program_course_graph():
    course_list: pd.DataFrame = pd.read_csv(PROG_COURSE_FILE_NAME)

    G: nx.DiGraph = nx.DiGraph()

    for index, row in course_list.iterrows():
        major = row['Major']
        course = row['Course Prefix']
        color = row['Color']

        major_attributes = {
            "type": "major",
            "outline_col": color,
            "size": int(400),
            "border_width": int(25),
            "text_col": "#000000",
            "fill_col": "#ffffff"
        }

        course_attributes = {
            "type": "course",
            "size": int(118),
            "text_col": "#ffffff",
            "fill_col": "#000000"
        }

        G.add_nodes_from([(major, major_attributes),
                         (course, course_attributes)])
        G.add_edge(major, course)

    label_dept_course_nodes(G)
    nx.write_graphml(G, PROG_COURSE_GRAPH)


if __name__ == "__main__":
    # create_college_depart_course_graph()
    create_program_course_graph()
    print("done")
