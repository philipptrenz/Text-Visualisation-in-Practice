# Knowledge Graph Construction (open IE approach)
#   * Install and set up Open IE (Stanford/AllenAI/ Graphene)
#   * Extract the triples for a reasonably sized dataset
#   * Perform entity disambiguation and canonicalization for the triples.
#   * Create a basic knowledge graph from the data
#   * Come up with creative visualizations, play around with various tools
#

import json
import numpy as np
import pandas as pd
from pycorenlp import StanfordCoreNLP

from data_loader import DataLoader



if __name__ == '__main__':

    loader = DataLoader()
    df = loader.get_dataframe()

    nlp = StanfordCoreNLP('http://localhost:9000')

    #nlp = StanfordCoreNLP('http://corenlp.run:80')

    for index, row in df.iterrows():

        #sentence = "Twenty percent electric motors are pulled from an assembly line"
        paragraph = row['article'].split('\n\n')[0]


        for p in paragraph.split('\n'):


            for s in p.split('. '):

                s = s.strip()

                if len(s) == 0 or s.startswith("=="): continue # skip headings

                print('Sentence: \n\t \'' + s + '\'\nResult:')


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
                        relationSent=rel['relation'],rel['subject'],rel['object']
                        print('\t', relationSent)

                print('\n')



        break
