from build_graphs import label_nodes
import networkx as nx
from generate_clusters_old import build_interest_clusters

INTEREST_COURSE_GRAPH: str = "interest_program.graphml"
COUNT_THRESHOLD: int = 15


def build_interest_programs_graph():
    G: nx.DiGraph = nx.DiGraph()
    interest_clusters = build_interest_clusters()
    # print(interest_clusters)

    for cluster in interest_clusters:
        G.add_node(cluster.id, words=",".join(
            cluster.words), label=",".join(cluster.words))
        ranking = cluster.program_ranking.items()
        for (program, count) in ranking:
            if count < COUNT_THRESHOLD:
                continue
            print(program, count)
            G.add_node(program, label=program)
            G.add_edge(cluster.id, program)

    nx.write_graphml(G, INTEREST_COURSE_GRAPH)


if __name__ == "__main__":
    build_interest_programs_graph()
    print("done")
