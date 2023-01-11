from site import PREFIXES
import xarray as xr
import pandas as pd
import numpy as np

PREFIXES = ["AERO", "AGB", "AEPS", "AGC", "AGED", "AG", "ASCI", "ANT", "ARCE", "ARCH", "ART", "ASTR", "BIO", "BMED", "BRAE", "BOT", "BUS", "CHEM", "CD", "CHIN", "CRP", "CE", "CLA", "COMS", "CPE", "CSC", "CM", "DSCI", "DANC", "DATA", "ESE", "ESM", "ERSC", "ECON", "EDUC", "EE", "ENGR", "ENGL", "EDES", "ENVE", "ESCI", "ES", "FPE", "FSN", "FR", "GEOG", "GEOL", "GER",
            "GS", "GSA", "GSB", "GSE", "GSP", "GRC", "HLTH", "HIST", "HNRC", "HNRS", "IME", "ITP", "ISLA", "ITAL", "JPNS", "JOUR", "KINE", "LA", "LAES", "LS", "MSCI", "MATE", "MATH", "ME", "MCRO", "MSL", "MU", "NR", "PHIL", "PEM", "PEW", "PSC", "PHYS", "POLS", "PSY", "RPTA", "RELS", "SCM", "SOC", "SS", "SPAN", "SPED", "STAT", "SIE", "TH", "UNIV", "WVIT", "WGS", "WLC"]


def extract_major_prefixes(course_prefix: str):
    return course_prefix.split(' ')[0].split('/')


def build_shared_course_matrix():
    df = pd.read_csv('program_courses.csv')
    num_programs = len(df['Major'].unique())
    data = xr.DataArray(np.zeros((num_programs, len(PREFIXES))),
                        dims=("program", "prefix"),
                        coords={"program": df['Major'].unique(),
                        "prefix": PREFIXES})
    # print(data)

    for index, row in df.iterrows():
        major = row['Major']
        prefixes = extract_major_prefixes(row['Course Prefix'])
        for prefix in prefixes:
            data.loc[major, prefix] += 1

    df = data.to_pandas()
    df.to_csv('shared_course.csv')
    print(df)


if __name__ == "__main__":
    build_shared_course_matrix()
    print("done")
