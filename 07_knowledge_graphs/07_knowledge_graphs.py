#
# Option 1 – Ontology Design with Protégé (create a simple art ontology with Protégé )
#   * Install Protégé, follow simple tutorials to get the idea of the software tool
#   * Design a basic ontology for the art and cultural heritage domain
#   * Visualize it with Protégé, other tools
#
#
# Option 2 - Knowledge Graph Construction (open IE approach)
#   * Install and set up Open IE (Stanford/AllenAI/ Graphene)
#   * Extract the triples for a reasonably sized dataset
#   * Perform entity disambiguation and canonicalization for the triples.
#   * Create a basic knowledge graph from the data
#   * Come up with creative visualizations, play around with various tools
#

from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')


s = "Twenty percent electric motors are pulled from an assembly line"

output = nlp.annotate(s, properties={
    "annotators": "tokenize,ssplit,pos,depparse,natlog,openie",
    "outputFormat": "json",
    "triple.strict": "true",
    "openie.triple.strict": "true",
    "openie.max_entailments_per_clause": "1",
    "splitter.disable": "true"
})

result = [output["sentences"][0]["openie"] for item in output]
print(result)


for i in result:
    for rel in i:
        relationSent = rel['relation'], rel['subject'], rel['object']
        print(relationSent)
