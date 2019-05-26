# Knowledge Graph Construction (open IE approach)
#   * Install and set up Open IE (Stanford/AllenAI/ Graphene)
#   * Extract the triples for a reasonably sized dataset
#   * Perform entity disambiguation and canonicalization for the triples.
#   * Create a basic knowledge graph from the data
#   * Come up with creative visualizations, play around with various tools
#

import os
import json
import string
import operator
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pycorenlp import StanfordCoreNLP

from data_loader import DataLoader


def process_openie(df):
    nlp = StanfordCoreNLP('http://localhost:9000')

    #nlp = StanfordCoreNLP('http://corenlp.run:80')

    predicates = dict()
    triples = dict()

    for index, row in df.iterrows():

        print('\n(' + index+1 + ')'+ row['name'] + ':')

        triples[row['name']] = list()

        #sentence = "Twenty percent electric motors are pulled from an assembly line"
        paragraph = row['article'].split('\n\n')[0]


        for p in paragraph.split('\n'):


            for s in p.split('. '):

                s = s.strip()

                if len(s) == 0 or s.startswith("=="): continue # skip headings

                print('\t\'' + s + '\'')


                output = nlp.annotate(s, properties = {
                    "annotators": "tokenize,ssplit,pos,depparse,natlog,openie",
                    "outputFormat": "json",
                    "triple.strict": "true",
                    "openie.triple.strict": "true",
                    #"openie.max_entailments_per_clause": "1",
                    #"splitter.disable": "true"
                })


                result = [output["sentences"][0]["openie"] for item in output]
                #print(result)

                for i in result:
                    for rel in i:

                        # count predicates
                        predicate = rel['relation'].lower()

                        # skip predicates with special characters
                        if any(char in set(string.punctuation) for char in predicate):
                            continue

                        if predicate in predicates:
                            predicates[predicate] += 1
                        else:
                            predicates[predicate] = 1

                        relationSent = predicate, rel['subject'], rel['object']
                        triples[row['name']].append(relationSent)

                        print('\t\t', relationSent)

    data = dict()
    with open('data.json', 'w') as fp:


        tmp['triples'] = triples
        tmp['predicates'] = predicates

        json.dump(tmp, fp, sort_keys=True, indent=4)

    print('\n\npredicates:', predicates)
    return data



def plot_pie_chart_of_predicates(data, threshhold=0.6, show=False):
    counter = 0


    # sort data
    predicates = sorted(data['predicates'].items(), key=operator.itemgetter(1), reverse=True)
    num_predicates = sum(data['predicates'].values())

    # reduce data
    predicates_reduced = dict()
    for i in predicates:
        key, val = i
        if ((counter+val)/num_predicates) > threshhold: break
        counter += val
        predicates_reduced[key] = val
    predicates_reduced['others'] = num_predicates-counter

    # Data to plot
    labels = list(predicates_reduced.keys())
    sizes = list(predicates_reduced.values())
    #colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    #explode = (0.1, 0, 0, 0)  # explode 1st slice

    def absolute_value(val):
        return int(np.round(val/100.*sum(sizes), 0))

    # Plot
    plt.pie(sizes, labels=labels, autopct=absolute_value, shadow=True, startangle=140)

    plt.axis('equal')
    if show: plt.show()

    plt.title('Distribution of predicates over all Wikipedia articles')

    plt.savefig('img/predicates_pie_chart.png')


if __name__ == '__main__':

    loader = DataLoader()
    df = loader.get_dataframe()

    data = dict()
    if not os.path.isfile('data.json'):
        data = process_openie(df)
    else:
        with open('data.json', 'r') as f:
            data = json.load(f)

    plot_pie_chart_of_predicates(data, threshhold=0.7)










