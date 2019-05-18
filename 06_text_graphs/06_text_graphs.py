import os
import numpy as np
import pandas as pd
import json
from multiprocessing import Process, Manager

from gensim.models import TfidfModel
from gensim.models import FastText
from gensim.corpora import Dictionary

from sklearn.metrics.pairwise import cosine_similarity


def calculate_nodes(dct, df):

    print('preparing node export')

    def worker(all_nodes, process_id, dct, df, min, max):
        if max > len(dct): max = len(dct)

        for token_id in range(min, max):

            token = dct[token_id]
            count = 0

            for index, row in df.iterrows():
                if token in row['article']: count += 1

            #if count > 10:  # min count
            all_nodes.append({
                'single_couses': 0,
                'name': token,
                'uses': count
            })

            print(int((token_id-min)/(max-min)*100),'% (worker', process_id, ')')

    with Manager() as manager:
        workers = 20
        workload = int(len(dct)/workers)

        all_nodes = manager.list()  # <-- can be shared between processes.
        processes = []
        for i in range(workers):

            min = i * workload
            max = (i+1) * workload

            p = Process(target=worker, args=(all_nodes,i, dct, df, min, max))  # Passing the list
            p.start()
            processes.append(p)
        for p in processes:
            p.join()

        return list(all_nodes)


def get_all_nodes(dct, df):
    all_nodes = []
    all_nodes_file = 'nodes_all.json'

    if not os.path.isfile(all_nodes_file):

         # calculate all nodes
        all_nodes = calculate_nodes(dct, df)

        with open(all_nodes_file, 'w') as f:
            f.write(json.dumps(all_nodes))
    else:
        with open(all_nodes_file) as f:
            all_nodes = json.load(f)

    return all_nodes


def calculate_edges(export_nodes, model):
    all_edges = []
    print('calculating edges ...')
    i = 0
    for n1 in export_nodes:

        for n2 in export_nodes:
            token1 = n1["name"]
            token2 = n2["name"]
            if token1 == token2: continue

            sim = cosine_similarity(model[token1].reshape(1, -1), model[token2].reshape(1, -1))[0,0]
            all_edges.append({
                'source': token1,
                'target': token2,
                'value': float(sim)
            })

        i += 1
        print('processed', i, 'of', len(export_nodes), 'edges')

    return all_edges

def get_all_edges(export_nodes, model):
    all_edges = []
    all_edges_file = 'links_all.json'
    if not os.path.isfile(all_edges_file):

         # calculate all edges
        all_edges = calculate_edges(export_nodes, model)

        with open(all_edges_file, 'w') as f:
            f.write(json.dumps(all_edges))
    else:
        with open(all_edges_file) as f:
            all_edges = json.load(f)

    return all_edges



def get_fasttext_model(df):

    fasttext_model_file = 'fasttext.model'
    model = None
    if not os.path.isfile(fasttext_model_file):
        print('building fasttext model ...')

        size = 50
        window = 5
        sentences = df['article']
        total_examples = len(sentences)
        epochs = 10

        model = FastText(size=size, window=window)  # instantiate
        model.build_vocab(sentences=sentences)
        model.train(sentences=sentences, total_examples=total_examples, epochs=epochs)  # train
        model.save(fasttext_model_file)
    else:
        print('loading fasttext model ...')
        model = FastText.load(fasttext_model_file)

    return model

def write_export(export_nodes, export_edges):

    with open('nodes.json', 'w') as f:
        f.write(json.dumps(export_nodes))

    with open('links.json', 'w') as f:
        f.write(json.dumps(export_edges))


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


    ####################################


    print('getting all nodes ...')
    all_nodes = get_all_nodes(dct, df)


    print('filtering all nodes to relevant ones ...')
    export_nodes = []
    for n in all_nodes:
        # TODO: Adjust value
        if n["uses"] > 40: # if word occures in more than X documents
            export_nodes.append(n)


    print('getting fasttext model ...')
    model = get_fasttext_model(df)


    print('getting all edges ...')
    all_edges = get_all_edges(export_nodes, model)


    print('filtering all edges to relevant ones ...')
    '''
    export_edges = []
    for l in all_edges:
        # TODO: Adjust value
        if l['value'] > 0.9:
            export_edges.append(l)
    '''
    # get the 1000 most significant edges
    export_edges=sorted(all_edges, key=lambda k:k['value'])[-1000:]


    ####################################

    print('calculating couses (whatever that is)')
    for node in export_nodes:
        for edge in export_edges:
            if edge['source'] == node['name'] or edge['target'] == node['name']:
                node['single_couses'] += edge['value']

    ####################################

    print('writing exports')
    write_export(export_nodes, export_edges)
