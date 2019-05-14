import os
from gensim.models import ldamodel
from gensim.test.utils import datapath
from gensim.test.utils import common_texts
from gensim.corpora import Dictionary
from matplotlib import pyplot as plt

if __name__ == '__main__':

    PARTIES = [
        'afd', 'blaue', 'cdu', 'csu', 'union', 'fdp', 'grune', 'linke', 'spd'
    ]
    PATH_lda = "lda.model"

    plt.rcParams["figure.figsize"] = (10, 5)
    # inspired by http://nipunbatra.github.io/2014/08/latexify/


    model = [None, None]
    if not os.path.isfile(PATH_lda):
        from data_loader import DataLoader
        loader = DataLoader()
        df = loader.get_dataframe()

        print('building LDA model ...')

        # Create a corpus from a list of texts
        dictionary = Dictionary(df['article'])

        corpus = [dictionary.doc2bow(text) for text in df['article']]

        # Train model
        lda = ldamodel.LdaModel(corpus, num_topics=50, alpha='auto', eval_every=5)  # learn asymmetric alpha from data

        # Save model to disk.
        temp_file = datapath("model")
        lda.save(PATH_lda)


    else:
        print('loading lda model ...')
        lda = ldamodel.LdaModel.load(PATH_lda)


    print('getting started ...')


    # print topics
    for i in range(0, lda.num_topics):
        t = lda.show_topic(i)
        print(t)

