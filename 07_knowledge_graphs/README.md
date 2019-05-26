# Knowledge graphs about the House of Commons (UK)

> **Date:** 26.05. *(Due: 28.05.)*  
> **Name:** `PhTr` Philipp Trenz  
> **Code:**
> [git](https://github.com/philipptrenz/Text-Visualisation-in-Practice/tree/master/07_knowledge_graphs)  
> **Session:** [Knowledge Graphs](../index)

----

## Intro

As the topic of this weeks blogpost are
[Ontologies and Knowledge Graphs](https://en.wikipedia.org/wiki/Ontology_(information_science)),
I chose to investigate Wikipedia articles again.

## Approach

As I wanted to use the
[OpenIE annotator](https://stanfordnlp.github.io/CoreNLP/openie.html)
within the [Stanford CoreNLP](http://stanfordnlp.github.io) and it only
provides models only for the English language, I had to change my
dataset. Instead of the members of the German Parliament I'm retrieving
the Wikipedia articles about the members of the
[United Kingdom House Of Commons](https://de.wikipedia.org/wiki/House_of_Commons).
As a basis this
[list of MPs elected in the 2017 United Kingdom general election](https://en.wikipedia.org/wiki/List_of_MPs_elected_in_the_2017_United_Kingdom_general_election).

### Install
 
To install CoreNLP the JavaSDK 1.8 as well as loading the compiled
sources of the server is required. The scripts included in the
repository provide an easy way to load an execute the CoreNLP server.

```bash
# Load CoreNLP for OpenIE with Models for German
sh get_corenlp.sh

# Start CoreNLP
sh start_corenlp.sh
```

After starting the server, requests can be sent to it via port 9000. For
this task I use the Python package `pycorenlp`.

```python
from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')
```

## Result

After mining the new dataset, normalizing the Wikipedia articles and
setting up the processing pipeline, which took quite long due to several
software and compatibility issues, the CoreNLP processing ring for the MP Stephen Kinnock:esults
exemplary in the follow

```
Stephen Kinnock:
	'Stephen Nathan Kinnock (born 1 January 1970) is a British Labour Party politician who has been the Member of Parliament (MP) for Aberavon since the 2015 general election'
		 ('is', 'Kinnock', 'British')
	'His wife is the former Danish Prime Minister Helle Thorning-Schmidt'
		 ('is', 'His wife', 'former Danish Prime Minister Helle Thorning-Schmidt')
		 ('is', 'His wife', 'former Prime Minister Helle Thorning-Schmidt')
	'His father, Neil Kinnock, is a former Leader of the British Labour Party and was a European Commissioner and Vice President of the European Commission'
		 ('was European Commissioner of', 'His father', 'Commission')
		 ('was Commissioner of', 'His father', 'European Commission')
		 ('father', 'His', 'Neil Kinnock')
		 ('was', 'His father', 'Commissioner')
		 ('is', 'His father', 'former Leader')
		 ('was Commissioner of', 'His father', 'Commission')
		 ('was', 'father', 'European')
		 ('is former Leader of', 'His father', 'Labour Party')
		 ('is former Leader of', 'His father', 'British Labour Party')
		 ('was', 'His father', 'European Commissioner')
		 ('was European Commissioner of', 'His father', 'European Commission')
	'His mother is a former Labour Party MEP.'
		 ('is', 'His mother', 'former Labour Party MEP')
    ...
```

As the dataset of the 650 Wikipedia articles is quite large, I began
with a reduced dataset in **Round 1**, which was limited to the first
paragraph of each article. In Round 2 instead, I used the first two
paragraphs of each article, but to visualize the data appropriately, the
visualization got reduced to only display triples, that contain the
politicians name. I used the networkx library in Python for the
visualization.

### Round 1

Looking at all triples over all 650 Wikipedia articles of the members of
UK House of Commons, which are detected by OpenIE, the following
distribution of predicates can be seen:

![Fig 01](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/predicates_pie_chart.png)

At this point it is noticeable that already in this reduced selection of
predicates several ones contain the word "member" or "mp", which stands
for *Member of Parliament* . A short investigation showed, that there
are 52 different predicates related to membership and in total these
predicates, which are shown below, make 17% (588 out of 3309) of all
found triples.

```
[
	'been member for'
	'been member of'
	'been member since'
	'been mp for'
	'been mp in'
	'been mp since'
	'best mp on'
	'for member is'
	'in member is'
	'is also member of'
	'is conservative member for'
	'is conservative member of'
	'is current member for'
	'is current member of'
	'is currently female mp in'
	'is currently member for'
	'is currently member of'
	'is currently mp in'
	'is female mp in'
	'is former member for'
	'is former member of'
	'is incumbent member for'
	'is incumbent member of'
	'is member for'
	'is member in'
	'is member of'
	'is member within'
	'is mp in'
	'is now member of'
	'locally is also member of'
	'locally is member of'
	'member at'
	'member for'
	'member of'
	'mp for'
	'mp in'
	'mp on'
	'mp since'
	'of member is'
	'previously been member for'
	'previously been member of'
	'previously was mp for'
	'since member is'
	'was formerly member for'
	'was formerly member of'
	'was member for'
	'was member of'
	'was mp for'
	'was mp in'
	'was previously member for'
	'was previously member of'
	'was youngest mp in'
]

```

To visualize the extracted triples I used the networkx library for
visualization. Initially, I limited the analysis to the first paragraph
of each Wikipedia article. These are some results:

![Fig 2](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_bernard_jenkin_round_1.png)

![Fig 3](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_margaret_beckett_round_1.png)

![Fig 4](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_mike_penning_round_1.png)


### Round 2

Within the second round every Wikipedia article was fully processed by
OpenIE. As mentioned above, to provide a understandable visualization,
the dataset had to be reduced. This was done by selecting only the
nodes, that are somehow connected to the main node, which is the name of
the politician. 

These are the graphs of the Wikipedia articles shown in Round 1, but
processed in this manner:

![Fig 5](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_bernard_jenkin_round_2.png)

![Fig 6](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_margaret_beckett_round_2.png)

![Fig 7](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_mike_penning_round_2.png)


Additionally, these figures provide interesting insights:

![Fig 8](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_kate_osamor_round_2.png)

![Fig 9](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_dawn_butler_round_2.png)



Also some graphs became very large ... 

![Fig 10](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_boris_johnson_round_2.png)

... and others contain wrong or misleading information (not she but her
mother died 1992) ...

![Fig 11](https://github.com/philipptrenz/Text-Visualisation-in-Practice/raw/master/07_knowledge_graphs/img/graph_colleen_fletcher_round_2.png)
