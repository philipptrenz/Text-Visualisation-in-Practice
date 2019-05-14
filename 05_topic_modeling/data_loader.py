import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import unicodedata
import inflect
import nltk
from nltk.corpus import stopwords
from nltk.stem import lancaster
from nltk.stem import wordnet

class DataLoader:

    '''
    Constructor
    '''
    def __init__(self, path='members_bundestag.pkl'):

        # save retrieved data as pickle and load if it already exists
        if not os.path.isfile(path):
            url_members_german_bundestag = 'https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Deutschen_Bundestages_(19._Wahlperiode)'
            self.dataframe = self.get_all_members_of_bundestag(url_members_german_bundestag)
            print('saving pickle ...')
            self.dataframe.to_pickle(path)
        else:
            print('loading from pickle ...')
            self.dataframe = pd.read_pickle(path)

    def get_dataframe(self):
        return self.dataframe

    def tokenize(self, sample):
        words = nltk.word_tokenize(sample)
        return words

    def remove_non_ascii(self, words):
        """Remove non-ASCII characters from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
            new_words.append(new_word)
        return new_words

    def to_lowercase(self, words):
        """Convert all characters to lowercase from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = word.lower()
            new_words.append(new_word)
        return new_words

    def remove_punctuation(self, words):
        """Remove punctuation from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = re.sub(r'[^\w\s]', '', word)
            if new_word != '':
                new_words.append(new_word)
        return new_words

    def replace_numbers(self, words):
        """Replace all interger occurrences in list of tokenized words with textual representation"""
        p = inflect.engine()
        new_words = []
        for word in words:
            if word.isdigit():
                new_word = p.number_to_words(word)
                new_words.append(new_word)
            else:
                new_words.append(word)
        return new_words

    def remove_stopwords(self, words, lang):
        """Remove stop words from list of tokenized words"""
        new_words = []
        for word in words:
            if word not in stopwords.words(lang):
                new_words.append(word)
        return new_words

    def stem_words(self, words):
        """Stem words in list of tokenized words"""
        stemmer = lancaster.LancasterStemmer()
        stems = []
        for word in words:
            stem = stemmer.stem(word)
            stems.append(stem)
        return stems

    def lemmatize_verbs(self, words):
        """Lemmatize verbs in list of tokenized words"""
        lemmatizer = wordnet.WordNetLemmatizer()
        lemmas = []
        for word in words:
            lemma = lemmatizer.lemmatize(word, pos='v')
            lemmas.append(lemma)
        return lemmas

    def normalize(self, words, lang='english'):
        words = self.remove_non_ascii(words)
        words = self.to_lowercase(words)
        words = self.remove_punctuation(words)
        words = self.replace_numbers(words)
        words = self.remove_stopwords(words, lang)
        words = self.stem_words(words)
        words = self.lemmatize_verbs(words)
        return words

    '''
    This method retrieves all members of the German Bundestag of the 19th electoral term
    
    Returns: DataFrame
    '''
    def get_all_members_of_bundestag(self, url):
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
            article_text = self.get_wiki_article_textonly(mem)

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


            article_text = self.tokenize(article_text)
            article_text = self.normalize(article_text, lang='german')

            #print(article_text)

            articles.append(article_text)

        df['article'] = articles


        return df


    '''
    This method retrieves Wikipedia articles in plain text by article name using the Wikipedia API
    
    Returns: Plain text article as string
    '''
    def get_wiki_article_textonly(self, name):

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
