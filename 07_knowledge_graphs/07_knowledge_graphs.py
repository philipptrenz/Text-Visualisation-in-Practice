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
import nltk.data
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pycorenlp import StanfordCoreNLP

from data_loader import DataLoader


def process_openie(df):
    nlp = StanfordCoreNLP('http://localhost:9000')

    #nlp = StanfordCoreNLP('http://corenlp.run:80')

    predicates = dict()
    triples = dict()

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    for index, row in df.iterrows():

        print('\n(' + str(index+1) + ') '+ row['name'] + ':')

        triples[row['name']] = list()

        #sentence = "Twenty percent electric motors are pulled from an assembly line"
        paragraphs = row['article'].split('\n\n')

        #paragraphs = paragraphs[:2] # only take first two paragraphs

        for paragraph in paragraphs:

            sentences = tokenizer.tokenize(paragraph)

            for s in sentences:

                s = s.strip()

                if len(s) == 0 or s.strip().startswith("=="): continue # skip headings

                print('\t\'' + s + '\'')


                output = nlp.annotate(s, properties = {
                    "annotators": "tokenize,ssplit,pos,depparse,natlog,openie",
                    "outputFormat": "json",
                    "triple.strict": "true",
                    "openie.triple.strict": "true",
                    "openie.max_entailments_per_clause": "1",
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


        data['triples'] = triples
        data['predicates'] = predicates

        json.dump(data, fp, sort_keys=True, indent=4)

    print('\n\npredicates:', predicates)
    return data


def find_predicates_related_to_membership(data):
    num_predicates = sum(data['predicates'].values())
    member_predicates = list()
    num_member_predicates = 0
    for key in data['predicates']:
        val = data['predicates'][key]
        if 'member' in key.lower() or 'mp ' in key.lower() or ' mp' in key.lower():

            member_predicates.append(key)
            num_member_predicates += val
    print(num_member_predicates, 'of', num_predicates, '(' + str(int(num_member_predicates/num_predicates*100)) + '%) member predicates,', len(member_predicates), 'different ones')

    return member_predicates



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

    def absolute_value(val):
        return int(np.round(val/100.*sum(sizes), 0))

    # Plot
    plt.pie(sizes, labels=labels, autopct=absolute_value, shadow=True, startangle=140)

    plt.axis('equal')
    if show: plt.show()

    plt.title('Distribution of predicates over all Wikipedia articles')

    plt.savefig('img/predicates_pie_chart.png')


def get_graph_for_name(name, data, debug=False):

    found = False
    for n in data['triples']:
        if name in n:
            name = n
            found = True
            break

    if not found:
        if debug: print('shit')
        return

    name_fixed = name
    if name.find('(') > 0: name_fixed = name[:name.find('(')].strip()

    if debug: print(name_fixed)

    graph = dict()
    graph['name']  = name_fixed
    graph['nodes'] = list()
    graph['edges'] = list()


    def correct_name(input):
        _input = input.lower().strip()
        for n in name_fixed.lower().split(' '):
            if n in _input:
                return name_fixed
        if 'he' in _input or 'she' in _input:
            return name_fixed
        return input

    for triple in data['triples'][name]:

        e1 = triple[0]
        e2 = correct_name(triple[1])
        e3 = correct_name(triple[2])

        if debug: print(triple)


        graph['nodes'].append(e2)
        graph['nodes'].append(e3)
        graph['edges'].append({ 'from': e2, 'to': e3, 'label': e1})


    return graph


def get_all_connected_nodes(node, graph):
    nodes = list()
    edges = list()
    for e in graph['edges']:
        if node == e['from'] and node == e['to']: continue
        if node == e['from']:
            nodes.append(e['to'])
            edges.append(e)
        if node == e['to']:
            nodes.append(e['from'])
            edges.append(e)
    return nodes, edges

def limit_graph_to_only_name_related_nodes(graph):

    new_graph = dict()
    new_graph['name'] = graph['name']
    new_graph['nodes'] = list()
    new_graph['edges'] = list()

    # select only nodes that are connect to 'name' node
    todo = set()
    todo.add(graph['name'])

    while len(todo) > 0:
        n = todo.pop()

        if n in new_graph['nodes']: continue # prevent circles

        ns, es = get_all_connected_nodes(n, graph)

        for x in ns: todo.add(x)

        new_graph['nodes'].append(n)
        new_graph['edges'].extend(es)

    return new_graph


def draw_graph_for_name(name, data, only_name_related_nodes=False, show=False, save=True):
    graph = get_graph_for_name(name, data)

    G = nx.Graph()
    plt.title(graph['name'])

    # TODO: limit nodes to only_name_related_nodes


    if only_name_related_nodes:
        graph = limit_graph_to_only_name_related_nodes(graph)

    G.add_nodes_from(graph['nodes'])

    edge_labels = {}
    for edge in graph['edges']:
        G.add_edge(edge['from'], edge['to'])
        tmp = (edge['from'], edge['to'])
        edge_labels[tmp] = edge['label']


    pos = nx.spring_layout(G)

    nx.draw(G, pos , edge_color='black', width=1, linewidths=1, node_size=800, node_color='pink',alpha=0.9, labels={ node:node for node in G.nodes() }, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=10)

    plt.axis('off')

    if show: plt.show()
    if save: plt.savefig('img/graph_'+graph['name'].lower().replace(' ', '_'))

    plt.clf()
    plt.cla()
    plt.close()

if __name__ == '__main__':

    plt.rcParams["figure.figsize"] = (14, 8)

    loader = DataLoader()
    df = loader.get_dataframe()

    data = dict()
    if not os.path.isfile('data.json'):
        data = process_openie(df)
    else:
        with open('data.json', 'r') as f:
            data = json.load(f)

    #plot_pie_chart_of_predicates(data, threshhold=0.7)

    #membership_predicates = find_predicates_related_to_membership(data)

    i = 0
    for name in data['triples']:
        i += 1
        print(i)
        draw_graph_for_name(name, data, only_name_related_nodes=True, show=False, save=True)



