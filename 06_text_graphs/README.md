# Text graph, co-occurrance, fasttext and more

> **Date:** 18.05. *(Due: 21.05.)*  
> **Name:** `PhTr` Philipp Trenz  
> **Code:**
> [git](https://github.com/philipptrenz/Text-Visualisation-in-Practice/tree/master/06_text_graphs)  
> **Session:** [Text Graphs](../index)

----

## Intro

In this week's blog post, the dataset of the Wikipedia articles of all
members of the Bundestag is analyzed and visualized using a
[text graph](https://en.wikipedia.org/wiki/Text_graph).

## Approach

To generate the text graph already known metrics are used: The nodes of
the graph represent the words across all documents. 

To select relevant words, co-occurrance at the document level of each
word is considered. A threshold of 40 limits the number of nodes (so a
word must appear in at least 40 documents to be represented in the
graph) and determines the size of the node.

The selection and weighting of the edges is based on a trained fast text
model to represent both statistical and semantic similarity. For this,
the cosine similarity of the token vectors between every two nodes is
calculated and the 1000 most similar pairs are added as edges to the
graph. 

## Results

The following pictures show parts of the graph, which was rendered with
D3.js.

![](img/03.png)



![](img/05.png)



![](img/06.png)



![](img/07.png)


## Findings
