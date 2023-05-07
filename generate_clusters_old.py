from typing import Dict
from InterestCluster import InterestCluster
import csv
from build_corpus import process_corpus
from sklearn.cluster import KMeans

# Data Structures
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer


# K-Means
from sklearn import cluster

# Visualization and Analysis
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
from sklearn.metrics import silhouette_samples, silhouette_score
from wordcloud import WordCloud

from pprint import pprint


from scrapers import course_scraper
from build_data_dict import build_course_program_dict, build_word_course_dict

DESCRIPTION = "Description"
PROGRAM = "Program"

FREQ_DIST_FILE = "word_freq.csv"

plt.rcParams["font.family"] = "Times New Roman"

vectorizer = TfidfVectorizer(sublinear_tf=True, min_df=5, max_df=0.95)


def write_fdist(fdist):
    file = csv.writer(open(FREQ_DIST_FILE, 'w'))
    for key, count in fdist.most_common(fdist.N()):
        file.writerow([key, count])


def build_ranking_dict():
    df = pd.read_csv('program_courses.csv')
    programs = df[PROGRAM].unique().tolist()
    program_counts = {'count': 0, 'relative_count': 0}
    # use dictionary comprehension to avoid mutating the same dictionary for program counts
    return {key: dict(program_counts) for key in list(set(programs))}


def build_interest_clusters(calc_silhouette=False, create_word_clouds=False):
    df = pd.read_csv(course_scraper.FILE_NAME)
    corpus = df[DESCRIPTION].tolist()
    corpus = process_corpus(corpus)
    # print(corpus[200:400])
    X = vectorizer.fit_transform(corpus)

    tf_idf = pd.DataFrame(
        data=X.toarray(), columns=vectorizer.get_feature_names_out())
    final_df = tf_idf

    best_result = 5
    kmeans_results: Dict[int, KMeans]

    if calc_silhouette:
        k = 30
        # run k means for a bunch of different numbers
        kmeans_results = run_multiple_k_means(k, final_df)
        silhouette(kmeans_results, final_df)
    else:
        kmeans_results = run_k_means(best_result, final_df)

    kmeans = kmeans_results.get(best_result)
    kmeans.fit(final_df)

    clusters = kmeans.labels_

    # generate word clouds
    if create_word_clouds:
        centroids = pd.DataFrame(kmeans.cluster_centers_)
        centroids.columns = final_df.columns
        generate_word_clouds(centroids)

    # get top words for each cluster
    final_df_array = final_df.to_numpy()
    prediction = kmeans.predict(final_df)
    n_feats = 8

    # build interest clusters
    interest_clusters = []
    program_ranking_dict = build_ranking_dict()

    dfs = get_top_features_cluster(final_df_array, prediction, n_feats)
    for i in range(0, len(dfs)):
        # print(dfs[i][:n_feats])
        words = dfs[i][:n_feats]['features'].values.tolist()
        # print(dfs[i][:n_feats]['features'].values.tolist())
        interest_clusters.append(InterestCluster(
            i, words, program_ranking_dict))

     # rank programs for each cluster
    word_course_dict = build_word_course_dict()
    program_course_dict = build_course_program_dict()
    # print(word_course_dict['computer'])
    # print(program_course_dict)
    for cluster in interest_clusters:
        for word in cluster.words:
            courses = word_course_dict[word]
            for course in courses:
                if course in program_course_dict:
                    programs = program_course_dict[course]
                    # print(word, course, programs)
                    # print()
                    for program in programs:
                        cluster.program_ranking[program]['count'] += 1

    for cluster in interest_clusters:
        cluster.calculate_relative_counts()

    return interest_clusters


def run_k_means(k, data):
    kmeans_results = dict()
    kmeans = cluster.KMeans(n_clusters=k, init='k-means++', n_init=10,
                            tol=0.0001, random_state=0)
    kmeans_results.update({k: kmeans.fit(data)})
    return kmeans_results


def run_multiple_k_means(max_k, data):
    STEP = 1
    max_k += 1
    kmeans_results = dict()
    for k in range(2, max_k, STEP):
        kmeans = cluster.KMeans(n_clusters=k, init='k-means++', n_init=10,
                                tol=0.0001, random_state=0)

        kmeans_results.update({k: kmeans.fit(data)})

    return kmeans_results

# Transforms a centroids dataframe into a dictionary to be used on a WordCloud.


def centroidsDict(centroids, index):
    a = centroids.T[index].sort_values(ascending=False).reset_index().values
    centroid_dict = dict()

    for i in range(0, len(a)):
        centroid_dict.update({a[i, 0]: a[i, 1]})

    return centroid_dict


def generate_word_clouds(centroids):
    wordcloud = WordCloud(
        width=600, height=300, max_font_size=100, max_words=20, background_color='white', colormap="viridis")
    for i in range(0, len(centroids)):
        centroid_dict = centroidsDict(centroids, i)
        wordcloud.generate_from_frequencies(centroid_dict)

        plt.figure(figsize=(4, 2), dpi=150)
        # plt.title('Cluster {}'.format(i))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig(f'v1_wordclouds/topic{i}.png', bbox_inches='tight', pad_inches = 0)


def silhouette(kmeans_dict, df, plot=True):
    df = df.to_numpy()
    avg_list = []
    for n_clusters, kmeans in kmeans_dict.items():
        kmeans_labels = kmeans.predict(df)
        # Average Score for all Samples
        silhouette_avg = silhouette_score(df, kmeans_labels)
        avg_list.append((n_clusters, silhouette_avg))
        if(plot):
            plotSilhouette(df, n_clusters, kmeans_labels, silhouette_avg)

    silhouette_score_df = pd.DataFrame(avg_list, columns=['Num Clusters','Silhouette Score'])
    silhouette_score_df.set_index('Num Clusters', inplace=True)
    silhouette_score_df.plot()
    plt.plot(5, silhouette_score_df.loc[5], marker='o', color='blue')
    plt.text(6, silhouette_score_df.loc[5].values[0], round(silhouette_score_df.loc[5].values[0],3))
    # print(silhouette_score_df['Silhouette Score'].sort_values(ascending=False))
    
    plt.savefig(f'v1_silhouette_scores/silhouette_score_averages.png', bbox_inches='tight', pad_inches = 0.1)

    # avg_list.plt.plot(n_clusters)


def plotSilhouette(df, n_clusters, kmeans_labels, silhouette_avg):
    fig, ax1 = plt.subplots(1)
    fig.set_size_inches(8, 6)
    fig.set_dpi(150)
    ax1.set_xlim([-0.2, 1])
    ax1.set_ylim([0, len(df) + (n_clusters + 1) * 10])

    # The vertical line for average silhouette score of all the values
    ax1.axvline(x=silhouette_avg, color="red", linestyle="--")
    ax1.set_yticks([])  # Clear the yaxis labels / ticks
    ax1.set_xticks([-0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])
    plt.title(("Silhouette analysis for K = %d" %
              n_clusters), fontsize=10, fontweight='bold')

    y_lower = 10
    # Compute the silhouette scores for each sample
    sample_silhouette_values = silhouette_samples(df, kmeans_labels)
    for i in range(n_clusters):
        ith_cluster_silhouette_values = sample_silhouette_values[kmeans_labels == i]
        ith_cluster_silhouette_values.sort()

        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i

        color = cm.nipy_spectral(float(i) / n_clusters)
        ax1.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values,
                          facecolor=color, edgecolor=color, alpha=0.7)

        if (n_clusters <= 20):
            # Label the silhouette plots with their cluster numbers at the middle
            ax1.text(-0.05, y_lower + 0.35 * size_cluster_i, str(i))

        y_lower = y_upper + 10  # Compute the new y_lower for next plot. 10 for the 0 samples
    plt.savefig(f'v1_silhouette_scores/{n_clusters}clusters.png', bbox_inches='tight', pad_inches = 0.1)


def get_top_features_cluster(tf_idf_array, prediction, n_feats):
    labels = np.unique(prediction)
    dfs = []
    for label in labels:
        id_temp = np.where(prediction == label)  # indices for each cluster
        # returns average score across cluster
        x_means = np.mean(tf_idf_array[id_temp], axis=0)
        # indices with top 20 scores
        sorted_means = np.argsort(x_means)[::-1][:n_feats]
        features = vectorizer.get_feature_names()
        best_features = [(features[i], x_means[i]) for i in sorted_means]
        df = pd.DataFrame(best_features, columns=['features', 'score'])
        dfs.append(df)
    return dfs


def plotWords(dfs, n_feats):
    plt.figure(figsize=(8, 4))
    for i in range(0, len(dfs)):
        plt.title(("Most Common Words in Cluster {}".format(i)),
                  fontsize=10, fontweight='bold')
        sns.barplot(x='score', y='features', orient='h', data=dfs[i][:n_feats])
        plt.show()


if __name__ == "__main__":
    build_interest_clusters(calc_silhouette=True, create_word_clouds=False)
