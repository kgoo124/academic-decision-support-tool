from collections import OrderedDict
import copy
from typing import List, TypedDict

from helper import get_num_courses_per_program


class InterestCluster:
    def __init__(self, id_num, words, ranking_dict):
        self.id: int = id_num
        self.words: List[str] = words
        self.program_ranking: OrderedDict[str, ProgramCounts] = copy.deepcopy(
            ranking_dict)

    def __repr__(self):
        return f'{self.id}\t{self.words}'

    def get_tuple(self):
        return (", ".join(self.words), self.id)

    def get_top_programs(self, n=5, order=True):
        """Get top n programs. 

        Returns a dictionary or an `OrderedDict` if `order` is true.
        """
        top = sorted(self.program_ranking.items(),
                     key=lambda x: x[1]['relative_count'], reverse=True)[:n]
        if order:
            return OrderedDict(top)
        return dict(top)

    def calculate_relative_counts(self):
        courses_per_program = get_num_courses_per_program()
        for program in self.program_ranking.keys():
            total_courses = courses_per_program[program]
            current_program = self.program_ranking[program]
            current_program['relative_count'] = current_program['count'] / total_courses
            # print(program, current_program['count'], total_courses,
            #       current_program['relative_count'])


class ProgramCounts(TypedDict):
    count: int
    relative_count: float
