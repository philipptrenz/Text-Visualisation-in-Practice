import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

class DataLoader:

    '''
    Constructor
    '''
    def __init__(self, path='members_house_of_common.pkl'):

        # save retrieved data as pickle and load if it already exists
        if not os.path.isfile(path):
            url_members_german_bundestag = 'https://en.wikipedia.org/wiki/List_of_MPs_elected_in_the_2017_United_Kingdom_general_election'
            self.dataframe = self.get_all_members_of_house_of_common(url_members_german_bundestag)
            print('saving pickle ...')
            self.dataframe.to_pickle(path)
        else:
            print('loading from pickle ...')
            self.dataframe = pd.read_pickle(path)

    def get_dataframe(self):
        return self.dataframe

    '''
    This method retrieves all members of the German Bundestag of the 19th electoral term
    
    Returns: DataFrame
    '''
    def get_all_members_of_house_of_common(self, url):
         #
        bundestag_wiki_html = requests.get(url).text
        soup = BeautifulSoup(bundestag_wiki_html, 'lxml')

        members_table = soup.find_all('table', {'class':'wikitable sortable'})[-2]
        members_trs = members_table.find('tbody').findAll('tr')

        constituency = []
        color = []
        party = []
        name = []
        links = []
        notes = []

        for i in members_trs:
            tds = i.findAll('td')
            if len(tds) < 7: continue

            constituency.append( str(tds[0].find('a').string) )
            links.append( 'https://de.wikipedia.org' + str( tds[0].find('a').get('href') ) )
            color_index = str(tds[3].get('style')).find('#')
            color.append( str(tds[1].get('style')[color_index:color_index+7]) )
            party.append( str(tds[2].find('a').string) )
            name.append( str(tds[5].find('a').get('title')) )


            note = tds[6].string

            if (note is not None): notes.append( note.strip() )
            else: notes.append( '' )


        df = pd.DataFrame()
        df['costituency'] = constituency
        df['color'] = color
        df['party'] = party
        df['name'] = name
        df['link'] = links
        df['note'] = notes

        articles = []
        for index, row in df.iterrows():
            mem = row['name']

            print('retrieving wiki article for', mem, '('+str(index+1)+'/'+str(650)+')')
            article_text = self.get_wiki_article_textonly(mem)

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
            article_text = remove_chapter('== See also ==', article_text)
            article_text = remove_chapter('== References ==', article_text)
            article_text = remove_chapter('== External links ==', article_text)

            articles.append(str(article_text))


        df['article'] = articles

        print(df)


        return df


    '''
    This method retrieves Wikipedia articles in plain text by article name using the Wikipedia API
    
    Returns: Plain text article as string
    '''
    def get_wiki_article_textonly(self, name):

        response = requests.get(
            'https://wikipedia.org/w/api.php',
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
