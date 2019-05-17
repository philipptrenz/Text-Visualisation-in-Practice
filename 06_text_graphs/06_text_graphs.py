import os
import numpy as np
import pandas as pd
import json


from gensim.models import TfidfModel
from gensim.models import FastText
from gensim.corpora import Dictionary

from sklearn.metrics.pairwise import cosine_similarity


if __name__ == '__main__':

    from data_loader import DataLoader
    loader = DataLoader(force=False)
    df = loader.get_dataframe()

    dataset = df['article']

    dct = Dictionary(dataset)  # fit dictionary
    corpus = [dct.doc2bow(line) for line in dataset]  # convert corpus to BoW format

    PATH = 'tfidf.model'
    model = None
    if not os.path.isfile(PATH):
        model = TfidfModel(corpus, id2word=dct)  # fit model
        model.save(PATH)
    else:
        model = TfidfModel.load(PATH)

    corpus_tfidf = model[corpus]

    #########

    def calculate_nodes():

        print('preparing node export')
        export_nodes = []

        for token_id in dct:
            token = dct[token_id]
            count = 0

            for index, row in df.iterrows():
                if token in row['article']: count += 1

            #if count > 10:  # min count
            export_nodes.append({
                'single_couses': 0,
                'name': token,
                'uses': count
            })

            print(token_id, '/', len(dct))

        print(f'exporting {len(export_nodes)} nodes')

        print('writing node exports')
        with open('nodes_all.json', 'w') as f:
            f.write(json.dumps(export_nodes))
    # calculate_nodes()

    export_nodes = []
    with open('nodes_all.json') as json_file:
        all_nodes = json.load(json_file)

        for n in all_nodes:
            if n["uses"] > 25: # if word occures in more than 15 documents
                export_nodes.append(n)


    PATH_fasttext = 'fasttext.model'
    model = None
    if not os.path.isfile(PATH_fasttext):
        print('building fasttext model ...')

        size = 200
        window = 5
        sentences = df['article']
        total_examples = len(sentences)
        epochs = 10

        model = FastText(size=size, window=window)  # instantiate
        model.build_vocab(sentences=sentences)
        model.train(sentences=sentences, total_examples=total_examples, epochs=epochs)  # train
        model.save(PATH_fasttext)
    else:

        print('loading fasttext model ...')
        model = FastText.load(PATH_fasttext)

    vocab = list(model.wv.vocab)

    print('calculating edges ...')
    similarities = []
    export_links = []

    i=0
    for n1 in export_nodes:
        for n2 in export_nodes:
        #if source in relevant_token and target in relevant_token:
            token1 = n1["name"]
            token2 = n2["name"]

            if token1 == token2: continue

            sim = cosine_similarity(model[token1].reshape(1, -1), model[token2].reshape(1, -1))[0,0]

            if sim > 0.95:
                export_links.append({
                    'source': token1,
                    'target': token2,
                    'value': float(sim)
                })

        #if len(export_links) > 2000 and not False: break
        i += 1
        print(i, '/', len(export_nodes), '(', len(export_links), 'elements)')
    print(f'exporting {len(export_links)} links')

    print('calculating couses (whatever that is)')
    for node in export_nodes:
        for link in export_links:
            if link['source'] == node['name'] or link['target'] == node['name']:
                node['single_couses'] += link['value']

    print('writing exports')
    with open('links.json', 'w') as f:
        f.write(json.dumps(export_links))

    with open('nodes.json', 'w') as f:
        f.write(json.dumps(export_nodes))
