import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import networkx as nx


# color scheme: https://www.colorcombos.com/color-schemes/7626/ColorCombo7626.html


# list of german stop words
STOP_WORDS = ['aber','als','am','an','auch','auf','aus','bei','bin','bis','bist','da','dadurch','daher','darum','das','daß','dass','dein','deine','dem','den','der','des','dessen','deshalb','die','dies','dieser','dieses','doch','dort','du','durch','ein','eine','einem','einen','einer','eines','er','es','euer','eure','für','hatte','hatten','hattest','hattet','hier','hinter','ich','ihr','ihre','im','in','ist','ja','jede','jedem','jeden','jeder','jedes','jener','jenes','jetzt','kann','kannst','können','könnt','machen','mein','meine','mit','muß','mußt','musst','müssen','müßt','nach','nachdem','nein','nicht','nun','oder','seid','sein','seine','sich','sie','sind','soll','sollen','sollst','sollt','sonst','soweit','sowie','und','unser','unsere','unter','vom','von','vor','wann','warum','was','weiter','weitere','wenn','wer','werde','werden','werdet','weshalb','wie','wieder','wieso','wir','wird','wirst','wo','woher','wohin','zu','zum','zur','über']


'''
This method retrieves all members of the German Bundestag of the 19th electoral term

Returns: DataFrame
'''
def get_all_members_of_bundestag(url):
     #
    bundestag_wiki_html = requests.get(url).text
    soup = BeautifulSoup(bundestag_wiki_html, 'lxml')

    members_table = soup.find('table', {'class':'wikitable sortable'})
    members_trs = members_table.find('tbody').findAll('tr')

    members = []
    links = []
    party = []
    color = []
    day_of_birth = []
    state = []

    for i in members_trs:
        tds = i.findAll('td')
        if len(tds) > 6:
            a = tds[1].find('a')
            members.append(a.get('title'))
            links.append('https://de.wikipedia.org'+str(a.get('href')))
            day_of_birth.append(tds[2].text.strip())
            party.append(tds[3].text.strip())

            color_index = str(tds[3].get('style')).find('#')
            color.append(tds[3].get('style')[color_index:color_index+7])

            state.append(tds[4].text.strip())

    assert(len(members) == 709)

    df = pd.DataFrame()
    df['members'] = members
    df['links'] = links
    df['party'] = party
    df['day_of_birth'] = day_of_birth
    df['state'] = state
    df['color'] = color

    articles = []
    for index, row in df.iterrows():
        mem = row['members']
        print('retrieving wiki article for', mem, '('+str(index)+'/'+str(709)+')')
        article_text = get_wiki_article_textonly(mem)

        # remove numbers
        tmp = ''.join([i for i in article_text if not i.isdigit()])

        # convert to lowercase
        article_text = tmp.lower()

       # remove chapters 'weblinks', 'literatur' and 'einzelnachweise'
        def remove_chapter(heading, text):
            t = text
            i = t.find(heading)
            if i > 0: # if the heading is in the text
                j = t.find('==', i+len(heading))-1 # find beginning of next chapter
                if j > 0: # if there is a following chapter
                    return t[:i-1]+t[j:]
                else: return t[:i-1]
            return t
        article_text = remove_chapter('== weblinks ==', article_text)
        article_text = remove_chapter('== literatur ==', article_text)
        article_text = remove_chapter('== einzelnachweise ==', article_text)

        articles.append(article_text)

    df['article'] = articles

    return df

'''
This method retrieves Wikipedia articles in plain text by article name using the Wikipedia API

Returns: Plain text article as string
'''
def get_wiki_article_textonly(name):

    response = requests.get(
        'https://de.wikipedia.org/w/api.php',
        params = {
            'action': 'query',
            'format': 'json',
            'titles': name,
            'prop': 'extracts',
            'explaintext': True,
        }
    ).json()
    page = next(iter(response['query']['pages'].values()))
    return page['extract']


def plot_article_length_by_parties(df):
    parties = df['party'].unique()

    average = []
    median = []
    for party in parties:
        tmp = []
        member_articles = df.loc[df['party'] == party]['article']
        for a in member_articles:
            tmp.append(len(a))
        average.append(int(np.average(tmp)))
        median.append(int(np.median(tmp)))

    #print(res)

    fig, ax = plt.subplots()
    index = np.arange(len(parties))
    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(index, average, bar_width,
    alpha=opacity,
    color='#74828F',
    label='average')

    rects2 = plt.bar(index + bar_width, median, bar_width,
    alpha=opacity,
    color='#96C0CE',
    label='median')

    plt.xlabel('parties')
    plt.ylabel('words per article')
    plt.xticks(index + bar_width, parties)
    plt.legend()
    plt.savefig('img/article_length_by_parties.png')



def plot_unique_tokens_per_party(df):
    parties = df['party'].unique()

    average = []
    median = []
    for party in parties:
        tmp = []
        member_articles = df.loc[df['party'] == party]['article']
        for a in member_articles:


            tokens = a.split(' ')


            normalized_number_unique_tokens = len(set(tokens)) / len(tokens) *100
            print(len(set(tokens)), len(tokens), normalized_number_unique_tokens)

            tmp.append(normalized_number_unique_tokens)
        average.append(int(np.average(tmp)))
        median.append(int(np.median(tmp)))

    #print(res)

    fig, ax = plt.subplots()
    index = np.arange(len(parties))
    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(index, average, bar_width,
    alpha=opacity,
    color='#74828F',
    label='average')

    rects2 = plt.bar(index + bar_width, median, bar_width,
    alpha=opacity,
    color='#96C0CE',
    label='median')

    plt.xlabel('parties')
    plt.ylabel('unique tokens per article (normalized) in percent')
    plt.xticks(index + bar_width, parties)
    plt.legend()
    plt.savefig('img/unique_tokens_per_party.png')


def calc_tfidf(df):
    to_analyze = df['article']
    #to_analyze = df.loc[df['party'] == 'AfD']['article']

    vectorizer = TfidfVectorizer(analyzer='word', stop_words=STOP_WORDS)
    response = vectorizer.fit_transform(to_analyze)

    terms = vectorizer.get_feature_names()
    #print('unique tokens:', len(vectorizer.get_feature_names()))

    # sum tfidf frequency of each term through documents
    sums = response.sum(axis=0)

    # connecting term to its sums frequency
    data = []
    for col, term in enumerate(terms):
        data.append(( term, sums[0,col] ))

    ranking = pd.DataFrame(data, columns=['term','rank'])

    #with pd.option_context('display.max_rows', 300, 'display.max_columns', None):  # more options can be specified also
        #print(ranking.sort_values('rank', ascending=False))

    return response


def calculate_cosine_similarity_with_tfidf(tfidf_matrix, index):
    if index < 0 or index > tfidf_matrix.shape[0]-1: return None

    #print(tfidf_matrix.shape)
    from sklearn.metrics.pairwise import cosine_similarity
    x = cosine_similarity(tfidf_matrix[index], tfidf_matrix)

    return x

def plot_cosine_similarity_graph_for_member_articles(tfidf_matrix, number_of_edges_per_member=20):
    df_similarity = pd.DataFrame(columns=['from', 'to'])
    for i in range(df['members'].shape[0]):
    #for i in range(10):
        # get member
        m_master = df.at[i,'members']
        # calculate cosine_similarity for member with index i
        sim = calculate_cosine_similarity_with_tfidf(tfidf_matrix, i)[0]

        members = df['members']
        # sort names of members weighted by cosine similarity
        members_sorted = [x for _,x in sorted(zip(sim, members))]


        if number_of_edges_per_member < 0 or number_of_edges_per_member > len(members_sorted):
            for m in members_sorted:
                df_similarity = df_similarity.append({'from': m_master, 'to': m}, ignore_index=True)
        else:
            for m in members_sorted[:number_of_edges_per_member]:
                df_similarity = df_similarity.append({'from': m_master, 'to': m}, ignore_index=True)

        #print(df_similarity)



    G = nx.from_pandas_dataframe(df_similarity, 'from', 'to', create_using=nx.Graph() )

    # color nodes after party
    color_map = []
    for node in G:
        c = df.loc[df['members'] == node]['color'].to_string(header=False,index=False)
        color_map.append(c)

    nx.draw(G, with_labels=False, node_size=30, alpha=0.2, arrows=False, node_color=color_map)

    #nx.draw(G, with_labels=False, node_size=15, alpha=0.3, arrows=False)

    plt.savefig('img/cosine_similarity.png')

if __name__ == '__main__':

    pickle_file_name = 'members_bundestag.pkl'

    # save retrieved data as pickle and load if it already exists
    if not os.path.isfile(pickle_file_name):
        url_members_german_bundestag = 'https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Deutschen_Bundestages_(19._Wahlperiode)'
        df = get_all_members_of_bundestag(url_members_german_bundestag)
        print('saving ...')
        df.to_pickle(pickle_file_name)
    else:
        print('loading from pickle ...\n')
        df = pd.read_pickle(pickle_file_name)

    print('parties:', df['party'].unique())

    plot_article_length_by_parties(df)
    plt.show()

    plot_unique_tokens_per_party(df)
    plt.show()

    # calculate tfidf matrix
    tfidf_matrix = calc_tfidf(df)

    plot_cosine_similarity_graph_for_member_articles(tfidf_matrix, number_of_edges_per_member=3)
    plt.show()




