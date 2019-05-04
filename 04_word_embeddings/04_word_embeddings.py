import os
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from gensim.models import FastText
from matplotlib import pyplot as plt
from scipy.spatial import distance


def plot(X, vocab, colors, labels, show=False):

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    for i, x in enumerate(X):

        print('calculating t-SNE ...')
        from sklearn.manifold import TSNE
        tsne = TSNE(n_components=2)
        X_tsne = tsne.fit_transform(x)


        df2 = pd.DataFrame(X_tsne, index=vocab, columns=['x', 'y'])


        print('generate scatter plot ...')


        ax.scatter(df2['x'], df2['y'], c=colors[i], label=labels[i], alpha=0.5)
        ax.legend()
        ax.grid(True)

        # add labels
        #print('adding labels ...')
        #for word, pos in df2.iterrows():
        #   ax.annotate(word, pos)

    plt.title('Fig 1: vec2word and fasttext models, reduced with t-SNE')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    if show: plt.show()

    plt.savefig("img/fig1_plot.png")

def plot_party_names(X, model, vocab, PARTIES, colors, labels, show=False):

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    for i, x in enumerate(X):

        dimensions = model[i][vocab].shape[1]

        # get vec2word vectors of party names
        parties_list = []
        for p in PARTIES:
            elem = None
            try:
                elem = model[i][p]
            except:
                elem = np.zeros(dimensions)
            parties_list.append(elem)

        print('calculating t-SNE ...')
        from sklearn.manifold import TSNE
        tsne = TSNE(n_components=2)
        X_tsne_parties = tsne.fit_transform(np.array(parties_list))

        df2 = pd.DataFrame(X_tsne_parties, index=PARTIES, columns=['x', 'y'])

        ax.scatter(df2['x'], df2['y'], c=colors[i], label=labels[i], alpha=0.5)

        print('adding labels ...')
        for word, pos in df2.iterrows():
           ax.annotate(word, pos)


    plt.title('Fig 2: vec2word and fasttext models, reduced with t-SNE')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    if show: plt.show()

    plt.savefig("img/fig2_party_names.png")


def plot_distances_between_vectors(X, model, vocab, words, labels, show=False):

    fig = plt.figure()

    for i, x in enumerate(X):

        ax = plt.subplot(1,2,i+1)

        mtx = np.zeros(( len(words), len(words) ))
        dimensions = model[i][vocab].shape[1]

        for idx1, a in enumerate(words):

            for idx2, b in enumerate(words):
                if a == b: continue

                v1 = np.zeros(dimensions)
                try: v1 = model[i][a] # if token a is in model
                except: k=0

                v2 = np.zeros(dimensions)
                try: v2 = model[i][b]
                except: k=0

                # calculate Euclidean distance between vectors
                mtx[idx1,idx2] = distance.euclidean(v1, v2)

        # normalize vector distances
        mtx = np.divide(mtx, np.max(mtx.flatten()))

        heatmap = ax.imshow(mtx, cmap=plt.cm.RdBu)
        #heatmap = ax.imshow(mtx, cmap=plt.cm.RdBu, interpolation='bilinear')


        fig.colorbar(heatmap, ax=ax)

        # set labels
        ax.set_xticks(np.arange( len(words)) )
        ax.set_yticks(np.arange( len(words)) )
        ax.set_xticklabels( words )
        ax.set_yticklabels( words )

        ax.set_aspect('auto')

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        plt.title(labels[i])

    fig.suptitle("Fig 3: Normalized vector distances between words")

    if show: plt.show()

    plt.savefig("img/fig3_distances_of_vectors.png")




if __name__ == '__main__':

    PARTIES = [
        'afd', 'blaue', 'cdu', 'csu', 'union', 'fdp', 'grune', 'linke', 'spd'
    ]
    PATH_vec2word = "word2vec.model"
    PATH_fasttext = "fasttext.model"

    plt.rcParams["figure.figsize"] = (10, 5)
    # inspired by http://nipunbatra.github.io/2014/08/latexify/


    model = [None, None]
    if not os.path.isfile(PATH_vec2word) or not os.path.isfile(PATH_fasttext):

        from data_loader import DataLoader
        loader = DataLoader()
        df = loader.get_dataframe()

        print('building vec2word model ...')
        #model[0] = Word2Vec(df['article'], size=DIMENSIONS, min_count=50, workers=5)

        size = 200
        window = 5
        min_count = 50
        sentences = df['article']
        total_examples = len(df['article'])
        epochs = 10

        model[0] = Word2Vec(size=size, window=window, min_count=min_count)
        model[0].build_vocab(sentences=sentences)  # prepare the model vocabulary
        model[0].train(sentences=sentences, total_examples=total_examples, epochs=epochs)
        model[0].save(PATH_vec2word)

        print('building fasttext model ...')
        model[1] = FastText(size=size, window=window, min_count=min_count)  # instantiate
        model[1].build_vocab(sentences=sentences)
        model[1].train(sentences=sentences, total_examples=total_examples, epochs=epochs)  # train
        model[1].save(PATH_fasttext)

    else:
        print('loading vec2word and fasttext models ...')
        model[0] = Word2Vec.load(PATH_vec2word)
        model[1] = FastText.load(PATH_fasttext)


    print('getting started ...')

    # only using vocab of vec2word, as it is the smaller one
    vocab = list(model[0].wv.vocab)

    X = [
        model[0][vocab] ,
        model[1][vocab]
    ]

    colors = [ 'g', 'b']
    labels = ['vec2word', 'fasttext']

    plot(X, vocab, colors, labels, show=False)
    plot_party_names(X, model, vocab, PARTIES, colors, labels, show=False)
    plot_distances_between_vectors(X, model, vocab, PARTIES, labels, show=False)
