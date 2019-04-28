from sklearn.feature_extraction.text import TfidfVectorizer
from matplotlib import pyplot as plt
import numpy as np

from data_loader import DataLoader

# list of german stop words
STOP_WORDS = \
    [
        'aber','als','am','an','auch','auf','aus','bei','bin','bis','bist','da','dadurch','daher','darum',
        'das','daß','dass','dein','deine','dem','den','der','des','dessen','deshalb','die','dies','dieser',
        'dieses','doch','dort','du','durch','ein','eine','einem','einen','einer','eines','er','es','euer',
        'eure','für','hatte','hatten','hattest','hattet','hier','hinter','ich','ihr','ihre','im','in','ist',
        'ja','jede','jedem','jeden','jeder','jedes','jener','jenes','jetzt','kann','kannst','können','könnt',
        'machen','mein','meine','mit','muß','mußt','musst','müssen','müßt','nach','nachdem','nein','nicht',
        'nun','oder','seid','sein','seine','sich','sie','sind','soll','sollen','sollst','sollt','sonst',
        'soweit','sowie','und','unser','unsere','unter','vom','von','vor','wann','warum','was','weiter',
        'weitere','wenn','wer','werde','werden','werdet','weshalb','wie','wieder','wieso','wir','wird',
        'wirst','wo','woher','wohin','zu','zum','zur','über'
    ]


def plot_wordcloud_per_party(df, docs, vocabulary):
    for party in df['party'].unique():

        # get tfidf vectors for party
        indices = df.index[df['party'] == party].tolist()
        docs_per_party = docs[indices]

        # sum up the word frequency per word
        freqs = dict([(word, docs_per_party.getcol(idx).sum()) for word, idx in vocabulary])

        print('generating wordcloud for', party, '...')

        from wordcloud import WordCloud
        w = WordCloud(width=1200, height=900, mode='RGBA', background_color='white', max_words=2000).fit_words(freqs)

        plt.imsave('img/wordcloud_'+party+'.png', w)

def plot_with_tsne_by_age(df, X_embedded, show=True):

    print('generating plot ...')
    # Plot
    fig, ax = plt.subplots()
    res = np.array(X_embedded)

    import time
    year = time.strftime("%Y,%m,%d,%H,%M").split(',')[0]
    age = np.array([int(year)-int(i) for i in df['day_of_birth']])

    for i in range(int(age.min()/10), int(round(age.max()/10))):

        min = i*10
        max = i*10+9

        indices = np.where(np.logical_and(age>=min, age<=max))

         # get all related values from t-SNE result
        res_for_age = np.array(list(res[indices]))

        x = res_for_age[:,0]
        y = res_for_age[:,1]

        ax.scatter(x, y, label=(str(min)+' to '+str(max)), alpha=0.5)
        ax.legend()
        ax.grid(True)

    if show: plt.show()

    print('saving plot ...')
    fig.savefig('img/tsne_plot_per_age.png')

def plot_with_tsne_by_state(df, X_embedded, show=True):

    print('generating plot ...')
    # Plot
    fig, ax = plt.subplots()
    res = np.array(X_embedded)

    for state in df['state'].unique():

        # get all indices for selected party
        indices = df.index[df['state'] == state].tolist()

        # get all related values from t-SNE result
        res_for_party = np.array(list(res[indices]))

        x = res_for_party[:,0]
        y = res_for_party[:,1]

        ax.scatter(x, y, label=state, alpha=0.5)
        ax.legend()
        ax.grid(True)

    if show: plt.show()

    print('saving plot ...')
    fig.savefig('img/tsne_plot_per_state.png')


def plot_with_tsne_by_party(df, X_embedded, show=True):

    print('generating plot ...')
    # Plot
    fig, ax = plt.subplots()
    res = np.array(X_embedded)

    for party in df['party'].unique():

        # get related color
        color = df.loc[df['party'] == party]['color'].unique()

        # color hack
        if party == 'Blaue': color = '#0000FF'
        elif party == 'parteilos': color = '#FF9900'

        # get all indices for selected party
        indices = df.index[df['party'] == party].tolist()

        # get all related values from t-SNE result
        res_for_party = np.array(list(res[indices]))

        x = res_for_party[:,0]
        y = res_for_party[:,1]

        ax.scatter(x, y, c=color, label=party, alpha=0.5)
        ax.legend()
        ax.grid(True)

    if show: plt.show()

    print('saving plot ...')
    fig.savefig('img/tsne_plot_per_party.png')

def plot_with_tsne_by_party_with_wordcount(df, X_embedded, show=True):

    print('generating plot ...')
    # Plot
    fig, ax = plt.subplots()
    res = np.array(X_embedded)

    all_sizes = np.array([len(a.split(' ')) for a in df['article']])

    for party in df['party'].unique():

        # get related color
        color = df.loc[df['party'] == party]['color'].unique()

        # color hack
        if party == 'Blaue': color = '#0000FF'
        elif party == 'parteilos': color = '#FF9900'

        # get all indices for selected party
        indices = df.index[df['party'] == party].tolist()

        # get all related values from t-SNE result
        res_for_party = np.array(list(res[indices]))

        # get number of words for each article
        size = [(len(a.split(' '))-all_sizes.min())/all_sizes.max()*100 for a in df.loc[df['party'] == party]['article']]
        #size = [np.exp(len(a.split(' '))) for a in df.loc[df['party'] == party]['article']]

        x = res_for_party[:,0]
        y = res_for_party[:,1]

        ax.scatter(x, y, c=color, s=size, label=party, alpha=0.5)
        ax.legend()
        ax.grid(True)

    if show: plt.show()

    print('saving plot ...')
    fig.savefig('img/tsne_plot_per_party_with_article_size.png')

def plot_with_3d_tsne_by_party(docs, show=True):
    print('calculating 3D t-SNE ...')
    X = docs.toarray()
    from sklearn.manifold import TSNE
    tsne = TSNE(n_components=3)
    X_embedded = tsne.fit_transform(X)
    res = np.array(X_embedded)

    fig = plt.figure()

    #ax = fig.add_subplot(111, projection='3d')
    from mpl_toolkits.mplot3d import Axes3D
    ax = Axes3D(fig)


    for party in df['party'].unique():

        # get related color
        color = df.loc[df['party'] == party]['color'].unique()

        # color hack
        if party == 'Blaue': color = '#0000FF'
        elif party == 'parteilos': color = '#FF9900'

        # get all indices for selected party
        indices = df.index[df['party'] == party].tolist()

        # get all related values from t-SNE result
        res_for_party = np.array(list(res[indices]))

        x = res_for_party[:,0]
        y = res_for_party[:,1]
        z = res_for_party[:,2]

        ax.scatter(x, y, z, c=color, label=party, alpha=0.5)
        ax.legend()
        ax.grid(True)

    if show: plt.show()

    print('saving plot ...')
    fig.savefig('img/tsne_3d_plot_per_party.png')


if __name__ == '__main__':

    loader = DataLoader()
    df = loader.get_dataframe()

    # execute TF-IDF
    print('generating TF-IDF vectors ...')
    vectorizer = TfidfVectorizer(analyzer='word', stop_words=STOP_WORDS)
    docs = vectorizer.fit_transform(df['article'])


    #plot_wordcloud_per_party(df, docs, vectorizer.vocabulary_.items())



    print('calculating t-SNE ...')
    X = docs.toarray()
    from sklearn.manifold import TSNE
    tsne = TSNE(n_components=2)
    X_embedded = tsne.fit_transform(X)

    plot_with_tsne_by_age(df, X_embedded, show=False)
    plot_with_tsne_by_state(df, X_embedded, show=False)
    plot_with_tsne_by_party(df, X_embedded, show=False)
    plot_with_3d_tsne_by_party(docs, show=False)
    plot_with_tsne_by_party_with_wordcount(df, X_embedded, show=False)




    '''
    # PCA
    from sklearn.decomposition import PCA
    pca = PCA()
    pca.fit(docs)
    print(docs.shape)
    '''














