import os
from gensim.models import ldamodel
from gensim.test.utils import datapath
from gensim.corpora import Dictionary
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib



def remove_custom_stop_words(input, stop_words):
    x = []
    for text in input:
        for stop in stop_words:
            while stop in text:
                text.remove(stop)
            x.append(text)
    return x

def show_topics_chart(documents, num_topics, num_words, path="img/01_topics.png", show=False):

    dictionary = Dictionary(documents)
    corpus = [dictionary.doc2bow(text) for text in documents]

    # Train model
    lda = ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=num_topics, alpha='auto', eval_every=5)  # learn asymmetric alpha from data

    data = [[], [], []]
    for i in range(0, lda.num_topics):
        t = lda.show_topic(i, topn=num_words)
        for j in t:
            data[0].append(i+1)
            data[1].append(j[0])
            data[2].append(j[1])

    rows = zip(data[0], data[1], data[2])
    headers = ['Topic', 'Word', 'Value']
    dx = pd.DataFrame(rows, columns=headers)

    matplotlib.style.use('ggplot')
    pivot_dx = dx.pivot(index='Topic', columns='Word', values='Value')
    ax = pivot_dx.plot.barh(stacked=True, cmap=plt.get_cmap('tab20'), figsize=(14,8))

    # add labels to bars and remove legend
    def annotateBars(row, ax=ax):
        curr_value = 0
        for col in row.index:
            value = row[col]
            if (str(value) != 'nan'):
                ax.text(curr_value + (value)/2, int(row.name)-1, col, ha='center',va='center')
                curr_value += value
    pivot_dx.apply(annotateBars, ax=ax, axis=1)
    ax.get_legend().remove()

    plt.savefig(path)
    if show: plt.show()

    plt.cla()
    print(path, 'finished')


if __name__ == '__main__':

    plt.rcParams["figure.figsize"] = (14, 8)

    from data_loader import DataLoader
    loader = DataLoader(force=False)
    df = loader.get_dataframe()
    x = df['article']

    num_topics = 10
    num_words = 5


    show_topics_chart(x, num_topics, num_words, path="img/01_topics.png")

    x = remove_custom_stop_words(x, ['wurd', 'mitg', 'seit', 'dass', 'ab', 'sei', 'un', 'de', 'die', 'jahr', 'isbn'])
    show_topics_chart(x, num_topics, num_words, path="img/02_topics.png")

    x = remove_custom_stop_words(x, ['abgeordnet', 'deutsch', 'bundest', 'gewahlt', 'bundestagswahl', 'stellvertretend', 'vorsitzend'])
    show_topics_chart(x, num_topics, num_words, path="img/03_topics.png")
